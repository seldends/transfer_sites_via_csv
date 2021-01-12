import re
from utils.util import time_test, get_config, get_csv_path, save_csv
from core.News import News
from core.File import NewsIndexImgFile, NewsFile, NewsMediaFile
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
    data = db_local.get_obj_list(news_types)                 # Получение списка Новостей из старой таблицы
    for row in data:
        params = {
            "old_id":       row[0],
            "structure":    config["news_type"][row[1]],
            "title":        row[2],
            "date":         row[3],
            "body":         row[4],
            "publ_date":    row[5],
            "resume":       row[6],
            "image_index":  row[7],
        }
        news = News(params, config)
        news_list.append(news)
        # Получение медиафайлов из таблицы
        files_raw = db_local.get_news_files_list(news.old_id)
        files_from_table, empty_news = news.get_files_from_table(files_raw, NewsMediaFile)
        # Добавление проблемных новостей
        null_news.extend(empty_news)

        # Файлы из текста
        files_from_text = news.get_files_from_body(NewsFile)

        # Запись в атрибут файлы НПА
        news.update_files(files_from_table)

        # Удаление ссылок на страницы
        news.delete_page_links()

        # Замена ссылок на файлы из текста
        news.replace_file_link(files_from_text)
        # Обработка основного изображения
        # index_image_file = get_index_file(config, news)
        # Получение данных объекта
        obj = news.get_data()
        fieldnames = obj.keys()
        query_list.append(obj)
        # TODO сделать полное описание или разделение на отдельные списки
        # news_files.extend(index_image_file)     # Основная картинка новости
        news_files.extend(files_from_text)      # Обычные файлы из новости
        news_files.extend(files_from_table)     # Медиафайлы из таблицы

    path_csv = get_csv_path(config, 'news')         # Получение пути для csv
    save_csv(path_csv, fieldnames, query_list)      # Сохранение словаря в csv

    # Копирование файлов
    # for file in news_files:
    #     print(file.new_link)
    #     file.copy_file()
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
