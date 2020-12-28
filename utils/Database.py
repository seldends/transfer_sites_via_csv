import sys
import yaml

# from sshtunnel import SSHTunnelForwarder
# TODO Переделать свою реализация на примерах
# TODO https://hackersandslackers.com/psycopg2-postgres-python/
# TODO https://stackoverflow.com/questions/22046708/psycopg2-access-postgresql-database-on-remote-host-without-manually-opening-ssh
# TODO https://stackoverflow.com/questions/37488175/simplify-database-psycopg2-usage-by-creating-a-module
# TODO https://pynative.com/python-postgresql-tutorial/
# TODO http://zetcode.com/python/psycopg2/


class Database:
    def __init__(self, db_type, db_name=None):
        self.dbtype = db_type
        try:
            with open("configs/db.yml", "r") as ymlfile:
                config = yaml.safe_load(ymlfile)
                try:
                    self.host = config[db_type]["host"]
                    self.port = config[db_type]["port"]
                    self.username = config[db_type]["user"]
                    self.password = config[db_type]["password"]
                    if db_name:
                        self.dbname = db_name
                    else:
                        self.dbname = config[db_type]["db_name"]
                except KeyError as error:
                    print(f'В конфигурации {db_type} отсутствует атрибут: {error}')
                    sys.exit(1)
        except FileNotFoundError as error:
            print(f'Отсутствует файл конфигурации configs/db.yml: {error}')
            sys.exit(1)
        self.conn = None

    def select_rows(self, query, *val):
        """Run a SQL query to select rows from table."""
        self.connect()
        with self.conn.cursor() as cur:
            if val:
                cur.execute(query, val)
            else:
                cur.execute(query)
            records = cur.fetchall()
            cur.close()
            return records

    def query_put(self, sql, val):
        self.connect()
        with self.conn.cursor() as cur:
            cur.execute(sql, val)

    # TODO Сделать функцию для коммита
    # Применение изменений
    def db_commit(self):
        self.conn.commit()
        with self.conn.cursor() as cur:
            cur.close()
        print("Изменения сохранены. Закрытие соединения")