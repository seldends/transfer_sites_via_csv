import re
from utils import time_test, get_config, get_csv_path, save_csv
from csv_objects import Auction, AuctionFile
from utils_db_local import DatabaseBitrix as Database


# Перенос НПА
def transfer_auction(config):
    auction_list = []
    filenames = []
    auction_files = []
    files_from_text = []
    files_from_table = []
    null_auction = []
    query_list = []

    db_type_local = config["db_type"]
    db_name_local = config["db_name"]

    db_local = Database(db_type_local, db_name_local)       # Объект подключения к бд со старыми данными

    auction_types = list(config["auction_type"].keys())
    data = db_local.get_auction_list(auction_types)                 # Получение списка НПА из старой таблицы
    for row in data:
        params = {
            "old_id":           row[0],
            "structure":        config["auction_type"][row[1]],
            "title":            row[2],
            "date":             row[3],
            "body":             str(row[4]).replace("^", "#").replace("\r", "").replace("\n", "").replace('<p style="text-align: justify;"></p>', '').replace('<p style="text-align: justify;">	 &nbsp;</p>', '').replace('<p style="text-align: justify;">	<br></p>', '').replace('<p style="text-align: justify;"> <b>', '<p style="text-align: justify;">').replace('<p style="text-align: center;"></p>', '').replace('<p style="text-align: center;"><b></b></p>', '').replace('<p style="text-align: center;"><b></b>', ''),
            "publ_date":        row[5],
            "linkTorg":         '',
            "linkMap":          '',
            "linkUTP":          '',
            "numberUTP":        '',
            "expirationDate":   row[5],
            "tradingDate":      row[5],
        }
        auction = Auction(params, config)
        auction_list.append(auction)
        # # Получение медиафайлов из таблицы
        files_from_table, empty_auction = auction.get_auctionfile_from_table(db_local)
        # Атрибуты УТП
        auction.bitrix_get_utp_from_body()
        # Добавление проблемных НПА
        null_auction.extend(empty_auction)
        # Замена ссылок и записывание в атрибут файлы НПА
        files_from_text = auction.get_auctionfile_from_body(AuctionFile)
        # Замена ссылок на файлы
        # files_from_text = auction.update_body(auctionFile)

        # # Удаление ссылок на страницы
        auction.delete_links()
        # # Обработка основного изображения
        # # index_image_file = get_index_file(config, auction)
        row = {
                'category':         auction.structure,
                'title':            auction.title,
                "publ_date":        auction.date_publication.strftime("%d.%m.%Y %H:%M:%S"),
                "expirationDate":   auction.date_expiration.strftime("%d.%m.%Y %H:%M:%S"),
                "tradingDate":      auction.date_trading.strftime("%d.%m.%Y %H:%M:%S"),
                'text':             re.sub(r'[\n]{2,3}', r'', auction.body),
                "linkTorg":         auction.linkTorg,
                "linkMap":          auction.linkMap,
                "linkUTP":          auction.linkUTP,
                "numberUTP":        auction.numberUTP,
                'classification':   auction.classification,
                'auctionFiles':     auction.objFiles,
            }
        fieldnames = row.keys()
        query_list.append(row)
        # TODO сделать полное описание или разделение на отдельные списки
        auction_files.extend(files_from_text)      # Файлы из текста описания НПА
        auction_files.extend(files_from_table)     # Файлы из таблицы файлов, связанные с текущим НПА

    path_csv = get_csv_path(config, 'auction')         # Получение пути для csv
    save_csv(path_csv, fieldnames, query_list)      # Сохранение словаря в csv

    # Копирование файлов
    for file in auction_files:
        print(file.new_link)
        file.copy_file()
    # TODO
    print(f'Количество пустых НПА : {len(null_auction)}')
    print(f'Количество НПА : {len(auction_list)}')
    print(f'Количество файлов НПА из таблицы : {len(files_from_table)}')
    print(f'Количество файлов НПА из текста НПА : {len(files_from_text)}')
    print(f'Количество файлов НПА общее : {len(auction_files)}')
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
        transfer_auction(config)


if __name__ == "__main__":
    main()
