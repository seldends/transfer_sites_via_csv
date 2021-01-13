from utils.util import time_test, get_config, get_csv_path, save_csv, copy_files
from core.Npa import Npa
from core.File import NpaFile
from utils.Genum import DatabaseGenum as Database


# Перенос НПА
def transfer_npa(config):
    npa_list = []
    npa_files = []
    null_npa = []
    query_list = []

    db_type_local = config["db_type"]
    db_name_local = config["db_name"]

    db_local = Database(db_type_local, db_name_local)       # Объект подключения к бд со старыми данными
    db_local.npa_info()
    npa_types = tuple(config["npa_type"].keys())
    data = db_local.get_npa_list(npa_types)                 # Получение списка НПА из старой таблицы
    for row in data:
        if row[5]:  # На сайте отображается дата создания
            date_publ = row[5]  # 4 - дата создания
        else:
            date_publ = row[4]  # 5 - дата изменения
        if row[6]:  # Если пустая дата принятия, то подставить дату публикации
            date_accept = row[6]
        else:
            date_accept = date_publ
        params = {
            "old_id":       row[0],
            "structure":    config["npa_type"][row[1]],
            "title":        row[2],
            "body":         row[3],
            "date":         date_accept,
            "publ_date":    date_publ,
            "number":       row[7],
        }
        npa = Npa(params, config)
        npa_list.append(npa)
        # Получение медиафайлов из таблицы
        files_raw = db_local.get_npa_files_list(npa.old_id)
        files_from_table, empty_npa = npa.get_files_from_table(files_raw, NpaFile)
        # Добавление проблемных НПА
        null_npa.extend(empty_npa)
        # Файлы из текста
        files_from_text = npa.get_files_from_body(NpaFile)

        # Запись в атрибут файлы НПА
        npa.update_files(files_from_table)
        npa.update_files(files_from_text)

        # Удаление ссылок на страницы
        npa.delete_page_links()
        # Удаление ссылок на файлы из текста
        npa.delete_file_link(files_from_text)

        # Получение данных объекта
        obj = npa.get_data()
        fieldnames = obj.keys()
        query_list.append(obj)
        # TODO сделать полное описание или разделение на отдельные списки
        npa_files.extend(files_from_text)      # Файлы из текста описания НПА
        npa_files.extend(files_from_table)     # Файлы из таблицы файлов, связанные с текущим НПА

    path_csv = get_csv_path(config, 'npa')         # Получение пути для csv
    save_csv(path_csv, fieldnames, query_list)      # Сохранение словаря в csv

    # Копирование файлов
    # copy_files(npa_files)

    # TODO
    # report_date = {
    #     "element_list": npa_list,
    #     "files_from_table": files_from_table,
    #     "files_from_table": files_from_table,
    # }
    print(f'Количество пустых НПА : {len(null_npa)}')
    print(f'Количество НПА : {len(npa_list)}')
    print(f'Количество файлов НПА из таблицы : {len(files_from_table)}')
    print(f'Количество файлов НПА из текста НПА : {len(files_from_text)}')
    print(f'Количество файлов НПА общее : {len(npa_files)}')
    print(f"Количество НПА {str(len(data))}")


@time_test
def main():
    # Список конфигураций сайтов
    sites = [
        "szn74",
    ]
    for site in sites:
        # Получение конфигурации
        config = get_config(site)
        # Перенос НПА
        transfer_npa(config)


if __name__ == "__main__":
    main()
