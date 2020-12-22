import re
from utils import time_test, get_config, get_csv_path, save_csv
from csv_objects import News, NewsIndexImgFile, NewsFile
from utils_db_local import DatabaseGenum as Database


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
                    file = NewsIndexImgFile(config, data)
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
        params = {
            "old_id": row[0],
            "structure": config["news_type"][row[1]],
            "title": row[2],
            "date": row[9],
            "image_index": str(row[7]).replace("^", "#"),
            "body": str(row[4]).replace("^", "#").replace("\r", "").replace("\n", ""),
            "publ_date": row[5],
            "resume": row[3]
        }
        news = News(params, config)
        news_list.append(news)
        # Получение медиафайлов из таблицы
        files_from_table, empty_news = news.get_mediafile_from_table(db_local)
        # Добавление проблемных новостей
        null_news.extend(empty_news)
        # Обратока ссылок на файлы
        files_from_text = news.update_body(NewsFile)
        # Обработка основного изображения
        index_image_file = get_index_file(config, news)
        row = {
                'structure': news.a_structure,
                'title': news.a_title,
                'resume': news.a_resume,
                'body': news.body,
                'classification': news.a_classification,
                'isPublish': news.isPublish,
                'pubmain': news.pubmain,
                "publ_date": news.a_publ_date.strftime("%d.%m.%Y %H:%M:%S"),
                "date": news.a_date.strftime("%d.%m.%Y %H:%M:%S"),
                'image_index': news.a_image_index,
                'mediaFiles': news.mediaFiles
            }
        fieldnames = row.keys()
        query_list.append(row)
        # TODO сделать полное описание или разделение на отдельные списки
        # news_files.extend(index_image_file)     # Основная картинка новости
        # news_files.extend(files_from_text)      # Обычные файлы из новосте, сохраняются в
        # news_files.extend(files_from_table)     # Медиафайлы из таблицы

    path_csv = get_csv_path(config, 'news')         # Получение пути для csv
    save_csv(path_csv, fieldnames, query_list)      # Сохранение словаря в csv

    # Копирование файлов
    for file in news_files:
        file.copy_news_file()
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
