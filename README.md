# Решение кейса от компании МТС Линк "ИИ для анализа пользовательских ответов" методом кластеризации пользовательских ответов с последующим построением смысловых облаков на основе нейросетей-трасформеров

## Установка (Windows)

1. Клонирование репозитория 

```git clone https://github.com/OkulusDev/Oxygen.git```

2. Создание виртуального окружения

```python -m venv venv```

3. Активация виртуального окружения

```venv/Scripts/activate```

4. Установка зависимостей

```pip3 install -r requirements.txt```

## Настройка бота

1. Создаем бота с помощью https://t.me/BotFather

2. Создать файл .env со следующий содержимым

   ![image](https://github.com/user-attachments/assets/6789273f-6499-4820-a94b-60414ebb89a5)

3. Запуск бота

```python run.py```
## Инструкция

В функционал админов бота входит:
1. Рассылка опроса по сотрудникам компании, id которых лежат в базе данных
2. Получение краткой выжимки ответов сотрудников на поставленный в опросе вопрос в виде таблицы и рисунка(см. рис)
   ![image](https://github.com/user-attachments/assets/ea68d8cf-aaa1-436d-8c6c-f5436a059afd)
   ![image](https://github.com/user-attachments/assets/a3c16777-2e24-4f31-8ceb-4f7af604762f)

   
## В свою очередь, функционал пользователей состоить лишь из 1 действия - ответить на вопроса(см. рис)


   ![image](https://github.com/user-attachments/assets/dc62618d-3851-49f7-b865-1d76e14786d0)
   ![image](https://github.com/user-attachments/assets/d4f1f098-1e9c-4436-bb39-a2c42f2e4c22)


### Ссылка на базовое решение с подробным объяснением в Google Colab(немного отличается от финального, но суть та же)
https://colab.research.google.com/drive/12AEfG43BqIJdrjB_GGbzmXGNJkGhjmW8
