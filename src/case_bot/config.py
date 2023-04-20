import os
import telebot
from dotenv import load_dotenv

load_dotenv()

dbname = os.getenv("db_name")
user = os.getenv("db_user")
password = os.getenv("db_password")
host = os.getenv("db_host")

bot_token = os.getenv("bot_token")
cur_apikey = os.getenv("cur_apikey")