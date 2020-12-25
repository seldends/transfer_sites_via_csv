import re
from utils import time_test, get_config, get_csv_path, save_csv
from csv_objects import Npa, NpaFile
from utils_db_local import DatabaseBitrix as Database


# Перенос НПА
def transfer_npa(config):
    npa_list = []
    filenames = []
    npa_files = []
    files_from_text = []
    files_from_table = []
    null_npa = []
    query_list = []

    db_type_local = config["db_type"]
    db_name_local = config["db_name"]

    db_local = Database(db_type_local, db_name_local)       # Объект подключения к бд со старыми данными

    npa_types = list(config["npa_type"].keys())
    data = db_local.get_npa_list(npa_types)                 # Получение списка НПА из старой таблицы
    for row in data:
        params = {
            "old_id": row[0],
            "structure": config["npa_type"][row[1]],
            "title": row[2],
            "date": row[3],
            "body": str(row[4]).replace("^", "#").replace("\r", "").replace("\n", "").replace('<p style="text-align: justify;"></p>', '').replace('<p style="text-align: justify;">	 &nbsp;</p>', '').replace('<p style="text-align: justify;">	<br></p>', '').replace('<p style="text-align: justify;"> <b>', '<p style="text-align: justify;">').replace('<p style="text-align: center;"></p>', '').replace('<p style="text-align: center;"><b></b></p>', '').replace('<p style="text-align: center;"><b></b>', ''),
            "publ_date": row[5],
            "number": '',
        }
        npa = Npa(params, config)
        npa_list.append(npa)
        # # Получение медиафайлов из таблицы
        files_from_table, empty_npa = npa.get_npafile_from_table(db_local)
        # Добавление проблемных НПА
        null_npa.extend(empty_npa)
        # Замена ссылок и записывание в атрибут файлы НПА
        files_from_text = npa.get_npafile_from_body(NpaFile)
        # Замена ссылок на файлы
        # files_from_text = npa.update_body(NpaFile)

        # # Удаление ссылок на страницы
        npa.delete_links()
        # # Обработка основного изображения
        # # index_image_file = get_index_file(config, npa)
        row = {
                'structure':        npa.structure,
                'title':            npa.title,
                'text':             re.sub(r'[\n]{2,3}', r'', npa.body),
                'classification':   npa.classification,
                "publ_date":        npa.date_publication.strftime("%d.%m.%Y %H:%M:%S"),
                "date":             npa.date.strftime("%d.%m.%Y %H:%M:%S"),
                "number":           npa.number,
                'npaFiles':         npa.objFiles,
            }
        fieldnames = row.keys()
        query_list.append(row)
        # TODO сделать полное описание или разделение на отдельные списки
        npa_files.extend(files_from_text)      # Файлы из текста описания НПА
        npa_files.extend(files_from_table)     # Файлы из таблицы файлов, связанные с текущим НПА

    path_csv = get_csv_path(config, 'npa')         # Получение пути для csv
    save_csv(path_csv, fieldnames, query_list)      # Сохранение словаря в csv

    # Копирование файлов
    for file in npa_files:
        print(file.new_link)
        file.copy_file()
    # TODO
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
        "imchel74",
    ]
    for site in sites:
        # Получение конфигурации
        config = get_config(site)
        # Перенос НПА
        transfer_npa(config)


if __name__ == "__main__":
    main()
