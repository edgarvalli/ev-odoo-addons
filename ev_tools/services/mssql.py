import pyodbc


class SqlServer:

    DRIVERS_PRIORIDAD = [
        "ODBC Driver 18 for SQL Server",
        "ODBC Driver 17 for SQL Server",
        "ODBC Driver 13 for SQL Server",
        "SQL Server Native Client 11.0",
        "SQL Server",
    ]

    driver = None

    def __init__(
        self,
        dbname="master",
        server="localhost",
        instance="SQLExpress",
        user="sa",
        password="",
        autocommit=False,
    ):

        self.dbname = dbname
        self.server = server
        self.instance = instance
        self.user = user
        self.password = password
        self.autocommit = autocommit

        self._create_connection()

    # =========================
    # CONNECTION
    # =========================

    def _get_connection_str(self, driver):

        return (
            f"DRIVER={{{driver}}};"
            f"SERVER={self.server}\\{self.instance};"
            f"DATABASE={self.dbname};"
            f"UID={self.user};"
            f"PWD={self.password};"
            f"TrustServerCertificate=yes;"
        )

    def _get_driver(self):

        if SqlServer.driver:
            return SqlServer.driver

        installed = pyodbc.drivers()

        for d in self.DRIVERS_PRIORIDAD:

            if d in installed:
                SqlServer.driver = d
                return d

        if installed:
            SqlServer.driver = installed[0]
            return installed[0]

        raise Exception("No SQL Server ODBC driver found")

    def _create_connection(self):

        driver = self._get_driver()

        self.connection = pyodbc.connect(
            self._get_connection_str(driver),
            autocommit=self.autocommit,
        )

        self.cursor = self.connection.cursor()

    # =========================
    # INTERNAL
    # =========================

    def _dict_fetch(self):

        cols = [c[0] for c in self.cursor.description]

        return [dict(zip(cols, row)) for row in self.cursor.fetchall()]

    def _dict_fetchone(self):

        row = self.cursor.fetchone()

        if not row:
            return None

        cols = [c[0] for c in self.cursor.description]

        return dict(zip(cols, row))

    # =========================
    # QUERY HELPERS
    # =========================

    def execute(self, query, args=()):

        self.cursor.execute(query, args)

        return self.cursor.rowcount

    def fetchall(self, query, args=()):

        self.cursor.execute(query, args)

        return self._dict_fetch()

    def fetchone(self, query, args=()):

        self.cursor.execute(query, args)

        return self._dict_fetchone()

    def insert(self, query, args=()):

        self.cursor.execute(query, args)

        return self._dict_fetchone()

    # =========================
    # TRANSACTIONS
    # =========================

    def commit(self):

        self.connection.commit()

    def rollback(self):

        self.connection.rollback()

    # =========================
    # HELPERS
    # =========================

    @property
    def connected(self):

        try:
            self.cursor.execute("SELECT 1")
            return True

        except Exception:
            return False

    def close(self):

        if getattr(self, "cursor", None):
            self.cursor.close()

        if getattr(self, "connection", None):
            self.connection.close()

    # =========================
    # CONTEXT MANAGER
    # =========================

    def __enter__(self):

        return self

    def __exit__(self, exc_type, exc, tb):

        try:

            if exc:
                self.rollback()
            else:
                self.commit()

        finally:

            self.close()
