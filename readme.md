## Тестовое задание в отдел аналитики на место back-end разработчика на Python

## Проблема
У нас есть несколько отдельных проектов, которым требуется использовать информацию о научной деятельности сотрудников. Многие из этих проектов так или иначе хотят взаимодействовать с информацией, которую предоставляют наукометрические базы данных, такие как Scopus, WOS, РИНЦ. 
Мы пришли к выводу, что необходимо централизовать работу с профилями авторов из наукометрических баз данных и вынести ёе в отдельный сервис.

## Задача
Необходимо реализовать микросервис для работы с наукометрическими профилями пользователей (добавление нового профиля пользователя, получение списка профилей и отдельного профиля пользователя, подсчет статистики по публикационной активности авторов). Сервис должен предоставлять HTTP API и принимать/отдавать запросы/ответы в формате JSON.

## Решение
* Язык программирования Python 3.10.
* Использовался FastAPI.
* Реляционная СУБД: PostgreSQL. (Но так же есть ветка sqlite version. Её легче тестить и там уже лежит БД с записями)
* Для миграций использовал alembic.
* В общем код соответствовать PEP. Есть несоответсвия только по необходимости, например, в частичном дублировании названий для функций автотестов, для лучшего понимания их смысла.
* Весь код выложен на GitHub в данный репозиторий.
* Ниже описана инструкция для запуска проекта.
* Реализовано 5 методов: получение списка профилей авторов, получение одного профиля, создание профиля автора, получение статистики по публикациям авторов, удаление записи (добавил чтобы стереть запись, которая добавляется в автотестах);
* Для всех полей из раздела детали, добавлена валидация через regex.

## Порядок запуска

