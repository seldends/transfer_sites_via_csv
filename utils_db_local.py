import psycopg2
import sys
import yaml
import mariadb
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


class DatabaseSinta(Database):
    def connect(self):
        if self.conn is None:
            if self.dbtype == 'mariadb':
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

        # Функция для получения новостей
    def get_news_list(self, params):
        # MariaDB
        select_news_local = '''
            SELECT
            node.nid as id,
            field_data_field_news_cat.field_news_cat_tid as categoty,
            node.title as title,
            field_data_body.body_value as body,
            field_data_field_teaser.field_teaser_value as resume,
            node.created as date_created, 
            node.changed as date_edit,
            file_managed.uri as image_url,
            field_data_field_image.field_image_alt as image_alt,
            file_managed.origname as image_name,
            node.vid, node.uid, node.status
            FROM pravmin74_12_11.node 
            LEFT JOIN pravmin74_12_11.field_data_field_image
            ON field_data_field_image.entity_id=node.nid
            LEFT JOIN pravmin74_12_11.file_managed
            ON file_managed.fid=field_data_field_image.field_image_fid
            LEFT JOIN pravmin74_12_11.field_data_field_news_cat
            ON field_data_field_news_cat.entity_id=node.nid
            LEFT JOIN pravmin74_12_11.field_data_body
            ON field_data_body.entity_id=node.nid
            LEFT JOIN pravmin74_12_11.field_data_field_teaser
            ON field_data_field_teaser.entity_id=node.nid
            WHERE node.type='news'
            AND node.created > 1514746800
            AND field_data_field_news_cat.field_news_cat_tid IN (104, 105)
            ORDER BY node.nid DESC
            ;
            '''
        # news_list = self.select_rows(select_news_local, params)
        news_list = self.select_rows(select_news_local)
        return news_list
    # TODO
    # Функция для получения медиафайлов
    def get_news_files_list(self, id):
        select_mediafiles_local = """
            SELECT
            file_managed.uri,
            field_data_field_gallery.field_gallery_alt
            FROM file_managed
            LEFT JOIN field_data_field_gallery
            ON field_data_field_gallery.field_gallery_fid=file_managed.fid
            WHERE field_data_field_gallery.bundle='news'
            AND field_data_field_gallery.deleted=0
            AND file_managed.filemime LIKE '%image%'
            AND field_data_field_gallery.entity_id=?;
        """
        select_newsfiles_local = '''
                SELECT "Image", "Title"
                FROM public."sd4_PublicationItemImage"
                WHERE "Item_id"=%s;
                '''
        newsfiles_list = self.select_rows(select_mediafiles_local, id)
        return newsfiles_list


class DatabaseBitrix(Database):
    def connect(self):
        if self.conn is None:
            if self.dbtype == 'mariadb':
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

        # Функция для получения новостей
    def get_news_list(self, params):
        # MariaDB
        select_news_local = '''
            SELECT
            ID as id,
            IBLOCK_ID,
            NAME as title,
            DATE_CREATE as date_create,
            PREVIEW_PICTURE as index_img,
            DETAIL_TEXT as body,
            TIMESTAMP_X as date_publ,
            PREVIEW_TEXT as resume,
            XML_ID
            FROM imchel_10_12.b_iblock_element
            WHERE DATE_CREATE > '2018-01-01 00:00:00'
            AND IBLOCK_ID = 13
            AND ACTIVE = 'Y'
            order by ID DESC
            ;
            '''
        # news_list = self.select_rows(select_news_local, params)
        news_list = self.select_rows(select_news_local)
        return news_list


def main():
    pass
