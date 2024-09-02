import pymysql
import socks


class ReplicaConnectionException(Exception):
    pass


class Replica:
    def __init__(self, config):
        self.config = config
        self.dbname = ""

    def _db_name_mangler(self):
        self.is_tools_db = False
        self.is_quarry_p = False
        if self.dbname == "":
            raise ReplicaConnectionException(
                "Attempting connection before a database is selected"
            )
        if "__" in self.dbname and self.dbname.endswith("_p"):
            self.is_tools_db = True
            self.database_p = self.dbname
        elif self.dbname == "quarry" or self.dbname == "quarry_p":
            self.is_quarry_p = True
            self.database_p = "quarry_p"
        elif self.dbname == "meta" or self.dbname == "meta_p":
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

    def get_host_name(self):
        if self.is_tools_db:
            return self.config["TOOLS_DB_HOST"]
        if self.is_quarry_p:
            return self.config["DB_HOST"]
        if self.config["REPLICA_DOMAIN"]:
            return f"{self.database_name}.{self.config['REPLICA_DOMAIN']}"
        return self.database_name

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
        host = self.get_host_name()
        if self.is_tools_db:
            conf_prefix = "TOOLS_DB"
        elif self.is_quarry_p:
            conf_prefix = "QUARRY_P"
        else:
            conf_prefix = "REPLICA"
        port = self.config[f"{conf_prefix}_PORT"]
        connect_opts = {
            "db": self.database_p,
            "user": self.config[f"{conf_prefix}_USER"],
            "passwd": self.config[f"{conf_prefix}_PASSWORD"],
            "charset": "utf8",
            "client_flag": pymysql.constants.CLIENT.MULTI_STATEMENTS,
        }

        if not self.config.get("REPLICA_SOCKS5_PROXY_HOST"):
            self._replica = pymysql.connect(
                host=host, port=port, **connect_opts
            )
        else:
            self._replica = pymysql.connect(defer_connect=True, **connect_opts)

            sock = socks.socksocket()
            sock.set_proxy(
                socks.SOCKS5,
                addr=self.config["REPLICA_SOCKS5_PROXY_HOST"],
                port=self.config["REPLICA_SOCKS5_PROXY_PORT"],
            )
            sock.connect((host, port))
            self._replica.connect(sock=sock)

    @connection.deleter
    def connection(self):
        self.dbname = ""
        if hasattr(self, "_replica"):
            if self._replica.open:
                self._replica.close()

            delattr(self, "_replica")
