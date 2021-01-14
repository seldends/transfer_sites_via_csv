# Скрипты для переноса объектов из старых систем в Sitex

# Установка
На платформе Genum в качестве СУБД используется PostgreSQL.

На платформах Sinta, Bitrix в качестве СУБД используется MariaDB.

Разворачивание бэкапов:
| СУБД          | Linux                                                           | Windows                                                                   |
| ------------- | --------------------------------------------------------------- | ------------------------------------------------------------------------- |
| PostgreSQL    | `psql -U <username> -d <dbname> -q -f path/to/<backupname>.sql` | `psql.exe -U <username> -d <dbname> -q -f C:\\path\\to\\<backupname>.sql` |
| MariaDB/MySQL | `mysql -u <username> -p <dbname> < /path/to/<backupname>.sql`   | `mysql -u <username> -p <dbname> < C:\path\to\<backupname>.sql`           |

# Алгоритм работы
1. Разворачивание бэкапа.
   1. Создать пустую бд `<dbname>` в соответствующей СУБД в зависимости от типа старой системы
   2. Развернуть бэкап в `<dbname>`
2. Создать кофигурацию для сайта в файле `config.yml`
3. Запустить скрипт scan.py для сохрарения отчета по категориям/типам новостей и НПА для системы генум
4. Дополнить конфигурацию исходя из отчета, сопоставить старые и новые категории
5. Запустить скрипт для переноса нужныъ объектов (`csv_news.py` , `csv_npa.py`)
6. Проверить все ли ссылки на файлы и страницы обратолись, доработать регулярки если не все
7. Проверить csv в excel
8. Испортировать csv на тестовом контуре, проверить объекты
9. Испортировать csv на продуктивном контуре, проверить объекты


# Примечания

1. В ссылках на файлы делается замена `^` на `#` , может возникнуть проблема что файла не будет по измененному пути и нужно будет переименовать путь\файл.
## Sinta

| Содержимое                    | Таблица                            |
| ----------------------------- | ---------------------------------- |
| Базовая информация об объекте | `node`                             |
| Связь сущностей и таблиц      | `field_config_instance`            |
| Содержимое объекта (тело)     | `field_data_body`                  |
| Резюме                        | `field_data_field_teaser`          |
| Связь категорий и новостей    | `field_data_field_news_cat`        |
| Файлы прикрепленные к новости | `field_data_field_gallery`         |
| Картинки                      | `field_data_field_image`           |
| Файлы                         | `file_managed`                     |
| НПА, связь НПА и категорий    | `field_data_field_legal_acts`      |
| Связь НПА и даты принятия     | `field_data_field_npa_accept_date` |
| Связь НПА и номера            | `field_data_field_npa_number`      |


### Параметры новости:

| Поле             | Таблица и поле                                 |
| ---------------- | ---------------------------------------------- |
| Идентификатор    | `node.nid`                                     |
| Название новости | `node.title`                                   |
| Текст новости    | `field_data_body.body_value`                   |
| Путь до картинки | `file_managed.uri`                             |
| Дата создания    | `node.created`                                 |
| Дата изменения   | `node.changed`                                 |
| Дата публикации  |                                                |
| Структура        | `field_data_field_news_cat.field_news_cat_tid` |
| Резюме новости   | `field_data_field_teaser.field_teaser_value`   |

## Genum

| Сущность           | Таблица                    |
| ------------------ | -------------------------- |
| Новости            | `sd4_PublicationItem`      |
| Медиа-Файлы        | `sd4_PublicationItemImage` |
| Структура новостей | `sd4_PublicationGroup`     |

### Параметры новости:

| Поле                           | Таблица и поле                        |
| ------------------------------ | ------------------------------------- |
| Идентификатор                  | `sd4_PublicationItem.id`              |
| Название новости               | `sd4_PublicationItem.Title`           |
| Текст статьи с HTML            | `sd4_PublicationItem.Article`         |
| Дата публикации                | `sd4_PublicationItem.PublicationDate` |
| Путь до картинки               | `sd4_PublicationItem.Image`           |
| Скрыта ли новость\опубликована | `sd4_PublicationItem.IsHidden`        |
| Дата создания                  | `sd4_PublicationItem.CreationDate`    |
| Публиковать на главной         | `sd4_PublicationItem.OnMain`          |
| Структура                      | `sd4_PublicationItem.Group-id`        |
| Резюме новости                 | `sd4_PublicationItem.Summary`         |
| Важное                         |                                       |

### Параметры медиа-файлов:

| Поле                               | Таблица и поле                     |
| ---------------------------------- | ---------------------------------- |
| Идентификатор                      | `sd4_PublicationItemImage.id`      |
| Ссылка на файл                     | `sd4_PublicationItemImage.Image`   |
| Новость в которой опубликован файл | `sd4_PublicationItemImage.Item_id` |
| Описание                           | `sd4_PublicationItemImage.Title`   |