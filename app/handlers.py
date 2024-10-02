from aiogram.filters import CommandStart
from aiogram.types import Message
from aiogram import Router, F
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext
import app.keybords as kb
import sqlite3
from services.manager import *
from aiogram.methods import send_photo, send_document
from aiogram.types import FSInputFile
import pandas as pd
router = Router()

conn = sqlite3.connect('survey.db')
cursor = conn.cursor()
cursor.execute('SELECT tg_id_e FROM employees')
massive_big = cursor.fetchall()
employees = list(i[0] for i in massive_big)
cursor.execute('SELECT tg_id_a FROM admins')
massive_big = cursor.fetchall()
admins = list(i[0] for i in massive_big)

class AdminRequest(StatesGroup):
    message_text = State()

class EmployeeRequest(StatesGroup):
    waiting_for_answer = State()

# Обработка запуска бота
@router.message(CommandStart())
async def cmd_start(message: Message):
    user_id = message.from_user.id
    if user_id in admins:
        await message.reply("Добро пожаловать, админ! Выберите опцию", reply_markup=kb.admin_kb)
    else:
        info = cursor.execute(f"SELECT * FROM employees WHERE tg_id_e={user_id}")
        if info.fetchone() is None:
            cursor.execute(f"INSERT INTO employees (tg_id_e) VALUES ({user_id})")
            employees.append(user_id)
        await message.reply("Добро пожаловать, сотрудник! Выберите опцию", reply_markup=kb.employee_kb)
    conn.commit()

# =================== Админская логика ===================

# Обработка создания опроса (для админов)
@router.message(F.text == 'Создать опрос')
async def create_survey(message: Message, state: FSMContext):
    if message.from_user.id in admins:
        await state.set_state(AdminRequest.message_text)
        await message.answer("Пожалуйста, введите текст опроса")
    else:
        await message.answer("К сожалению, у вас нет прав для создания опроса")

# Сохранение опроса и отправка сотрудникам
@router.message(AdminRequest.message_text)
async def save_survey(message: Message, state: FSMContext):
    question = message.text
    await state.clear()
    conn = sqlite3.connect('survey.db')
    cursor = conn.cursor()
    if cursor.execute('SELECT COUNT(*) FROM users'):
        cursor.execute('DELETE FROM users')
    conn.commit()
    # Здесь происходит отправка опроса сотрудникам
    await message.answer(f"Опрос создан: {question}\nОпрос отправлен всем сотрудникам.")

    bot = message.bot
    for user_id in employees:
        await bot.send_message(chat_id=user_id, text=f"""Обьявлен новый опрос: {question}
                                                         
                                                         Пожалуйста, нажмите на кнопку над клавиатурой и ответьте на вопрос""", reply_markup=kb.answer_kb)

# =================== Логика сотрудников ===================

# Получение ответа от сотрудника
@router.message(F.text == 'Готов ответить')
async def ready_to_answer(message: Message, state: FSMContext):
    if message.from_user.id not in admins:  # Проверяем, что это не админ
        await state.set_state(EmployeeRequest.waiting_for_answer)
        await message.answer("Итак, введите ответ на опрос")

# Обработка и сохранение в базу данных ответа сотрудника
@router.message(EmployeeRequest.waiting_for_answer)
async def receive_answer(message: Message, state: FSMContext):
    answer = message.text
    user_id = message.from_user.id

    conn = sqlite3.connect('survey.db')
    cursor = conn.cursor()
    cursor.execute('INSERT OR REPLACE INTO users (user_id, answer) VALUES (?, ?)', (user_id, answer))
    conn.commit()
    conn.close()

    await state.clear()
    await message.answer("Спасибо за ответ! Ожидайте обратной связи!")

# =================== Получение результатов для админов ===================

@router.message(F.text == 'Получить результат')
async def get_result(message: Message):
    if message.from_user.id in admins:
        conn = sqlite3.connect('survey.db')
        cursor = conn.cursor()
        cursor.execute('SELECT answer FROM users')
        massive_big = cursor.fetchall()
        conn.close()
        reviews_list = list(i[0] for i in massive_big)
        # DataFrame таблица с ответами
        reviews_df = pd.DataFrame(reviews_list)

        # Путь к файлу, где будет храниться таблица ответов
        reviews_path = 'services/reviews/reviews.csv'

        # Путь к файлу визуализации результата опроса
        pic_path = 'services/results_pics/result.png'

        # Путь к файлу, где будет храниться таблица результата опроса
        result_path = 'services/results/result.csv'
        result_path_excel = 'services/results/result.xlsx'
        reviews_df.to_csv(reviews_path)

        # Вычисление результата
        result_df = get_result_df(csv_path=reviews_path, pic_path=pic_path)

        result_df.to_csv(result_path)

        # Пример вывода результатов
        result_df.to_excel(result_path_excel, columns=result_df.columns)
        pic_file = FSInputFile(pic_path)
        doc_file = FSInputFile(result_path_excel)

        await message.answer(f"""Результаты:""")
        await message.bot.send_photo(message.chat.id, photo=pic_file)
        await message.bot.send_document(message.chat.id, document=doc_file)
    else:
        await message.answer("К сожалению, у вас нет прав для просмотра результатов")

@router.message(F.text == 'Получить результат тестового опроса')
async def get_result_from_test(message: Message):
    if message.from_user.id in admins:

        pic_path = 'services/results_pics/result.png'
        result_path = 'services/results/result.csv'
        result_path_excel = 'services/results/result.xlsx'
        # Вычисление
        result_df = get_result_df(txt_path='services/test_reviews.txt', pic_path=pic_path)

        result_df.to_csv(result_path)
        result_df.to_excel(result_path_excel, columns=result_df.columns)
        pic_file = FSInputFile(pic_path)
        doc_file = FSInputFile(result_path_excel)
        await message.answer(f"""Результаты:""")
        await message.bot.send_photo(message.chat.id, photo=pic_file)
        await message.bot.send_document(message.chat.id, document=doc_file)
    else:
        await message.answer("К сожалению, у вас нет прав для просмотра результатов")