### Запуск проекта
* Клонируем проект
```
git clone https://github.com/lShoichil/Analytics-Sector-backend-task
```
* Создадим изориованную среду
```
py -m venv venv
```
* Заходим в изориованную среду
```
./venv/Scripts/activate
```
* Устанавливаем все необхдимые зависимости
```
pip install -r requirements.txt
```
* Запуск сервиса (Желательно после создания БД)
```
uvicorn knowledge.main:app --reload
```
* Советую использовать для тестирования внутреннюю документацию FastAPI. (http://127.0.0.1:8000/docs)

### Создание БД
Можно поднять как вам удобнее, через docker или локально, я поднимал локально.
* Создаём БД (Создавал ручками через pgAdmin 4)
* Нужно её подвизать к проекту, для этого нужно заменить строку в файле /core/database.py и ввести свои данные
```
SQLALCHEMY_DATABASE_URL = "postgresql://USER:PASSWORD@localhost/NAME_DB"
```
* Провести миграции и убедиться, что БД подвязалась с помощью alembic
```
alembic revision --autogenerate -m 'test_connection'
```
* Проверить это можно, зайдя в последний создавшийся файл в папке /migrations/version. Если там прописана модель, то это успех.
* Добавить миграция на всякий случай в head
```
alembic upgrade head
```

## Детали решения

### Структура БД
* ID - уникальный для каждой записи.
* guid - уникальный UUID идентификатор научного сотрудника.
* full_name - ФИО научного сотрудника.
* scientometric_database - источник данных (Scopus, WOS, RISC).
* document_count - количество публикаций автора, проиндексированных источником.
* citation_count - количество цитирований автора.
* h_index - индекс Хирша, рассчитанный НБД.
* url - ссылка на профиль автора в НБД.
* created_date - дата создания записи в бд, нужна для сортировки.

### Метод получения списка профилей
* Фильтрация: обязательный параметр - наукометрическая база данных.
  * Есть проверка на принадлежность в НБД.
* Пагинация: можно выбрать какую страницу вам открыть и сколько записей на одной странице вы хотите видеть.
  * page - номер страницы.
  * size - выбор кол-ва записей на 1 странице.
* Сортировки: по индексу Хирша (возрастание/убывание) и по дате создания в БД (возрастание/убывание).
  * Являются двумя необязательными параметрами (sort_h, sort_date).
  * Добавив оба будет ошибка.
  * Требуется выбрать один и выбрать True или False (убывание/возрастание)
* Поля в ответе: ФИО автора, индекс Хирша, ссылка на профиль в НБД.

### Метод получения профиля сотрудника
* Обязательные параметры - уникальный идентификатор сотрудника, внутренний ID в базе данных (по ТЗ нужно было по НБД, а не по ID, но я невнимательно прочёл :с ).
* Обязательные поля в ответе: ФИО автора, индекс Хирша, ссылка на профиль в НБД;
* Опциональные поля (можно запросить, передав параметр fields): количество цитирований, количество публикаций.

### Метод создания профиля автора:
* Принимает все вышеперечисленные поля, кроме внутреннего ID и даты создания: идентификатор сотрудника, ФИО автора, индекс Хирша, количество цитирований, количество публикаций, ссылка на профиль в НБД;
* Возвращает внутренний ID созданного профиля и код результата (404 и описание ошибки или 200).
  * Здесь очень высока вероятность словить ошибку на postgresql, если вы добавляли не запросами, а через БД сами. У него есть внутренний счётчик ID, который работает странно (из-за чего могут упасть автотесты, я об этом расписал в конце) который будет пытаться добавить запись с ID = 1, даже если у вас уже 30 записей и будет выдавать ошибку, ведь ID = 1 уже занят. Решение - пробить запрос кучу раз и ждать пока счётчик добежит. Мне помогло. Но происходит только в случае если вы сами вставляли записи в БД (Я это сделал в TablePlus, чтобы проверить пагинацию).

### Метод удаления профиля автора:
* Принимает идентификатор сотрудника и внутренний ID;
* Возвращает сообщение об успехе, либо код и описание ошибки.

### Метод подсчета статистики публикационной активности
* Обязательная группировка: по наукометрической базе данных.
  * Если не будет соответствовать одной из трёх НБД, то будт соответствующая ошибка.
  * Если всё хорошо, то всё будет подсчитано и выведено. Считал через orm.
* Поля, которые выведутся: 
  * общее количество публикаций - sum_documents
  * цитирований всех авторов - sum_citations
  * средний индекс Хирша авторов - h_average

### Валидация полей
При получении невалидных полей в качестве параметров ожидается выводется лог ошибки 422, где будет написан regex, которому нужно соответсвовать
* Количество публикаций, количество цитирований, индекс Хирша >= 0
* Ссылка на профиль в НБД - валидный URL
* Валидация ФИО
* Валидация значений наукометрических БД - Scopus, WOS, RISC 

### Дополнительные выполненные задачи
* Документация с описанием работы API сервиса прописывается сама и находится по пути localhost/docs, т.к. это FastAPI
* Методы API содержат описания ошибок и статус коды при их возникновении.
* Написал автотесты. Для запуска, необходимо использовать команду находясь Analytics-Sector-backend-task:
```
pytest
```

## Минусы моего решения, которые можно улучшить
Не успел исправить/добавить к 20:00 7-го числа.

### Автотесты
* Писал первый раз, и посчитал что удобно заранее завести глобальные переменные для создания записей. Но отсюда вытикает проблем, которая возникает при использовании postgresql. Он не повторяет один и тот же id, т.е. при добавлении и удалении в бд sqlite я всегда знал что последняя запись тестовая ВСЕГДА с id 31. В postgresql это не так и он никогда не повторится, следовательно проблема моей версии: 
  * Нужно заранее знать id следующей создаваемой записи и если указать его не правильно, то тесты лягут из-за не уникальности id (поэтому лучше тестить на ветке с sqlite, там и бд создавать не надо)

* Нет проверок на качество сортировки. Я проверяю, что мне пришёл правильный json, но не проверяю, что:
  * items не пустой
  * объекты items и правда отсортированы по одному из параметром (хотя я сортирую через orm и там не должно быть проблем)

### БД
* Переделать структуру БД. Она соответсвует ТЗ, но в идеале нужно разделить людей и публикации и связать через foreign key.

### Docker
* Добавить докер образ, чтобы быстро развернуть проект и не мучиться тоже было бы здорово.

### JWT
* Добавить авторизацию. С добавлением отдельной БД пользователей, нужно будет добавить авторизацию.

### CI/CD
* Нужно настроить CI/CD. Это в целом удобно и круто и нет причин его не добавлять. В прошлый раз делал это через GitHub. Удобно.)
* Так же мне понравилось использовать Jenkins, в частности встроить в него SonarQube и видеть ВСЕ свои ошибки безопасти и потенциально вредоносный код в отчёте после каждого commit.
