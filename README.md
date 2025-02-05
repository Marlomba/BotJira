# Jira-Telegram Bot

This project is a Telegram bot designed to interact with Jira, retrieve issue information, and send notifications to a Telegram chat.

## Project Structure

The project structure is as follows:

```bash
bot2prac/
├── .venv/                    # Virtual environment for the project
│   ├── Lib/
│   │   └── ...               # Python libraries for the project
│   │   └── Scripts/
│   └── ...                   # Virtual environment scripts
├── .gitignore                # File for ignoring files in Git (e.g., .venv)
├── pyvenv.cfg                # Virtual environment configuration file
├── botjira.py                # Main Python file with the bot's code
└── README.md                 # This file with the project description
```

## Как использовать
Установите Необходимые библиотеки:

pip install pyTelegramBotAPI requests jira urllib3

Запустите бота:

python botjira.py

Бот запустится и начнёт отслеживать изменения в Jira. Затем он будет отправлять уведомления в настроенный чат Telegram.

## Конфигурация
Настройте следующие параметры в botjira.py файл:

Токен Telegram-Бота:

Замените заполнитель вашим реальным токеном Telegram-бота:

TELEGRAM_BOT_TOKEN = 'YOUR_TELEGRAM_BOT_TOKEN'

Идентификатор чата Telegram:

Задайте CHAT_ID идентификатор чата Telegram, в который вы хотите получать уведомления:

CHAT_ID = 'YOUR_TELEGRAM_CHAT_ID'


Сведения о сервере Jira:

Настройте адрес сервера Jira, имя пользователя и пароль (или токен API):

JIRA_SERVER = 'https://jira.example.com'
JIRA_USER = 'your_jira_username'
JIRA_PASSWORD = 'your_jira_password'  # Or use JIRA_API_TOKEN


## Важное примечание по безопасности: хотя для базовой аутентификации можно использовать имя пользователя и пароль, настоятельно рекомендуется использовать токен Jira API для большей безопасности. Если вы не можете использовать токен API, проконсультируйтесь с администратором Jira, чтобы выбрать наиболее подходящий способ аутентификации.

Статус Jira для отслеживания:

Укажите статус Jira, который должен отслеживать бот. Убедитесь, что название статуса совпадает с точным значением, используемым в вашем экземпляре Jira (с учетом регистра):

STATUS_NAME_TO_TRACK = "In Progress" #Example

Or use Status ID:

STATUS_ID_TO_TRACK = "3" #Example

