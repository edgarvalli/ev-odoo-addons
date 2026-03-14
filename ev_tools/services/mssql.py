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
    ):

        self.dbname = dbname
        self.server = server
        self.instance = instance
        self.user = user
        self.password = password

        self._create_connection()

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

        self.connection = pyodbc.connect(self._get_connection_str(driver))
        self.cursor = self.connection.cursor()

    # =========================
    # SQL HELPERS
    # =========================

    def execute(self, query, args=()):
        """
        Ejecuta una query sin retorno (INSERT / UPDATE / DELETE)
        """
        self.cursor.execute(query, args)

    def fetchall(self, query, args=()):
        """
        Ejecuta un SELECT y devuelve todos los registros
        """
        self.cursor.execute(query, args)

        cols = [c[0] for c in self.cursor.description]

        return [dict(zip(cols, row)) for row in self.cursor.fetchall()]

    def fetchone(self, query, args=()):
        """
        Ejecuta un SELECT y devuelve un registro
        """
        self.cursor.execute(query, args)

        row = self.cursor.fetchone()

        if not row:
            return None

        cols = [c[0] for c in self.cursor.description]

        return dict(zip(cols, row))

    def commit(self):
        """
        Confirma la transacción
        """
        self.connection.commit()

    def rollback(self):
        """
        Revierte la transacción
        """
        self.connection.rollback()

    # =========================
    # HELPERS
    # =========================

    def close(self):

        if getattr(self, "cursor", None):
            self.cursor.close()

        if getattr(self, "connection", None):
            self.connection.close()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):

        if exc:
            self.connection.rollback()

        self.close()
