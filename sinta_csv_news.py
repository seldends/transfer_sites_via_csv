import re
from utils import time_test, get_config, get_csv_path, save_csv
from csv_objects import News, File, NewsFile
from utils_db_local import DatabaseSinta as Database


# TODO подумать как можно объединить общий функционал на функции обработки файлов
# Получение файла Новостей из описания Новостей
def get_file_from_body(config, obj):
    old_sitename = config["old_name"]
    pattern_file_1 = fr'(<a href=\"((?:http:\/\/(?:www\.|){old_sitename}|)\/(((?:dokumentydok\/[^\/]{{1,75}}|upload\/iblock\/[^\/]{{0,4}}|Upload\/files|Files\/DiskFile\/(?:|[0-9]{{4}}\/)[a-zA-Z]{{1,10}}|opendata|Storage\/Image\/PublicationItem\/Image\/src\/[0-9]{{1,5}})\/)([^>]{{1,450}}\.[a-zA-Z]{{3,5}})))\s?\"[^>]{{0,250}}>)'
    pattern_file_2 = fr'(<img alt=\"[^\/]{{0,50}}\"(?:\sclass=\"[^\/]{{0,50}}\"|)\ssrc=\"((?:http:\/\/(?:www\.|){old_sitename}|)\/(((?:Upload\/images\/|Storage\/Image\/PublicationItem\/Article\/src\/[0-9]{{1,5}}\/))([^>\/]{{1,450}}\.[a-zA-Z]{{3,5}})))\"[^>]{{0,550}}>)'
    # pattern_file_2 = fr'(<img alt=\".{0,50}\" )'
    pattern_list = {
        "news":     pattern_file_1,         # паттерн 1
        "news2":    pattern_file_2,         # паттерн 2
    }
    files = []
    filenames = []
    for link_type, pattern in pattern_list.items():
        # print(pattern)
        try:
            links = re.findall(pattern, obj.a_body)
            # Если есть совпадения
            if len(links) > 0:
                for link in links:
                    data = {
                        "full_link":            link[0],    # Полная ссылка с a href и стилями. Пример:     <a href="http://szn74.ru/Upload/files/Приказ МПР 496 от 111113 с изм 141217.rtf">
                        "file_full_path":       link[1],    # Ссылка на файл.                   Пример:     http://szn74.ru/Upload/files/Приказ МПР 496 от 111113 с изм 141217.rtf
                        "file_path":            link[2],    # Полный путь до файла.             Пример:     Upload/files/Приказ МПР 496 от 111113 с изм 141217.rtf
                        "file_relative_path":   link[3],    # Папка файла.                      Пример:     Upload/files/
                        "file":                 link[4],    # Имя файла с расширением.          Пример:     Приказ МПР 496 от 111113 с изм 141217.rtf
                    }
                    file = File(config, data, link_type)
                    files.append(file)
                    filenames.append(file.encoded_filename)
                    old_file_path = file.file_full_path
                    new_file_path = file.str_new_link
                    obj.a_body = str(obj.a_body).replace(old_file_path, new_file_path)     # Замены ссылки
        except Exception as e:
            print(e)
    return files, filenames


# Получение медиафайлов из таблицы
def get_mediafile_from_table(config, db_local, news):
    null_news = []
    pattern_file_1 = r'(\/(PublicationItemImage\/Image\/src\/[0-9]{1,5}\/)([^>]{1,75}))'
    pattern_list = {
        "mediafiles": pattern_file_1,         # паттерн 1
    }
    newsfiles_list = db_local.get_news_files_list(news.old_id)
    mediafiles = []
    mediafiles_name = []
    for mediafile in newsfiles_list:
        old_path = mediafile[0]
        # Проверка пустой ли путь у файлв Новостей (запись есть, но значение пустое, то добавлять в список пуcтых)
        if old_path:
            file_path = str(old_path).replace("\\", "/")
            for link_type, pattern in pattern_list.items():
                try:
                    links = re.findall(pattern, file_path)
                    # Если есть совпадения
                    if len(links) > 0:
                        for link in links:
                            data = {
                                "file_full_path":       link[0],    # Ссылка на файл.                   Пример:     /PublicationItemImage/Image/src/178/IMG_2038.JPG
                                "file_relative_path":   link[1],    # Папка файла.                      Пример:     /PublicationItemImage/Image/src/178/
                                "file":                 link[2],    # Имя файла с расширением.          Пример:     IMG_2038.JPG
                            }
                            file = File(config, data, link_type)
                            mediafiles.append(file)
                            mediafiles_name.append(file.encoded_filename)
                            # TODO запись в атрибут медиафайлы объектов через запятую
                            if news.mediaFiles != '':
                                news.mediaFiles = ','.join((news.mediaFiles, file.str_new_link))
                            else:
                                news.mediaFiles = file.str_new_link
                except AttributeError as e:
                    print('Ошибка в создании файла Новостей', e)
        else:
            null_news.append(news.old_id)
            print(f'Отсутствует имя файла ид старой новости : {news.old_id}')
    return mediafiles, mediafiles_name, null_news


