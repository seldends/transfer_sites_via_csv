import re
from utils.util import time_test, get_config, get_csv_path, save_csv
from core.News import News
from core.File import NewsIndexImgFile, NewsFile
from utils.Bitrix import DatabaseBitrix as Database


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
        params = {
            "old_id":       row[0],
            "structure":    config["news_type"][row[1]],
            "title":        row[2],
            "date":         row[3],
            "image_index":  str(row[4]).replace("^", "#"),
            "body":         str(row[5]).replace("^", "#").replace("\r", "").replace("\n", "").replace('<p style="text-align: justify;"></p>', '').replace('<p style="text-align: justify;">	 &nbsp;</p>', '').replace('<p style="text-align: justify;">	<br></p>', '').replace('<p style="text-align: justify;"> <b>', '<p style="text-align: justify;">'),
            "publ_date":    row[6],
            "resume":       str(row[7]).replace('<p style="text-align: justify;">', '').replace('<p>','').replace('<br>','').replace('p>','').replace('br>','').replace('<div>','').replace('div>','')
        }
        news = News(params, config)
        news_list.append(news)
        # Получение медиафайлов из таблицы
        # files_from_table, empty_news = news.get_mediafile_from_table(db_local)
        # Добавление проблемных новостей
        # null_news.extend(empty_news)
        # Обратока ссылок на файлы
        files_from_text = news.update_body(NewsFile)
        # Удаление ссылок на страницы
        news.delete_links()
        # Обработка основного изображения
        # index_image_file = get_index_file(config, news)
        row = {
                'structure':        news.structure,
                'title':            news.title,
                'resume':           re.sub(r'[\n]{2,3}', r'', news.resume),
                'body':             re.sub(r'[\n]{2,3}', r'', news.body),
                'classification':   news.classification,
                'isPublish':        news.isPublish,
                'pubmain':          news.pubmain,
                "publ_date":        news.date_publication.strftime("%d.%m.%Y %H:%M:%S"),
                "date":             news.date.strftime("%d.%m.%Y %H:%M:%S"),
                # 'image_index':     news.a_image_index,
                # 'mediaFiles':      news.objFiles
            }
        fieldnames = row.keys()
        query_list.append(row)
        # TODO сделать полное описание или разделение на отдельные списки
        # news_files.extend(index_image_file)     # Основная картинка новости
        news_files.extend(files_from_text)      # Обычные файлы из новосте, сохраняются в
        # news_files.extend(files_from_table)     # Медиафайлы из таблицы

    path_csv = get_csv_path(config, 'news')         # Получение пути для csv
    save_csv(path_csv, fieldnames, query_list)      # Сохранение словаря в csv

    # Копирование файлов
    # for file in news_files:
    #     file.copy_news_file()
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
        "imchel74",
    ]
    for site in sites:
        # Получение конфигурации
        config = get_config(site)
        # Перенос Новостей
        transfer_news(config)


if __name__ == "__main__":
    main()
