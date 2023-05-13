# tg_case_bot
 __Telegram Case Bot__ — это телеграм чат-бат для анализа рынка [*Steam Community Market*](https://steamcommunity.com/market/). Бот позволяет отслеживать состояние инвестиций и добавлять, удалять, и редактировать уже имеющиеся активности.

![12](https://img.shields.io/github/pipenv/locked/python-version/TriNitki/tg_case_bot?logo=python) ![12](https://img.shields.io/github/pipenv/locked/dependency-version/TriNitki/tg_case_bot/pytelegrambotapi?label=Telebot&logo=telegram) ![12](https://img.shields.io/badge/PostgreSQL-15.2-red/?color=blue&logo=postgresql&logoColor=white)


## Установка

+ Клонирование репозитория: 
```
$ git clone https://github.com/TriNitki/tg_case_bot
```
+ Установка необходимых пакетов: 
```
pip install -r requirements.txt
```
+ Добавление переменных окружения:
```
bot_token="..."
cur_apikey="..."

db_name="..."
db_user="..."
db_password="..."
db_host="..."
```
+ Запуск чат-бота:
```
python .\src\case_bot\main.py
```
