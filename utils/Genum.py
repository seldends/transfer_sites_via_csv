import psycopg2
from utils.Database import Database
import sys


class DatabaseGenum(Database):
    def connect(self):
        """Connect to a Postgres database."""
        if self.conn is None:
            db_pg_list = ['pg_local']
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
            SELECT "id", "Type_id", "Title", "Article", "CreationDate", "ModificationDate", "AdoptionDate", "Number"
            FROM "sd4_LegalAct"
            WHERE "IsHidden"=False
            AND "Type_id" IN %s
            ORDER BY id DESC
            ;
            '''
        npa_list = self.select_rows(select_npa_local, tuple(params))
        return npa_list

    # Функция для получения новостей
    def get_news_list(self, params):
        select_news_local = '''
                SELECT "id", "Group_id", "Title", "Article", "Summary", "CreationDate", "PublicationDate", "Image"
                FROM public."sd4_PublicationItem"
                WHERE "IsHidden"=False
                AND "CreationDate" > '2018-01-01 00:00:00'
                AND "Group_id" IN %s
                -- AND id > 28585
                ORDER BY id DESC
                -- LIMIT 1
                '''
        news_list = self.select_rows(select_news_local, tuple(params))
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

    def npa_info(self):
        query = """
            SELECT "sd4_LegalActType".id, "sd4_LegalActType"."Title", COUNT("sd4_LegalAct".id)
            FROM "sd4_LegalAct"
            LEFT JOIN "sd4_LegalActType"
            ON "sd4_LegalAct"."Type_id" = "sd4_LegalActType".id
            WHERE "sd4_LegalAct"."IsHidden"=False
            GROUP BY "sd4_LegalActType".id, "sd4_LegalActType"."Title"
            ORDER BY "sd4_LegalActType".id;
        """
        info = self.select_rows(query)
        for obj in info:
            print(f'тип {obj[0]} {obj[1]} количество {obj[2]}')

    def news_info(self):
        query = """
            SELECT "sd4_PublicationGroup".id, "sd4_PublicationGroup"."Title", COUNT("sd4_PublicationItem".id) 
            FROM "sd4_PublicationItem"
            LEFT JOIN "sd4_PublicationGroup"
            ON "sd4_PublicationItem"."Group_id" = "sd4_PublicationGroup".id
            WHERE "sd4_PublicationItem"."CreationDate" > '2018-01-01 00:00:00'
            AND "sd4_PublicationItem"."IsHidden"=False
            GROUP BY "sd4_PublicationGroup".id, "sd4_PublicationGroup"."Title"
            ORDER BY "sd4_PublicationGroup".id;
        """
        info = self.select_rows(query)
        for obj in info:
            print(f'тип {obj[0]} {obj[1]} количество {obj[2]}')
