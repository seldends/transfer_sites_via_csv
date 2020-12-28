import psycopg2
from utils.Database import Database
import sys


class DatabaseGenum(Database):
    def connect(self):
        """Connect to a Postgres database."""
        if self.conn is None:
            db_pg_list = ['pg_local', 'pg_test47', 'pg_test51', 'pg_mytest', 'pg_local_sitex_47']
            if self.dbtype in db_pg_list:
                try:
                    self.conn = psycopg2.connect(
                        host=self.host,
                        user=self.username,
                        password=self.password,
                        port=self.port,
                        dbname=self.dbname
                    )
                except psycopg2.DatabaseError as error:
                    print(f"Error while connecting to PostgreSQL: {error}")
                    sys.exit(1)
                finally:
                    print('PostgreSQL Connection opened successfully.')

    # Функция для получения ouid нпа
    def get_npa_files_list(self, id):
        select_npafiles_local = '''
            SELECT "File"
            FROM public."sd4_LegalActFile"
            WHERE "LegalAct_id"=%s;
            '''
        npafiles_list = self.select_rows(select_npafiles_local, id)
        return npafiles_list

    # Функция для получения нпа
    def get_npa_list(self, params):
        select_npa_local = '''
            SELECT "id", "AdoptionDate", "Title", "Article","ModificationDate", "Number", "Type_id"
            FROM "sd4_LegalAct"
            WHERE "IsHidden"=False
            AND "Type_id" IN %s
            ORDER BY id DESC
            ;
            '''
        npa_list = self.select_rows(select_npa_local, params)
        return npa_list

    # Функция для получения новостей
    def get_news_list(self, params):
        select_news_local = '''
                SELECT *
                FROM public."sd4_PublicationItem"
                WHERE "IsHidden"=False
                AND "CreationDate" > '2018-01-01 00:00:00'
                AND "Group_id" IN %s
                ORDER BY id DESC
                --LIMIT 3
                '''
        news_list = self.select_rows(select_news_local, params)
        return news_list

    # Функция для получения медиафайлов
    def get_news_files_list(self, id):
        select_newsfiles_local = '''
                SELECT "Image", "Title"
                FROM public."sd4_PublicationItemImage"
                WHERE "Item_id"=%s;
                '''
        newsfiles_list = self.select_rows(select_newsfiles_local, id)
        return newsfiles_list

    # Сохранение страниц
    def get_pages_list(self):
        select_page_local = '''
            SELECT "id","Parent_id","Title","Article", "Alias", "Path", "Level"
            FROM public."sd4_HtmlPage"
            WHERE "IsHidden"=false
            --AND "Alias"=%s
            ORDER BY id DESC;
            '''
        pages_list = self.select_rows(select_page_local)
        return pages_list

        self.connect()
        with self.conn.cursor() as cur:
            val = f'{code}%'
            conent = f'{content}'
            cur.execute(select_pages, (val, conent))
            records = cur.fetchall()
            cur.close()
            return records