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

        # Функция для получения новостей
    def get_npa_list(self, params):
        # MariaDB
        select_npa_local = '''
            SELECT
            ID as id,
            IBLOCK_ID,
            NAME as title,
            DATE_CREATE as date_create,
            DETAIL_TEXT as body,
            TIMESTAMP_X as date_publ,
            XML_ID
            FROM imchel_10_12.b_iblock_element
            WHERE ACTIVE = 'Y'
            AND IBLOCK_ID in (146)
            -- and NAME like '%регламент предоставления государственной услуги "Предоставление%'
            order by ID DESC
            ;
            '''
        # news_list = self.select_rows(select_news_local, params)
        npa_list = self.select_rows(select_npa_local)
        return npa_list

        # Функция для получения ouid нпа
    def get_npa_files_list(self, id):
        select_npafiles_local = '''
            SELECT CONCAT('upload/',b_file.SUBDIR, '/', b_file.FILE_NAME) as file_path
            FROM imchel_10_12.b_file
            LEFT JOIN imchel_10_12.b_iblock_element_property
            ON b_iblock_element_property.VALUE = imchel_10_12.b_file.ID
            WHERE b_iblock_element_property.IBLOCK_ELEMENT_ID=%s;
            '''
        npafiles_list = self.select_rows(select_npafiles_local, id)
        return npafiles_list

    def get_auction_list(self, params):
        # MariaDB
        select_auction_local = '''
            SELECT
            ID as id,
            IBLOCK_ID,
            NAME as title,
            DATE_CREATE as date_create,
            DETAIL_TEXT as body,
            TIMESTAMP_X as date_publ,
            XML_ID
            FROM imchel_10_12.b_iblock_element
            WHERE ACTIVE = 'Y'
            AND IBLOCK_ID in (42)
            -- AND IBLOCK_ID in (43)
            order by ID DESC
            ;
            '''
        # news_list = self.select_rows(select_news_local, params)
        auction_list = self.select_rows(select_auction_local)
        return auction_list

        # Функция для получения ouid нпа
    def get_auction_files_list(self, id):
        select_auctionfiles_local = '''
            SELECT CONCAT('upload/',b_file.SUBDIR, '/', b_file.FILE_NAME) as file_path
            FROM imchel_10_12.b_file
            LEFT JOIN imchel_10_12.b_iblock_element_property
            ON b_iblock_element_property.VALUE = imchel_10_12.b_file.ID
            WHERE b_iblock_element_property.IBLOCK_ELEMENT_ID=%s;
            '''
        auctionfiles_list = self.select_rows(select_auctionfiles_local, id)
        return auctionfiles_list