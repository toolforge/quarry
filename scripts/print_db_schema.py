#!/usr/bin/env python3
import os
import sys
from sqlalchemy import create_engine
from importlib import import_module
import pkgutil


if __name__ == "__main__":
    sys.path.append(os.path.join(os.path.dirname(__file__), ".."))
    from quarry.web import models
    # We might want to move to flask-sqlalchemy, as it provides create_all
    # this is required to actually force the import of the modules
    for importer, modname, ispkg in pkgutil.walk_packages(path=models.__path__):
        if modname != 'base':
            import_module("quarry.web.models." + modname)

    def metadata_dump(sql, *multiparams, **params):
        sql_str = str(sql.compile(dialect=engine.dialect)) + ";"
        print(
            sql_str.replace(
                "CREATE INDEX", "CREATE INDEX IF NOT EXISTS"
            ).replace("CREATE TABLE", "CREATE TABLE IF NOT EXISTS")
        )

    print(
        "DROP DATABASE quarry;\n"
        "CREATE DATABASE IF NOT EXISTS quarry CHARACTER SET utf8;\n"
        "USE quarry;"
    )
    # fake db, just so it generates the sql correctly
    db_uri = "mysql+pymysql://someuser@somehost/somedb?charset=utf8"
    engine = create_engine(db_uri, strategy='mock', executor=metadata_dump)
    from quarry.web.models.base import Base
    Base.metadata.create_all(bind=engine)
