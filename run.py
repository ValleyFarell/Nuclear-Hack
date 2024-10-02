import asyncio
import logging
from aiogram import Bot, Dispatcher
from config import load_config
from app.handlers import router
from aiogram.client.session.aiohttp import AiohttpSession
import sqlite3

logger = logging.getLogger(__name__)

#Создание базы данных (примерно)
conn = sqlite3.connect('survey.db')
cursor = conn.cursor()
cursor.execute('''CREATE TABLE IF NOT EXISTS users ( 
                    user_id INTEGER PRIMARY KEY,
                    answer TEXT
                )''')
conn.commit()
conn = sqlite3.connect('survey.db')
cursor = conn.cursor()
cursor.execute('''CREATE TABLE IF NOT EXISTS admins ( 
                    tg_id_a INTEGER PRIMARY KEY
                )''')
conn.commit()
conn = sqlite3.connect('survey.db')
cursor = conn.cursor()
cursor.execute('''CREATE TABLE IF NOT EXISTS employees ( 
                    tg_id_e INTEGER PRIMARY KEY
                )''')
conn.commit()


# session = AiohttpSession(proxy='http://proxy.server:3128')
token=load_config('.env')
bot = Bot(token=load_config('.env'))
dp = Dispatcher()

async def main():
    logging.basicConfig(
        level=logging.INFO,
        format='%(filename)s:%(lineno)d #%(levelname)-8s '
               '[%(asctime)s] - %(name)s - %(message)s')

    # Выводим в консоль информацию о начале запуска бота
    logger.info('Starting bot')
    dp.include_router(router)
    await dp.start_polling(bot)

if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print('Exit')
