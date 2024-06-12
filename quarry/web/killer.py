#!/usr/bin/env python
import os
import yaml
import logging
import pymysql
from quarry.web.replica import Replica

__dir__ = os.path.dirname(__file__)
config = yaml.safe_load(open(os.path.join(__dir__, "../default_config.yaml")))
try:
    config.update(yaml.safe_load(open(os.path.join(__dir__, "../config.yaml"))))
except IOError:
    # is ok if we do not have config.yaml
    pass

logging.basicConfig(
    filename=config["KILLER_LOG_PATH"],
    level=logging.INFO,
    format="%(asctime)s pid:%(process)d %(message)s",
)
logging.info(
    "Started killer process, with limit %s", config["QUERY_TIME_LIMIT"]
)

hosts = [db_slice + '.' + config.get['REPLICA_DOMAIN'] for db_slice in config.get['REPLICA_SLICES'].split(',')]
hosts.append(config.get['TOOLS_DB_HOST'])

for host in hosts:
    conn = Replica(config)

    cur = conn.connection.cursor()
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
        del conn.connection
