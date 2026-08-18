"""Small in-memory SQLAlchemy session fake used by the unit tests."""

import operator
from unittest.mock import MagicMock

from sqlalchemy.orm.exc import MultipleResultsFound, NoResultFound


def _entity_model(entity):
    if isinstance(entity, type):
        return entity
    return getattr(entity, "class_", None)


def _value(expression):
    return getattr(expression, "value", expression)


def _matches(item, criterion):
    """Evaluate the simple SQLAlchemy predicates used in the tests."""
    left = getattr(criterion, "left", None)
    right = getattr(criterion, "right", None)
    operation = getattr(criterion, "operator", None)
    key = getattr(left, "key", None)

    if key is None:
        # ``filter(Query.published)`` is represented by the column itself.
        key = getattr(criterion, "key", None)
        return bool(getattr(item, key, False)) if key else True

    actual = getattr(item, key, None)
    expected = _value(right)
    if operation is operator.eq:
        return str(actual) == str(expected)
    if operation is operator.ne:
        return str(actual) != str(expected)
    # Time comparisons are irrelevant to static fixture data.
    return True


def session_mock(items=()):
    session = MagicMock(name="session")
    session._items = list(items)

    def add(item):
        if item not in session._items:
            session._items.append(item)

    def delete(item):
        if item in session._items:
            session._items.remove(item)

    def query(*entities):
        model = entities[0] if entities else None
        model_type = _entity_model(model)
        rows = [
            item
            for item in session._items
            if isinstance(model_type, type) and isinstance(item, model_type)
        ]
        if model_type is not model:
            key = getattr(model, "key", None)
            rows = [(getattr(item, key),) for item in rows]
        result = MagicMock(name="query_result")
        result._rows = rows

        def get(primary_key):
            session.get(primary_key)
            return next(
                (row for row in result._rows if str(getattr(row, "id", None)) == str(primary_key)),
                None,
            )

        result.get.side_effect = get
        def filter_(*criteria):
            session.filter(*criteria)
            result._rows = [
                row
                for row in result._rows
                if all(_matches(row, criterion) for criterion in criteria)
            ]
            return result

        result.filter.side_effect = filter_
        result.filter_by.side_effect = lambda **values: result
        result.all.side_effect = lambda: list(result._rows)
        result.first.side_effect = lambda: result._rows[0] if result._rows else None
        result.one_or_none.side_effect = result.first.side_effect
        def one():
            if not result._rows:
                raise NoResultFound()
            return result._rows[0]

        result.one.side_effect = one

        result.count.side_effect = lambda: len(result._rows)
        result.scalar.side_effect = lambda: len(result._rows)
        result.__iter__.side_effect = lambda: iter(result._rows)
        for method in (result.order_by, result.join, result.outerjoin, result.offset):
            method.side_effect = lambda *args, _result=result, **kwargs: _result
        result.limit.side_effect = lambda value: result
        return result

    session.add.side_effect = add
    session.delete.side_effect = delete
    session.query.side_effect = query
    return session
