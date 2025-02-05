import requests
import logging
import json
import time
from requests.auth import HTTPBasicAuth
from jira import JIRA
import urllib3
urllib3.disable_warnings()

# Настройки Jira
JIRA_SERVER = 'https://jira.marlomba.ru'
JIRA_USER = 'admin'  # Your Jira username
JIRA_PASSWORD = 'GjvjomLheuf$337' # Your Jira password

# Настройки Telegram
TELEGRAM_BOT_TOKEN = '8139941261:AAG6UnImy3xu-trwphGSnRFqWVmEGfH-B9U'
CHAT_ID = '-4728891235'
TELEGRAM_API_URL = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}"

# Название статуса "В работе" (From API)
STATUS_ID_TO_TRACK = "3"   # The status ID from the API
STATUS_NAME_TO_TRACK = "В работе" # And name

# Логирование
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.DEBUG)

# Глобальная переменная для хранения ID задач
processed_issues = set()
processed_sprints = set() # Keep track of processed sprints to avoid duplicate notifications


def get_jira_issues():
    """Gets a list of issues using the jira-python library."""
    try:
        options = {
            'verify': False,  # Отключаем проверку SSL-сертификата
        }

        jira = JIRA(
            server=JIRA_SERVER,
            basic_auth=(JIRA_USER, JIRA_PASSWORD),  # Use basic authentication
            options=options
        )

        #jql_query = f'project = PR AND status = "{STATUS_NAME_TO_TRACK}"'  # Use STATUS NAME  - Old query
        jql_query = f'project = PR AND status = {STATUS_ID_TO_TRACK}'  # Use STATUS ID!!!
        issues = jira.search_issues(jql_query, maxResults=100)

        issue_list = []
        for issue in issues:
            issue_list.append({
                'project': issue.fields.project.name,
                'key': issue.key,
                'status': issue.fields.status.name
            })

        return issue_list

    except Exception as e:
        logging.exception(f"Error using jira-python library: {e}")
        return []


def send_telegram_notification(issue_data):
    """Отправляет уведомление в Telegram."""
    project_name = issue_data.get('project')
    issue_key = issue_data.get('key')
    status_name = issue_data.get('status')

    message = f"✅ Новая задача в проекте {project_name}:\n\n" \
              f"**{issue_key}**: Статус - {status_name}\n" \
              f"[Открыть в Jira]({JIRA_SERVER}/browse/{issue_key})"

    params = {
        'chat_id': CHAT_ID,
        'text': message,
        'parse_mode': 'Markdown'
    }

    try:
        response = requests.post(f"{TELEGRAM_API_URL}/sendMessage", params=params)
        response.raise_for_status()
        logging.info(f"Уведомление отправлено в Telegram: {response.json()}")
    except requests.exceptions.RequestException as e:
        logging.exception(f"Ошибка при отправке уведомления в Telegram: {e}")

def get_all_boards():
    """Retrieves all agile boards from Jira."""
    try:
        options = {'verify': False}
        jira = JIRA(server=JIRA_SERVER, basic_auth=(JIRA_USER, JIRA_PASSWORD), options=options)
        boards = jira.boards()
        return boards
    except Exception as e:
        logging.exception(f"Error getting boards: {e}")
        return []

def get_sprints_for_board(board_id, jira):
    """Retrieves all sprints for a given board ID."""
    try:
        sprints = jira.sprints(board_id, maxResults=50, state="active,future")  # Get active and future sprints
        return sprints
    except Exception as e:
        logging.exception(f"Error getting sprints for board {board_id}: {e}")
        return []


def send_telegram_sprint_notification(sprint_data):
    """Sends a Telegram notification for a newly created sprint."""
    sprint_name = sprint_data.get('name')
    sprint_startDate = sprint_data.get('startDate')
    sprint_endDate = sprint_data.get('endDate')
    message = f"🚀 Новый спринт создан!\n\n" \
              f"**{sprint_name}**\n" \
              f"Дата начала: {sprint_startDate}\n" \
              f"Дата окончания: {sprint_endDate}\n" \
              f"[Открыть спринт в Jira]({JIRA_SERVER}/secure/RapidBoard.jspa?rapidView=4&sprint={sprint_data.get('id')})"  #4 - id boards

    params = {
        'chat_id': CHAT_ID,
        'text': message,
        'parse_mode': 'Markdown'
    }

    try:
        response = requests.post(f"{TELEGRAM_API_URL}/sendMessage", params=params)
        response.raise_for_status()
        logging.info(f"Уведомление о спринте отправлено в Telegram: {response.json()}")
    except requests.exceptions.RequestException as e:
        logging.exception(f"Ошибка при отправке уведомления о спринте в Telegram: {e}")

def check_and_notify_sprints():
    """Checks for new sprints and sends notifications."""
    global processed_sprints
    try:
        options = {'verify': False}
        jira = JIRA(server=JIRA_SERVER, basic_auth=(JIRA_USER, JIRA_PASSWORD), options=options)
        boards = get_all_boards()

        for board in boards:
            sprints = get_sprints_for_board(board.id, jira)  # Pass the JIRA instance to the function
            for sprint in sprints:
                if sprint.id not in processed_sprints:
                    logging.info(f"Обнаружен новый спринт: {sprint.name}")
                    sprint_data = {
                        'id': sprint.id,
                        'name': sprint.name,
                        'startDate': sprint.startDate,
                        'endDate': sprint.endDate
                    }
                    send_telegram_sprint_notification(sprint_data)
                    processed_sprints.add(sprint.id)
                else:
                     logging.debug(f"Спринт {sprint.name} уже обработан.")

    except Exception as e:
        logging.exception(f"Ошибка при проверке и уведомлении о спринтах: {e}")


def check_and_notify():
    """Проверяет задачи и отправляет уведомления."""
    logging.debug("Запущен цикл проверки задач")
    global processed_issues
    while True:
        try:
            issues = get_jira_issues()
            logging.debug(f"Получено от Jira {len(issues)} задач")
            logging.debug(f"Уже обработанные задачи: {processed_issues}")

            for issue in issues:
                issue_key = issue.get('key')
                if issue_key and issue_key not in processed_issues:
                    logging.info(f"Обрабатывается задача {issue_key}")
                    send_telegram_notification(issue)
                    processed_issues.add(issue_key)
                else:
                     if issue_key:
                        logging.debug(f"Задача {issue_key} уже обработана или не имеет ключа.")
            check_and_notify_sprints() # Check for new sprints on each iteration
        except Exception as e:
            logging.exception(f"Произошла непредвиденная ошибка: {e}")

        logging.debug("Конец цикла while в check_and_notify")
        time.sleep(60)


def main():
    """Запускает бота."""
    logging.info("Бот запущен")
    check_and_notify()


if __name__ == '__main__':
    main()