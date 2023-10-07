import pymysql
import socks


class ReplicaConnectionException(Exception):
    pass


class Replica:
    def __init__(self, config):
        self.config = config
        self.dbname = ""

    def _db_name_mangler(self):
        if self.dbname == "":
            raise ReplicaConnectionException(
                "Attempting connection before a database is selected"
            )

        if self.dbname == "meta" or self.dbname == "meta_p":
            self.database_name = "s7"

            self.database_p = "meta_p"
        elif self.dbname == "centralauth" or self.dbname == "centralauth_p":
            self.database_name = "s7"
            self.database_p = "centralauth_p"
        else:
            self.database_name = (
                self.dbname
                if not self.dbname.endswith("_p")
                else self.dbname[:-2]
            )
            self.database_p = (
                self.dbname
                if self.dbname.endswith("_p")
                else "{}_p".format(self.dbname)
            )

    @property
    def connection(self):
        self._replica.ping(reconnect=True)
        return self._replica

    @connection.setter
    def connection(self, db):
        if db == self.dbname and hasattr(self, "_replica"):
            return self._replica.ping(reconnect=True)  # Reuse connections

        if hasattr(self, "_replica"):
            if self._replica.open:
                self._replica.close()

        self.dbname = db
        self._db_name_mangler()
        repl_host = (
            f"{self.database_name}.{self.config['REPLICA_DOMAIN']}"
            if self.config["REPLICA_DOMAIN"]
            else self.database_name
        )
        connect_opts = {
            "db": self.database_p,
            "user": self.config["REPLICA_USER"],
            "passwd": self.config["REPLICA_PASSWORD"],
            "charset": "utf8",
            "client_flag": pymysql.constants.CLIENT.MULTI_STATEMENTS,
        }

        if not self.config.get("REPLICA_SOCKS5_PROXY_HOST"):
            self._replica = pymysql.connect(
                host=repl_host, port=self.config["REPLICA_PORT"], **connect_opts
            )
        else:
            self._replica = pymysql.connect(defer_connect=True, **connect_opts)

            sock = socks.socksocket()
            sock.set_proxy(
                socks.SOCKS5,
                addr=self.config["REPLICA_SOCKS5_PROXY_HOST"],
                port=self.config["REPLICA_SOCKS5_PROXY_PORT"],
            )
            sock.connect((repl_host, self.config["REPLICA_PORT"]))
            self._replica.connect(sock=sock)

    @connection.deleter
    def connection(self):
        self.dbname = ""
        if hasattr(self, "_replica"):
            if self._replica.open:
                self._replica.close()

            delattr(self, "_replica")
