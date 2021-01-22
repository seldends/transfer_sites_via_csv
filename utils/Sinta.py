import mariadb
from utils.Database import Database
import sys


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
            REPLACE(file_managed.uri, 'hash://','') as image_url,
            field_data_field_image.field_image_alt as image_alt,
            file_managed.origname as image_name,
            node.vid, node.uid, node.status
            FROM node
            LEFT JOIN field_data_field_image
            ON field_data_field_image.entity_id=node.nid
            LEFT JOIN file_managed
            ON file_managed.fid=field_data_field_image.field_image_fid
            LEFT JOIN field_data_field_news_cat
            ON field_data_field_news_cat.entity_id=node.nid
            LEFT JOIN field_data_body
            ON field_data_body.entity_id=node.nid
            LEFT JOIN field_data_field_teaser
            ON field_data_field_teaser.entity_id=node.nid
            WHERE node.type='news'
            AND node.created > 1514746800
            AND field_data_field_news_cat.field_news_cat_tid IN (104, 105)
            ORDER BY node.nid DESC
            LIMIT 500
            ;
            '''
        # news_list = self.select_rows(select_news_local, tuple(params))
        news_list = self.select_rows(select_news_local)
        return news_list

    # TODO Функция для получения медиафайлов
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
        newsfiles_list = self.select_rows(select_mediafiles_local, id)
        return newsfiles_list

    # Функция для получения НПА
    def get_npa_list(self, params):
        # MariaDB
        select_npa_local = '''
            SELECT
            node.nid as id,
            field_data_field_legal_acts.field_legal_acts_tid as category,
            node.title as title,
            -- REPLACE(field_data_body.body_value, 'None','') as body
            field_data_body.body_value as body,
            node.created as date_created,
            node.changed as date_edit,
            field_data_field_npa_accept_date.field_npa_accept_date_value as accept_date,
            field_data_field_npa_number.field_npa_number_value as npa_number
            FROM node
            LEFT JOIN field_data_field_legal_acts
            ON field_data_field_legal_acts.entity_id=node.nid
            LEFT JOIN field_data_field_npa_accept_date
            ON field_data_field_npa_accept_date.entity_id=node.nid
            LEFT JOIN field_data_field_npa_number
            ON field_data_field_npa_number.entity_id=node.nid
            LEFT JOIN field_data_body
            ON field_data_body.entity_id=node.nid
            WHERE node.type='legal_acts'
            -- AND field_data_field_legal_acts.field_legal_acts_tid IN (3, 4, 5, 6)
            AND field_data_field_legal_acts.field_legal_acts_tid IN (3)
            -- AND field_data_field_legal_acts.field_legal_acts_tid IN (4)
            -- AND field_data_field_legal_acts.field_legal_acts_tid IN (5)
            -- AND field_data_field_legal_acts.field_legal_acts_tid IN (6)
            ORDER BY node.nid DESC
            LIMIT 50
            ;
            '''
        # npa_list = self.select_rows(select_npa_local, params)
        npa_list = self.select_rows(select_npa_local)
        return npa_list

        # TODO Функция для получения медиафайлов
    def get_npa_files_list(self, id):
        select_npafiles_local = """
            SELECT
            -- file_managed.uri as file_url,
            REPLACE(file_managed.uri, 'public://','sites/default/files/') as file_url,
            -- field_data_field_upload.entity_id,
            -- field_data_field_upload.revision_id,
            field_data_field_upload.field_upload_description
            FROM field_data_field_upload
            LEFT JOIN file_managed
            ON file_managed.fid=field_data_field_upload.field_upload_fid
            where field_data_field_upload.bundle ='legal_acts'
            AND field_data_field_upload.entity_id=?
        """
        npafiles_list = self.select_rows(select_npafiles_local, id)
        return npafiles_list

    def npa_info(self):
        query = """
            SELECT
            field_data_field_legal_acts.field_legal_acts_tid as npa_type,
            COUNT(node.nid) as npa_counts
            FROM node
            LEFT JOIN field_data_field_legal_acts
            ON field_data_field_legal_acts.entity_id=node.nid
            WHERE node.type='legal_acts'
            GROUP BY field_data_field_legal_acts.field_legal_acts_tid
            ORDER BY field_data_field_legal_acts.field_legal_acts_tid;
        """

        info = self.select_rows(query)
        data = '## Таблица НПА\n| Название |Категория в старой системе | Количество объектов |\n| --- | --- | --- |\n'
        count = 0
        for obj in info:
            data += f'| --- |{obj[0]}|{obj[1]}|\n'
            count += obj[1]
        data += f'|Всего|{len(info)}|{count}|\n'
        return data

        # for npa_type in npa_info:
        #     print(f'тип {npa_type[0]} количество {npa_type[1]}')

    def news_info(self):
        query = """
            SELECT
            field_data_field_news_cat.field_news_cat_tid as news_type,
            COUNT(node.nid) as news_counts
            FROM node
            LEFT JOIN field_data_field_news_cat
            ON field_data_field_news_cat.entity_id=node.nid
            WHERE node.type='news'
            GROUP BY field_data_field_news_cat.field_news_cat_tid
            ORDER BY field_data_field_news_cat.field_news_cat_tid;
        """
        npa_info = self.select_rows(query)
        for npa_type in npa_info:
            print(f'тип {npa_type[0]} количество {npa_type[1]}')

        info = self.select_rows(query)
        data = '## Таблица Новостей начиная с 2018-01-01 00:00:00\n| Название |Категория в старой системе | Количество объектов |\n| --- | --- | --- |\n'
        count = 0
        for obj in info:
            data += f'| --- |{obj[0]}|{obj[1]}|\n'
            count += obj[1]
        data += f'|Всего|{len(info)}|{count}|\n'
        return data
