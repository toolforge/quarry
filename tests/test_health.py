import json

from tests.db_mock import session_mock

from quarry.web.models.query import Query
from quarry.web.models.queryrun import QueryRun
from quarry.web.models.queryrevision import QueryRevision


def test_health(mocker, client):
    minutes = 5
    session = session_mock(
        [
            Query(),
            Query(),
            Query(),
            QueryRevision(),
            QueryRevision(),
            QueryRun(status=4),
            QueryRun(status=4),
            QueryRun(status=1),
        ]
    )

    with mocker.patch(
        "quarry.web.connections.Connections.session",
        new_callable=mocker.PropertyMock(return_value=session),
    ):
        rval = client.get("/.health/summary/v1/%d" % minutes)
        result_dict = json.loads(rval.data.decode("utf8"))

        filter_keys = [
            call.args[0].left.key for call in session.filter.call_args_list
        ]
        assert filter_keys == ["last_touched", "timestamp", "timestamp"]

        print(result_dict)
        assert result_dict["queries_num"] == 3
        assert result_dict["query_revs_num"] == 2
        assert result_dict["query_run_statuses"]["complete"] == 2
        assert result_dict["query_run_statuses"]["failed"] == 1
        assert result_dict["query_run_statuses"]["superseded"] == 0
