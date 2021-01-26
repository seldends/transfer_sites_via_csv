import re
from utils.util import time_test, get_config, get_csv_path, save_csv
from core.Vacancy import Vacancy
from core.File import VacancyFile
from utils.Bitrix import DatabaseBitrix as Database


# Перенос НПА
def transfer_vacancy(config):
    vacancy_list = []
    filenames = []
    vacancy_files = []
    files_from_text = []
    files_from_table = []
    null_vacancy = []
    query_list = []

    db_type_local = config["db_type"]
    db_name_local = config["db_name"]

    db_local = Database(db_type_local, db_name_local)       # Объект подключения к бд со старыми данными

    vacancy_types = list(config["vacancy_type"].keys())
    data = db_local.get_obj_list(vacancy_types)                 # Получение списка НПА из старой таблицы
    for row in data:
        params = {
            "old_id":           row[0],
            "structure":        config["vacancy_type"][row[1]],
            "title":            row[2],
            "date":             row[3],
            "body":             row[4],
            "publ_date":        row[5],
            "stageDate1":       row[5],
            "stageDate2":       row[5],
        }
        vacancy = Vacancy(params, config)
        vacancy_list.append(vacancy)
        # # Получение медиафайлов из таблицы
        files_from_table, empty_vacancy = vacancy.get_vacancyfile_from_table(db_local)
        # Атрибуты УТП
        vacancy.bitrix_get_utp_from_body()
        # Добавление проблемных НПА
        null_vacancy.extend(empty_vacancy)
        # Замена ссылок и записывание в атрибут файлы НПА
        files_from_text = vacancy.get_vacancyfile_from_body(VacancyFile)
        # Замена ссылок на файлы
        # files_from_text = vacancy.update_body(vacancyFile)

        # Удаление ссылок на страницы
        vacancy.delete_page_links()

        # Получение данных объекта
        obj = vacancy.get_data()
        fieldnames = obj.keys()
        query_list.append(obj)
        # TODO сделать полное описание или разделение на отдельные списки
        vacancy_files.extend(files_from_text)      # Файлы из текста описания НПА
        vacancy_files.extend(files_from_table)     # Файлы из таблицы файлов, связанные с текущим НПА

    path_csv = get_csv_path(config, 'vacancy')         # Получение пути для csv
    save_csv(path_csv, fieldnames, query_list)      # Сохранение словаря в csv

    # Копирование файлов
    # for file in vacancy_files:
    #     print(file.new_link)
    #     file.copy_file()
    # TODO
    print(f'Количество пустых НПА : {len(null_vacancy)}')
    print(f'Количество НПА : {len(vacancy_list)}')
    print(f'Количество файлов НПА из таблицы : {len(files_from_table)}')
    print(f'Количество файлов НПА из текста НПА : {len(files_from_text)}')
    print(f'Количество файлов НПА общее : {len(vacancy_files)}')
    print(f"Количество НПА {str(len(data))}")


@time_test
def main():
    # Список конфигураций сайтов
    sites = [
        "imchel74",
    ]
    for site in sites:
        # Получение конфигурации
        config = get_config(site)
        # Перенос НПА
        transfer_vacancy(config)


if __name__ == "__main__":
    main()
