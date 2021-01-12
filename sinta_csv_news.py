from utils.util import time_test, get_config, get_csv_path, save_csv, copy_files
from core.News import News
from core.File import NewsIndexImgFile, NewsFile, NewsMediaFile
from utils.Sinta import DatabaseSinta as Database


# Перенос Новостей
def transfer_news(config):
    news_list = []
    files = []
    all_files_from_text = []
    all_files_from_table = []
    all_index_image_file = []
    null_news = []
    query_list = []

    # db_type_local = config["db_type"]
    # db_name_local = config["db_name"]

    db_local = Database(config["db_type"], config["db_name"])       # Объект подключения к бд со старыми данными

    news_types = tuple(config["news_type"].keys())
    data = db_local.get_news_list(news_types)                 # Получение списка Новостей из старой таблицы
    for row in data:
        params = {
            "old_id":       row[0],
            "structure":    config["news_type"][row[1]],
            "title":        row[2],
            "body":         row[3],
            "resume":       row[4],
            "date":         row[5],
            "publ_date":    row[6],
            "image_index":  str(row[7]).replace("^", "#"),
        }
        news = News(params, config)
        news_list.append(news)
        # Получение медиафайлов из таблицы
        files_raw = db_local.get_news_files_list(news.old_id)
        # Обработка файлов из таблицы
        files_from_table, empty_news = news.get_files_from_table(files_raw, NewsMediaFile)
        # Файлы из текста
        files_from_text = news.get_files_from_body(NewsFile)
        # Добавление проблемных новостей
        null_news.extend(empty_news)

        # Запись в атрибут файлы НПА
        news.update_files(files_from_table)

        # Удаление ссылок на страницы
        news.delete_page_links()

        # Замена ссылок на файлы из текста
        news.replace_file_link(files_from_text)
        # Обработка основного изображения
        index_image_file = news.get_index_file()
        # Получение данных объекта
        obj = news.get_data()
        fieldnames = obj.keys()
        query_list.append(obj)
        # TODO сделать полное описание или разделение на отдельные списки
        all_index_image_file.extend(index_image_file)     # Основная картинка новости
        all_files_from_text.extend(files_from_text)      # Обычные файлы из новости
        all_files_from_table.extend(files_from_table)     # Медиафайлы из таблицы

    path_csv = get_csv_path(config, 'news')         # Получение пути для csv
    save_csv(path_csv, fieldnames, query_list)      # Сохранение словаря в csv

    # Копирование файлов
    files.extend(all_index_image_file)     # Основная картинка новости
    files.extend(all_files_from_text)      # Обычные файлы из новости
    files.extend(all_files_from_table)     # Медиафайлы из таблицы

    copy_files(files)

    print(f'Количество пустых Новостей : {len(null_news)}')
    print(f'Количество Новостей : {len(query_list)}')
    print(f'Количество файлов Новостей из таблицы : {len(all_files_from_table)}')
    print(f'Количество файлов Новостей из текста Новостей : {len(all_files_from_text)}')
    print(f'Количество файлов Новостей общее : {len(files)}')
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
