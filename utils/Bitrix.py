import mariadb
from utils.Database import Database
import sys


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

    def get_obj_list(self, params):
        # sql = """SELECT avg(downloadtime) FROM tb_npp where date(date) = %s 
        #  and substring(host,6,3) in ({c})""".format(
        #     c=', '.join(['%s']*len(dc)))
        # MariaDB
        # test = ', '.join(['%s']*len(params))
        # print(test, params, len(params))
        select_obj_local = f'''
            SELECT
            ID as id,
            IBLOCK_ID,
            NAME as title,
            DATE_CREATE as date_create,
            DETAIL_TEXT as body,
            TIMESTAMP_X as date_publ,
            PREVIEW_TEXT as resume,
            PREVIEW_PICTURE as index_img
            FROM imchel_10_12.b_iblock_element
            WHERE ACTIVE = 'Y'
            AND IBLOCK_ID in (43, 42)
            order by ID DESC
            ;
            '''
        # print(select_obj_local)
        # news_list = self.select_rows(select_news_local, params)
        # obj_list = self.select_rows(select_obj_local, test)
        obj_list = self.select_rows(select_obj_local)
        return obj_list

    def get_obj_files_list(self, id):
        select_obj_files_local = '''
            SELECT CONCAT('upload/',b_file.SUBDIR, '/', b_file.FILE_NAME) as file_path
            FROM imchel_10_12.b_file
            LEFT JOIN imchel_10_12.b_iblock_element_property
            ON b_iblock_element_property.VALUE = imchel_10_12.b_file.ID
            WHERE b_iblock_element_property.IBLOCK_ELEMENT_ID=%s;
            '''
        obj_files_list = self.select_rows(select_obj_files_local, id)
        return obj_files_list

    # Функция для получения ouid нпа
    def get_npa_files_list(self, id):
        npafiles_list = self.get_obj_files_list(id)
        return npafiles_list

    def get_doc_files_list(self, id):
        docfiles_list = self.get_obj_files_list(id)
        return docfiles_list

    def get_auction_files_list(self, id):
        auctionfiles_list = self.get_obj_files_list(id)
        return auctionfiles_list

    def get_vacancy_files_list(self, id):
        vacancyfiles_list = self.get_obj_files_list(id)
        return vacancyfiles_list

    def get_news_files_list(self, id):
        select_obj_local = '''
            SELECT
            ID as id,
            IBLOCK_ID,
            NAME as title,
            DATE_CREATE as date_create,
            DETAIL_TEXT as body,
            TIMESTAMP_X as date_publ,
            PREVIEW_TEXT as resume,
            PREVIEW_PICTURE as index_img
            FROM imchel_10_12.b_iblock_element
            WHERE ACTIVE = 'Y'
            AND DATE_CREATE > '2018-01-01 00:00:00'
            AND IBLOCK_ID in (13)
            order by ID DESC
            ;
            '''
        # news_list = self.select_rows(select_news_local, params)
        obj_list = self.select_rows(select_obj_local)
        return obj_list

