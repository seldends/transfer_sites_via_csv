from utils.util import time_test, get_config, connection, get_report_path, save_report


# Перенос Новостей
def scanning_site(config):
    db_local = connection(config)           # Объект подключения к бд
    report_news = db_local.news_info()      # Получение данных для отчета новостей
    report_npa = db_local.npa_info()        # Получение данных для отчета НПА

    path = get_report_path(config)          # Получение пути для файла отчетов
    save_report(path, report_news)          # Сохранение отчета новостяй
    save_report(path, report_npa)           # Сохранение отчета НПА


@time_test
def main():
    # Список конфигураций сайтов
    sites = [
        # "szn74",
        "pravmin74",
        # "imchel74",
    ]
    for site in sites:
        # Получение конфигурации
        config = get_config(site)
        # Перенос Новостей
        scanning_site(config)


if __name__ == "__main__":
    main()
