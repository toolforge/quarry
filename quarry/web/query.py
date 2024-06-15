import json

from flask import (
    Blueprint,
    current_app,
    g,
    render_template,
    Response,
    redirect,
    request,
    url_for,
    session,
)
from sqlalchemy import desc, func
from sqlalchemy.orm.exc import NoResultFound

from .models.query import Query
from .models.queryrevision import QueryRevision
from .models.queryrun import QueryRun
from .models.star import Star
from .user import get_user, get_preferences
from .utils import json_formatter
from .utils.pagination import RangeBasedPagination

query_blueprint = Blueprint("query", __name__)


@query_blueprint.route("/query/new")
def new_query():
    if get_user() is None:
        return redirect("/login?next=/query/new")
    query = Query()
    query.user = get_user()
    g.conn.session.add(query)
    g.conn.session.commit()
    return redirect(url_for("query.query_show", query_id=query.id))


@query_blueprint.route("/history/<int:query_id>")
def query_history(query_id):
    query = g.conn.session.query(Query).filter(Query.id == query_id).one()

    return render_template(
        "query/history.html",
        user=get_user(),
        queries=sorted(query.revs, key=lambda q: q.timestamp, reverse=True),
    )


@query_blueprint.route(
    "/history/<int:query_id>/<int:rev_id>/<int:latest_run_id>"
)
@query_blueprint.route("/query/<int:query_id>")
def query_show(query_id, rev_id=None, latest_run_id=None):
    this_rev_text = None
    try:
        query = g.conn.session.query(Query).filter(Query.id == query_id).one()
    except NoResultFound:
        return Response("No such query id " + str(query_id), status=404)
    can_edit = get_user() is not None and get_user().id == query.user_id
    is_starred = False
    if get_user():
        is_starred = (
            g.conn.session.query(func.count(Star.id))
            .filter(Star.user_id == get_user().id)
            .filter(Star.query_id == query_id)
            .scalar()
            == 1
        )
    jsvars = {
        "query_id": query.id,
        "can_edit": can_edit,
        "is_starred": is_starred,
        "published": query.published,
        "preferences": get_preferences(),
    }

    if rev_id:
        jsvars["qrun_id"] = latest_run_id
        for row in query.revs:
            if row.id == rev_id:
                this_rev_text = row.text
                break
    elif query.latest_rev and query.latest_rev.latest_run_id:
        jsvars["qrun_id"] = query.latest_rev.latest_run_id

    return render_template(
        "query/view.html",
        user=get_user(),
        query=query,
        jsvars=jsvars,
        latest_rev=query.latest_rev,
        this_rev_text=this_rev_text,
        rev_id=rev_id,
    )


@query_blueprint.route(
    "/query/<int:query_id>/result/latest/<string:resultset_id>/<string:format>"
)
def query_output_redirect(query_id, resultset_id, format):
    query = g.conn.session.query(Query).filter(Query.id == query_id).one()
    qrun_id = query.latest_rev.latest_run_id
    # FIXME: Enforce HTTPS everywhere in a nicer way!
    resp = redirect(
        url_for(
            "run.output_result",
            qrun_id=qrun_id,
            resultset_id=resultset_id,
            format=format,
            _external=True,
            _scheme="https",
        )
    )
    # CORS on the redirect
    resp.headers.add("Access-Control-Allow-Origin", "*")
    return resp


@query_blueprint.route("/query/runs/all")
def query_runs_all():
    queries = (
        g.conn.session.query(Query)
        .join(Query.latest_rev)
        .join(QueryRevision.latest_run)
    )
    queries_filter = "all"
    if request.args.get("published") == "true":
        queries = queries.filter(Query.published)
        queries_filter = "published"
        session["recent_queries_link"] = url_for(
            "query.query_runs_all", published="true"
        )
    else:
        session["recent_queries_link"] = url_for("query.query_runs_all")
    # Handle search parameters
    args = request.args
    search_term = args.get("search_term")
    search_parameter = ""
    if search_term is not None:
        search_parameter = f"search_term={search_term}"
        queries = queries.filter(
            Query.title.ilike(f"%{search_term}%")
            | Query.description.ilike(f"%{search_term}%")
        )
    limit = int(
        request.args.get(
            "limit", current_app.config.get("QUERY_RESULTS_PER_PAGE", 50)
        )
    )
    queries, prev_link, next_link = QueriesRangeBasedPagination(
        queries,
        request.args.get("from"),
        limit,
        request.path,
        request.referrer,
        dict(request.args),
    ).paginate()
    return render_template(
        "query/list.html",
        user=get_user(),
        queries=queries,
        prev_link=prev_link,
        next_link=next_link,
        search_parameter=search_parameter,
        search_term=search_term,
        queries_filter=queries_filter,
    )