def get_index_file(config, news):
    pattern_file_1 = r'(\\(PublicationItem\\Image\\src\\[0-9]{1,5}\\)([^>\\]{1,75}))'
    pattern_list = {
        "indeximage": pattern_file_1,         # паттерн 1
    }
    old_path = news.a_image_index
    index_file = []
    # print(old_path)
    # Проверка пустой ли путь у файлв Новостей (запись есть, но значение пустое, то добавлять в список пуcтых)
    for link_type, pattern in pattern_list.items():
        try:
            links = re.findall(pattern, str(old_path))
            # Если есть совпадения
            if len(links) > 0:
                for link in links:
                    data = {
                        "file_full_path":       link[0],    # Ссылка на файл.                   Пример:     \PublicationItem\Image\src\10836\images (24).jpg
                        "file_relative_path":   link[1],    # Папка файла.                      Пример:     PublicationItem\Image\src\10836\
                        "file":                 link[2],    # Имя файла с расширением.          Пример:     images (24).jpg
                    }
                    file = File(config, data, link_type)
                    news.a_image_index = file.str_new_link
                    index_file.append(file)
        except AttributeError as e:
            print('Ошибка в создании файла Новостей', e)
    return index_file


# Перенос Новостей
def transfer_news(config):
    news_list = []
    filenames = []
    news_files = []
    files_from_text = []
    files_from_table = []
    null_news = []
    query_list = []

    db_type_local = config["db_type"]
    db_name_local = config["db_name"]

    db_local = Database(db_type_local, db_name_local)       # Объект подключения к бд со старыми данными

    news_types = tuple(config["news_type"].keys())
    data = db_local.get_news_list(news_types)                 # Получение списка Новостей из старой таблицы

    for row in data:
        # print(row)
        params = {
            "old_id": row[0],
            "structure": config["news_type"][row[1]],
            "title": row[2],
            "body": str(row[3]).replace("^", "#").replace("\r", "").replace("\n", ""),
            "resume": row[4],
            "date": row[5],
            "publ_date": row[6],
            "image_index": str(row[7]).replace("^", "#"),
        }
        news = News(params, config)
        # print(news.a_image_index)
        news.update_body()
        news.delete_links()
        news.delete_links2()
        # news_list.append(news)
        # Получение медиафайлов из таблицы
        # files_from_table, file_names_from_table, empty_news = get_mediafile_from_table(config, db_local, news)
        # Добавление проблемных новостей
        # null_news.extend(empty_news)
        # Обратока ссылок на файлы
        # files_from_text, filenames_from_text = get_file_from_body(config, news)
        # Обработка основного изображения
        #index_image_file = get_index_file(config, news)
        # if files_from_text:
            # print(f'{files_from_text}-{filenames_from_text}')
        # row = {
        #         'structure': news.structure,
        #         'title': news.title,
        #         'resume': news.a_resume,
        #         'body': news.a_body,
        #         'classification': news.a_classification,
        #         'isPublish': news.isPublish,
        #         'pubmain': news.pubmain,
        #         "publ_date": news.a_publ_date.strftime("%d.%m.%Y %H:%M:%S"),
        #         "date": news.a_date.strftime("%d.%m.%Y %H:%M:%S"),
        #         'image_index': news.a_image_index,
        #         'mediaFiles': news.mediaFiles
        #     }
        # fieldnames = row.keys()
        # query_list.append(row)
        # TODO сделать полное описание или разделение на отдельные списки
        # news_files.extend(index_image_file)     # Основная картинка новости
        # news_files.extend(files_from_text)      # Обычные файлы из новосте, сохраняются в
        # news_files.extend(files_from_table)     # Медиавфайлы из таблицы 

    # path_csv = get_csv_path(config, 'news')         # Получение пути для csv
    # save_csv(path_csv, fieldnames, query_list)      # Сохранение словаря в csv

    # Копирование файлов
    # for file in news_files:
    #     file.copy_news_file()
    # TODO
    # news.delete_links()         # Удаление ссылок на страницы
    # Удаление содержимого описания Новостей
    # news.transform_text()
    print(f'Количество пустых Новостей : {len(null_news)}')
    print(f'Количество Новостей : {len(news_list)}')
    print(f'Количество файлов Новостей из таблицы : {len(files_from_table)}')
    print(f'Количество файлов Новостей из текста Новостей : {len(files_from_text)}')
    print(f'Количество файлов Новостей общее : {len(news_files)}')
    print(f"Количество Новостей {str(len(data))}")


@time_test
def main():
    # Список конфигураций сайтов
    sites = [
        "pravmin74",
    ]
    for site in sites:
        # Получение конфигурации
        config = get_config(site)
        # Перенос Новостей
        transfer_news(config)


if __name__ == "__main__":
    main()
