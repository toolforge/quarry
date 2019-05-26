"""
Simple CLI to help to administrate Quarry.

Use the following command in appropriate virtualenv in the directory where this file lives:

    FLASK_APP=cli.py flask quarry
"""
import click
from sqlalchemy import func
from sqlalchemy.orm.exc import NoResultFound
from functools import wraps

from .app import app, g, setup_context, kill_context
from .models.user import User, UserGroup
from .models.query import Query
from .models.queryrevision import QueryRevision
from .models.queryrun import QueryRun


def with_quarry_appcontext(f):
    @wraps(f)
    def wrapper(*args, **kwds):
        setup_context()
        value = f(*args, **kwds)
        kill_context()
        return value
    return wrapper


@app.cli.group()
def quarry():
    """
    Umbrella command group for Quarry maintenance.

    It is direcly mapped to "quarry" command on Quarry web server shell.
    """
    pass


@quarry.group()
def user():
    """Group of subcommands related to users."""
    pass


@user.command()
@click.argument('usernames', nargs=-1, required=True)
@with_quarry_appcontext
def block(usernames):
    """Block users from running new queries."""
    if not click.confirm('Do you really want to block these %s user(s) ("%s")?'
                         % (len(usernames), '", "'.join(usernames))):
        click.echo('Cancelled.')
        return

    for username in usernames:
        try:
            user = g.conn.session.query(User).filter(User.username == username).one()
        except NoResultFound:
            click.secho('- No user "%s" found, skip'
                        % username, fg='red')
            continue

        if g.conn.session.query(UserGroup).filter(UserGroup.user_id == user.id).first():
            click.secho('- User "%s" is already blocked or as special rights, skip'
                        % user.username, fg='red')
            continue

        block = UserGroup(user_id=user.id, group_id=UserGroup.GROUP_BLOCKED)
        g.conn.session.add(block)
        g.conn.session.commit()
        click.secho('- User "%s" blocked'
                    % user.username, fg='green')

    click.echo('Done.')


@user.command()
@click.argument('username')
@with_quarry_appcontext
def stats(username):
    """Compute some stats about a specified user."""
    setup_context()
    try:
        user = g.conn.session.query(User).filter(User.username == username).one()
    except NoResultFound:
        click.secho('No user "%s" found.'
                    % username, fg='red')
        return

    queries = g.conn.session.query(func.count(Query.id)) \
        .filter(Query.user_id == user.id) \
        .scalar()

    revisions = g.conn.session.query(func.count(QueryRevision.id)) \
        .join(Query, Query.id == QueryRevision.query_id) \
        .filter(Query.user_id == user.id) \
        .scalar()

    runs = g.conn.session.query(func.count(QueryRun.id)) \
        .join(QueryRevision, QueryRevision.id == QueryRun.query_rev_id) \
        .join(Query, Query.id == QueryRevision.query_id) \
        .filter(Query.user_id == user.id) \
        .scalar()

    click.echo('Statistics about user "%s":' % user.username)
    click.echo('- queries: %s' % queries)
    click.echo('- revisions: %s' % revisions)
    click.echo('- runs: %s' % runs)
