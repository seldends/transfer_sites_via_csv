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
        query = '''
            SELECT "File"
            FROM public."sd4_LegalActFile"
            WHERE "LegalAct_id"=%s;
            '''
        npafiles_list = self.select_rows(query, id)
        return npafiles_list

    # Функция для получения нпа
    def get_npa_list(self, params):
        query = '''
            SELECT "id", "Type_id", "Title", "Article", "CreationDate", "ModificationDate", "AdoptionDate", "Number"
            FROM "sd4_LegalAct"
            WHERE "IsHidden"=False
            AND "Type_id" IN %s
            ORDER BY id DESC
            ;
            '''
        npa_list = self.select_rows(query, tuple(params))
        return npa_list

    # Функция для получения новостей
    def get_news_list(self, params):
        query = '''
            SELECT "id", "Group_id", "Title", "Article", "Summary", "CreationDate", "PublicationDate", "Image"
            FROM public."sd4_PublicationItem"
            WHERE "IsHidden"=False
            AND "CreationDate" > '2018-01-01 00:00:00'
            AND "Group_id" IN %s
            -- AND id > 28585
            ORDER BY id DESC
            -- LIMIT 1
            '''
        news_list = self.select_rows(query, tuple(params))
        return news_list

    # Функция для получения медиафайлов
    def get_news_files_list(self, id):
        query = '''
            SELECT "Image", "Title"
            FROM public."sd4_PublicationItemImage"
            WHERE "Item_id"=%s;
            '''
        newsfiles_list = self.select_rows(query, id)
        return newsfiles_list

    # Сохранение страниц
    def get_pages_list(self):
        query = '''
            SELECT "id","Parent_id","Title","Article", "Alias", "Path", "Level"
            FROM public."sd4_HtmlPage"
            WHERE "IsHidden"=false
            --AND "Alias"=%s
            ORDER BY id DESC;
            '''
        pages_list = self.select_rows(query)
        return pages_list

        # self.connect()
        # with self.conn.cursor() as cur:
        #     val = f'{code}%'
        #     conent = f'{content}'
        #     cur.execute(select_pages, (val, conent))
        #     records = cur.fetchall()
        #     cur.close()
        #     return records

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
        data = '## Таблица НПА\n| Название |Категория в старой системе | Количество объектов |\n| --- | --- | --- |\n'
        count = 0
        for obj in info:
            data += f'|{obj[1]}|{obj[0]}|{obj[2]}|\n'
            count += obj[2]
            print(f'тип {obj[0]} {obj[1]} количество {obj[2]}')
        data += f'|Всего|{len(info)}|{count}|\n'
        return data

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
        data = '## Таблица Новостей начиная с 2018-01-01 00:00:00\n| Название |Категория в старой системе | Количество объектов |\n| --- | --- | --- |\n'
        count = 0
        for obj in info:
            data += f'|{obj[1]}|{obj[0]}|{obj[2]}|\n'
            count += obj[2]
            print(f'тип {obj[0]} {obj[1]} количество {obj[2]}')
        data += f'|Всего|{len(info)}|{count}|\n'
        return data

    def get_title_from_path(self, alias):
        query = '''
            SELECT "Title"
            FROM public."sd4_HtmlPage"
            WHERE "Alias"=%s
            ORDER BY id DESC;
            '''
        title_list = self.select_rows(query, alias)
        return title_list

    # # TODO доделать замену
    # def get_title_from_path(self, path):
    #     path_titles = []
    #     page_path = path.split('/')
    #     query = '''
    #         SELECT "Title"
    #         FROM public."sd4_HtmlPage"
    #         WHERE "Alias"=%s
    #         ORDER BY id DESC;
    #         '''
    #     for parent_path in page_path:
    #         # page_title = db_local.get_title_from_path(parent_path)
    #         page_title = self.select_rows(query, parent_path)
    #         if page_title is not None:
    #             try:
    #                 path_title = str(page_title[0][0]).replace('/', '.')
    #                 # TODO
    #                 # forest 134
    #                 # ugzhi 125
    #                 # Нужно делать обрезку количества символов в пути, т.к. есть ограницение на 255 символов в пути
    #                 # опытным путем подбираю количество символов имени так, чтобы сумма с путем была меньше 255
    #                 # path_titles.append(path_title[:125])
    #                 # path_titles.append(path_title[:134])
    #                 # .replace('«','').replace('»','')
    #                 path_titles.append(path_title.replace('<a href=http..gk74.ru.Upload.prikazy.prikaz_34_03.03.20.pdf>', '').replace('?', '').replace('"', '').replace('\t','').replace("'", '').replace(":", '').replace('...','').strip())
    #             except IndexError as e:
    #                 print(f'У страниц с адресом состоящим из {page_path}, нет названий {page_title} Ошибка: {e}')
    #                 print('Проверить соответствует ли в бд путь алиасам страниц')
    #                 # print(e)
    #     return (path_titles)