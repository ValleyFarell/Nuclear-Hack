from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

# Клавиатура для админов
admin_kb = ReplyKeyboardMarkup(keyboard=[
    [KeyboardButton(text='Создать опрос')],
    [KeyboardButton(text='Получить результат')],
    [KeyboardButton(text='Получить результат тестового опроса')]
], resize_keyboard=True)

# Клавиатура для сотрудников
employee_kb = ReplyKeyboardMarkup(keyboard=[
    [KeyboardButton(text='Готов ответить')]
], resize_keyboard=True)

# Кнопка для ответа на опрос
answer_kb = ReplyKeyboardMarkup(keyboard=[
    [KeyboardButton(text='Готов ответить')]
], resize_keyboard=True)
