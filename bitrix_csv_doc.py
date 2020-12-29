import re
from utils.util import time_test, get_config, get_csv_path, save_csv
from core.Documents import Doc
from core.File import DocFile
from utils.Bitrix import DatabaseBitrix as Database


# Перенос НПА
def transfer_doc(config):
    doc_list = []
    filenames = []
    doc_files = []
    files_from_text = []
    files_from_table = []
    null_doc = []
    query_list = []

    db_type_local = config["db_type"]
    db_name_local = config["db_name"]

    db_local = Database(db_type_local, db_name_local)       # Объект подключения к бд со старыми данными

    doc_types = list(config["doc_type"].keys())
    data = db_local.get_obj_list(doc_types)                 # Получение списка НПА из старой таблицы
    for row in data:
        params = {
            "old_id":       row[0],
            "structure":    config["doc_type"][row[1]],
            "title":        row[2],
            "date":         row[3],
            "body":         row[4],
            "publ_date":    row[5],
            "number":       '',
        }
        doc = Doc(params, config)
        doc_list.append(doc)

        # Получение медиафайлов из таблицы
        files_raw = db_local.get_doc_files_list(doc.old_id)
        files_from_table, empty_doc = doc.get_files_from_table(files_raw, DocFile)
        # Добавление проблемных НПА
        null_doc.extend(empty_doc)
        # Замена ссылок и записывание в атрибут файлы НПА
        doc.update_files(files_from_table)
        # Файлы из текста
        files_from_text = doc.get_files_from_body(DocFile)
        # Замена ссылок на файлы из текста
        doc.replace_file_link(files_from_text)
        # # Удаление ссылок на файлы
        # doc.delete_file_links(files_from_text)
        # Удаление ссылок на страницы
        doc.delete_page_links()
        row = {
                'page':        doc.structure,
                'classification':   doc.classification,
                'title':            doc.title,
                'description':      re.sub(r'[\n]{2,3}', r'', doc.body),
                "publ_date":        doc.date_publication.strftime("%d.%m.%Y %H:%M:%S"),
                'docFiles':         doc.objFiles,
            }
        fieldnames = row.keys()
        query_list.append(row)
        # TODO сделать полное описание или разделение на отдельные списки
        doc_files.extend(files_from_text)      # Файлы из текста описания НПА
        doc_files.extend(files_from_table)     # Файлы из таблицы файлов, связанные с текущим НПА

    path_csv = get_csv_path(config, 'doc')         # Получение пути для csv
    save_csv(path_csv, fieldnames, query_list)      # Сохранение словаря в csv

    # Копирование файлов
    for file in doc_files:
        print(file.new_link)
        file.copy_file()
    # TODO
    print(f'Количество пустых НПА : {len(null_doc)}')
    print(f'Количество НПА : {len(doc_list)}')
    print(f'Количество файлов НПА из таблицы : {len(files_from_table)}')
    print(f'Количество файлов НПА из текста НПА : {len(files_from_text)}')
    print(f'Количество файлов НПА общее : {len(doc_files)}')
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
        transfer_doc(config)


if __name__ == "__main__":
    main()