@query_blueprint.route("/query/<int:query_id>/meta")
def output_query_meta(query_id):
    query = g.conn.session.query(Query).get(query_id)
    if not query:
        return Response("No such query id", status=404)
    return Response(
        json.dumps(
            {
                "latest_run": query.latest_rev.latest_run,
                "latest_rev": query.latest_rev,
                "query": query,
            },
            default=json_formatter,
        ),
        mimetype="application/json",
        headers={"Access-Control-Allow-Origin": "*"},
    )


@query_blueprint.route("/explain/<string:db_name>/<int:connection_id>")
def output_explain(db_name, connection_id):
    g.replica.connection = db_name
    cur = g.replica.connection.cursor()
    try:
        cur.execute("SHOW EXPLAIN FOR %d;" % connection_id)
    except cur.InternalError as e:
        if e.args[0] in [1094, 1915, 1933]:
            # 1094 = Unknown thread id
            # 1915, 1933 = Target is not running an EXPLAINable command
            return Response(
                json.dumps(
                    {
                        "headers": ["Error"],
                        "rows": [["Hmm... Is the SQL actually running?!"]],
                    },
                    default=json_formatter,
                ),
                mimetype="application/json",
            )
        else:
            raise
    else:
        return Response(
            json.dumps(
                {
                    "headers": [c[0] for c in cur.description],
                    "rows": cur.fetchall(),
                },
                default=json_formatter,
            ),
            mimetype="application/json",
        )


@query_blueprint.route("/fork/<int:id>/<int:rev_id>")
@query_blueprint.route("/fork/<int:id>")
def fork_query(id, rev_id=None):
    if get_user() is None:
        return redirect("/login?next=fork/{id}".format(id=id))
    query = Query()
    query.user = get_user()
    parent_query = g.conn.session.query(Query).filter(Query.id == id).one()
    query.title = parent_query.title
    query.parent_id = parent_query.id
    query.description = parent_query.description
    g.conn.session.add(query)
    g.conn.session.commit()

    if rev_id:
        for row in parent_query.revs:
            if row.id == rev_id:
                text = row.text
                break
    else:
        text = parent_query.latest_rev.text

    query_rev = QueryRevision(
        query_id=query.id,
        query_database=parent_query.latest_rev.query_database,
        text=text,
    )
    query.latest_rev = query_rev
    g.conn.session.add(query)
    g.conn.session.add(query_rev)
    g.conn.session.commit()
    return redirect(url_for("query.query_show", query_id=query.id))


@query_blueprint.route("/rev/<int:rev_id>/meta")
def output_rev_meta(rev_id):
    rev = g.conn.session.query(QueryRevision).get(rev_id)
    if not rev:
        return Response("No such query revision id", status=404)
    return Response(
        json.dumps(
            {"latest_run": rev.latest_run, "rev": rev, "query": rev.query},
            default=json_formatter,
        ),
        mimetype="application/json",
        headers={"Access-Control-Allow-Origin": "*"},
    )


class QueriesRangeBasedPagination(RangeBasedPagination):
    def get_page_link(self, page_key, limit):
        get_params = dict(request.args)
        get_params.update({"from": page_key, "limit": limit})
        return url_for(
            "query.query_runs_all",
            **dict([(key, value) for key, value in list(get_params.items())]),
        )

    def order_queryset(self):
        if self.direction == "next":
            self.queryset = self.queryset.order_by(desc(QueryRun.timestamp))
        else:
            self.queryset = self.queryset.order_by(QueryRun.timestamp)

    def filter_queryset(self):
        if self.page_key is None:
            return
        from_query = g.conn.session.query(Query).get(self.page_key)
        if from_query:
            from_qrun_id = from_query.latest_rev.latest_run.id
            if self.direction == "prev":
                self.queryset = self.queryset.filter(QueryRun.id > from_qrun_id)
            else:
                self.queryset = self.queryset.filter(QueryRun.id < from_qrun_id)
