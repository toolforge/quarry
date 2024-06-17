#!/usr/bin/env python
import logging
import pymysql

from quarry.web.config import get_config
from connections import Connections

config = get_config()

logging.basicConfig(
    filename=config["KILLER_LOG_PATH"],
    level=logging.INFO,
    format="%(asctime)s pid:%(process)d %(message)s",
)
logging.info(
    "Started killer process, with limit %s", config["QUERY_TIME_LIMIT"]
)
conn = Connections(config)

cur = conn.replica.cursor()
try:
    cur.execute("SHOW PROCESSLIST")
    queries = cur.fetchall()
    logging.info("Found %s queries running", len(queries))
    to_kill = [
        q
        for q in queries
        if q[5] > config["QUERY_TIME_LIMIT"] and q[4] != "Sleep"
    ]
    logging.info("Found %s queries to kill", len(to_kill))
    for q in to_kill:
        try:
            cur.execute("KILL QUERY %s", q[0])
            logging.info("Killed query with thread_id:%s" % q[0])
        except pymysql.InternalError as e:
            if e.args[0] == 1094:  # Error code for 'no such thread'
                logging.info(
                    "Query with thread_id:%s dead before it could be killed"
                )
            else:
                raise
finally:
    logging.info("Finished killer process")
    cur.close()
    conn.close_all()
