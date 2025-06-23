from flask import current_app, Flask, render_template, g, Response
from flask_caching import Cache
from werkzeug.middleware.proxy_fix import ProxyFix

from .config import get_config
from .connections import Connections
from .replica import Replica
from .login import auth
from .metrics import metrics_init_app
from .redissession import RedisSessionInterface
from .user import user_blueprint, get_user
from .utils import monkey as _unused  # noqa: F401
from .health import health_blueprint
from .query import query_blueprint
from .run import run_blueprint
from .api import api_blueprint
from .webhelpers import templatehelpers
from .models.user import User
from .models.queryrun import QueryRun


def setup_context():
    g.conn = Connections(current_app.config)
    g.replica = Replica(current_app.config)


def kill_context(exception=None):
    if g.conn:
        g.conn.close_all()
    del g.replica.connection


def handle_internal_error(e: Exception):
    return render_template("500.html")


def create_app(test_config=None):
    app = Flask(__name__)
    app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1)

    if test_config is None:
        app.config.update(get_config())
    else:
        app.config.from_mapping(test_config)

    # Note: This only works when DEBUG is set to false.
    app.register_error_handler(Exception, handle_internal_error)

    app.register_blueprint(auth)
    app.register_blueprint(health_blueprint)
    app.register_blueprint(user_blueprint)
    app.register_blueprint(query_blueprint)
    app.register_blueprint(run_blueprint)
    app.register_blueprint(api_blueprint)
    app.register_blueprint(templatehelpers)

    global_conn = Connections(app.config)
    app.session_interface = RedisSessionInterface(global_conn.redis)

    app.before_request(setup_context)
    app.teardown_request(kill_context)

    metrics_init_app(app)
    cache = Cache(app)  # noqa: F841, this var is used in landing.html template

    @app.route("/")
    def index():
        return render_template(
            "landing.html",
            user=get_user(),
            stats_count_users=global_conn.session.query(User).count(),
            stats_count_runs=global_conn.session.query(QueryRun).count(),
        )

    @app.route("/robots.txt")
    def robots_txt():
        return Response("User-Agent: *\nDisallow: /\n", mimetype="text/plain")

    return app


if __name__ == "__main__":
    application = create_app()
    application.run(port=5000, host="0.0.0.0")
