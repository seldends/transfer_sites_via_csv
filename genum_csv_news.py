import re
from utils.util import time_test, get_config, get_csv_path, save_csv
from core.News import News
from core.File import NewsIndexImgFile, NewsFile
from utils.Genum import DatabaseGenum as Database


# Перенос Новостей
def transfer_news(config):
    news_list = []
    news_files = []
    files_from_text = []
    files_from_table = []
    null_news = []
    query_list = []

    db_local = Database(config["db_type"], config["db_name"])       # Объект подключения к бд со старыми данными
    db_local.news_info()
    data = db_local.get_news_list(config["news_type"].keys())       # Получение списка Новостей из старой таблицы
    print(len(data))
    for row in data:
        params = {
            "old_id":       row[0],
            "structure":    config["news_type"][row[1]],
            "title":        row[2],
            "date":         row[9],
            "image_index":  str(row[7]).replace("^", "#"),
            "body":         row[4],
            "publ_date":    row[5],
            "resume":       row[3]
        }
        news = News(params, config)
        # print(news)
        news_list.append(news)
        # Получение медиафайлов из таблицы
        files_from_table, empty_news = news.get_mediafile_from_table(db_local)
        # Добавление проблемных новостей
        null_news.extend(empty_news)
        # Обратока ссылок на файлы
        files_from_text = news.get_files_from_body(NewsFile)
        # Обработка основного изображения
        index_image_file = news.get_index_file()
        # Удаление ссылок на страницы
        news.delete_page_links()
        # Получение данных объекта
        obj = news.get_data()
        # print(obj)
        fieldnames = obj.keys()
        query_list.append(obj)
        # TODO сделать полное описание или разделение на отдельные списки
        news_files.extend(index_image_file)     # Основная картинка новости
        news_files.extend(files_from_text)      # Обычные файлы из новосте, сохраняются в
        news_files.extend(files_from_table)     # Медиафайлы из таблицы

    path_csv = get_csv_path(config, 'news')         # Получение пути для csv
    save_csv(path_csv, fieldnames, query_list)      # Сохранение словаря в csv

    # Копирование файлов
    # for file in news_files:
    #     print(file.new_link)
    #     file.copy_file()
    # TODO
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
        # "deti74",
        # "mindortrans74"
        # "mininform74"
        # "mincult74",
        # "forest74",
        # "chelarhiv74",
        # "ugzhi",
        "szn74",
        # "minstroy74",
        # "gk74",
        # "chelarhiv74",
        # "okn74"
    ]
    for site in sites:
        # Получение конфигурации
        config = get_config(site)
        # Перенос Новостей
        transfer_news(config)


if __name__ == "__main__":
    main()
