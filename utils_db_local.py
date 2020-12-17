import psycopg2
import mariadb
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
            elif self.dbtype == 'mariadb':
                try:
                    self.conn = mariadb.connect(
                        host=self.host,
                        user=self.username,
                        password=self.password,
                        port=self.port,
                        database=self.dbname
                    )
                except mariadb.Error as error:
                    print(f"Error while connecting to MariaDB: {error}")
                    sys.exit(1)
                finally:
                    print('MariaDB Connection opened successfully.')

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

    # Функция для получения ouid новостей с sitex
    def get_news_ouid_list(self, title):
        sql_select_news_ouid = '''
            SELECT ouid
            FROM public.cms_article
            WHERE a_title=%s;
            '''
        data = self.select_rows(sql_select_news_ouid, title)
        ouid_list = [ouid[0] for ouid in data]
        return ouid_list

    # Функция для получения ouid нпа с sitex
    def get_npa_ouid_list(self, title):
        sql_select_npa_ouid = '''
            SELECT ouid
            FROM public.norm_act
            WHERE a_title=%s;
            '''
        data = self.select_rows(sql_select_npa_ouid, title)
        ouid_list = [ouid[0] for ouid in data]
        return ouid_list

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

        # Обновление Новостей
    def update_static_list(self, page_list):
        update_static = '''
            UPDATE public.cms_po_static
            SET a_content = %s
            WHERE ouid = %s;
            '''
        for page in page_list:
            if page.new_content:
                print(page.get_static())
                self.query_put(update_static, page.get_static())                              # Обновления данных в таблице новостей СУС

        # Сохранение страниц
    def sitex_get_pages(self, code, content):
        select_pages = '''
            SELECT cms_sitepage.ouid as page_ouid,
            cms_sitepage.a_parent as parent_ouid,
            cms_po_static.ouid as static_ouid,
            cms_sitepage.a_code as code,
            cms_sitepage.a_name as name,
            cms_po_static.a_content as content
            --FROM public.cms_po_static
            --LEFT JOIN public.sxlink ON cms_po_static.ouid = sxlink.attrb
            --LEFT JOIN public.cms_sitepage ON sxlink.attra = cms_sitepage.ouid
            FROM public.cms_sitepage
            LEFT JOIN public.sxlink ON cms_sitepage.ouid = sxlink.attra
            LEFT JOIN public.cms_po_static ON sxlink.attrb = cms_po_static.ouid
            WHERE cms_sitepage.a_code LIKE %s ESCAPE '='
            AND cms_po_static.a_content LIKE %s ESCAPE '=';
            '''

        self.connect()
        with self.conn.cursor() as cur:
            val = f'{code}%'
            conent = f'{content}'
            cur.execute(select_pages, (val, conent))
            records = cur.fetchall()
            cur.close()
            return records

    # Обновление НПА
    def update_npa_list(self, npa_list):
        update_npa = '''
            UPDATE public.norm_act
            SET a_publ_date = %s, a_title = %s, a_text = %s, a_date = %s, a_number = %s, a_structure = %s
            WHERE ouid = %s;
            '''
        for npa in npa_list:
            self.query_put(update_npa, npa.get_data())                              # Обновления данных в таблице новостей СУС
            # print(npa.a_ouid)

    # Запись файлов НПА
    def insert_npa_files(self, npafiles_list):
        insert_npa_file = '''
            INSERT INTO public.norm_act_filelink (a_toid, a_name, a_type, a_fromid)
            VALUES (%s, %s, %s, %s);
            '''
        for npafile in npafiles_list:
            self.query_put(insert_npa_file, npafile.get_data())               # Запись данных в таблицу медиафайлов СУС
            # print(npafile.a_fromid)

    # Запись файлов НПА
    def create_npa_tables(self, params):
        sql_npa_tables = '''
            --DROP TABLE IF EXISTS norm_act;
            --DROP TABLE IF EXISTS norm_act_filelink;

            CREATE TABLE IF NOT EXISTS public.norm_act (
                a_title public.citext,
                a_text public.citext,
                a_date timestamp without time zone,
                a_structure integer,
                a_number public.citext,
                ouid serial,
                a_publ_date timestamp without time zone
            );
            CREATE TABLE IF NOT EXISTS public.norm_act_filelink (
                a_ouid serial,
                a_fromid integer,
                a_toid public.citext,
                a_name public.citext,
                a_type public.citext
            );

            TRUNCATE norm_act, norm_act_filelink RESTART IDENTITY;

            INSERT INTO norm_act (
                a_publ_date,
                a_title,
                a_text,
                a_date,
                a_number,
                a_structure
            )
            SELECT
                --round(random()*10000), -- for integer
                now() + round(random()*1000) * '1 second'::interval, -- for timestamps
                %s,
                md5(random()::text),
                now() + round(random()*1000) * '1 second'::interval, -- for timestamps
                left(md5(random()::text), 4),
                round(random()*20)
            FROM generate_series(1,%s);
            '''
        self.connect()
        self.query_put(sql_npa_tables, params)                              # Обновления данных в таблице новостей СУС
        print('Созданы таблицы norm_act и norm_act_filelink')

    # Обновление Новостей
    def update_news_list(self, news_list):
        update_news = '''
            UPDATE public.cms_article
            SET a_title = %s, a_date= %s,
            a_image_index = %s, a_body = %s,
            a_publ_date = %s, a_resume = %s, a_structure = %s
            WHERE ouid = %s;
            '''
        for news in news_list:
            self.query_put(update_news, news.get_data())                              # Обновления данных в таблице новостей СУС

    # Запись файлов новостей
    def insert_news_files(self, newsfiles_list):
        insert_news_file = '''
            INSERT INTO public.CMS_NEWS2MEDIA (a_toid, a_description, a_fromid)
            VALUES (%s, %s, %s);
            '''
        for newsfile in newsfiles_list:
            self.query_put(insert_news_file, newsfile.get_data())               # Запись данных в таблицу медиафайлов СУС

    # # Создание тестовых таблиц новостей
    # def create_news_tables(self, params):
    #     sql_npa_tables = '''
    #         DROP TABLE IF EXISTS cms_article;
    #         DROP TABLE IF EXISTS cms_news2media;
    #         CREATE TABLE IF NOT EXISTS public.cms_article (
    #             ouid serial,
    #             a_title public.citext,
    #             a_date timestamp without time zone,
    #             a_image_index public.citext,
    #             a_body public.citext,
    #             a_publ_date timestamp without time zone,
    #             a_structure integer,
    #             a_resume public.citext
    #         );
    #         CREATE TABLE IF NOT EXISTS public.cms_news2media (
    #             a_editowner integer,
    #             a_ts timestamp without time zone,
    #             ouid serial,
    #             a_systemclass integer,
    #             guid public.citext,
    #             a_createdate timestamp without time zone,
    #             a_crowner integer,
    #             a_fromid integer,
    #             a_toid public.citext,
    #             a_remove_date timestamp without time zone,
    #             a_description public.citext
    #         );

    #             ouid
    #             a_title,
    #             a_date,
    #             a_publish,
    #             a_image_index public.citext,
    #             a_code public.citext,
    #             a_body public.citext,
    #             a_publ_date timestamp without time zone,
    #             a_structure integer,
    #             a_resume public.citext,
    #             a_like boolean,
    #             a_important boolean,
    #             a_organization integer
    #         INSERT INTO cms_article (
    #             a_publ_date, 
    #             a_title,
    #             a_text, 
    #             a_date, 
    #             a_number, 
    #             a_structure
    #         )
    #         SELECT
    #             --round(random()*10000), -- for integer
    #             now() + round(random()*1000) * '1 second'::interval, -- for timestamps
    #             %s,
    #             md5(random()::text),
    #             now() + round(random()*1000) * '1 second'::interval, -- for timestamps
    #             left(md5(random()::text), 4),
    #             round(random()*20)
    #         FROM generate_series(1,%s);
    #         '''
    #     self.query_put(sql_npa_tables, params)                              # Обновления данных в таблице новостей СУС
    #     print('Созданы таблицы cms_article и cms_news2media')


# TODO Сделать функцию для коммита
# Применение изменений
    def db_commit(self):
        self.conn.commit()
        with self.conn.cursor() as cur:
            cur.close()
        print("Изменения сохранены. Закрытие соединения")


def main():
    pass
