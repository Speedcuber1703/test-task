import requests
from typing import List, Dict, Union
import os
from datetime import datetime

TODOS_URL = "https://json.medrocket.ru/todos"
USERS_URL = "https://json.medrocket.ru/users"
TASKS_DIR = os.path.join(os.getcwd(), "tasks")


def create_file(name: str, username: str, email: str, company_name: str,
                user_current_tasks: List[str], user_completed_tasks: List[str]) -> None:
    file_path = os.path.join(TASKS_DIR, f"{username}.txt")

    if os.path.exists(file_path):
        os.rename(file_path, os.path.join(
            TASKS_DIR, f"old_{username}_{datetime.now().strftime('%Y-%m-%dT%H:%M')}.txt"))

    current_tasks = "\n-".join(user_current_tasks)
    completed_tasks = "\n-".join(user_completed_tasks)

    data = f"# Отчёт для {company_name}.\
        \n{name} <{email}> {datetime.now().strftime('%d.%m.%Y %H:%M')} \
        \nВсего задач: {len(user_current_tasks) + len(user_completed_tasks)}"

    data += f"\n \
        \n## Актуальные задачи ({len(user_current_tasks)}): \
        \n-{current_tasks} \
        \n \
        \n## Завершённые задачи ({len(user_completed_tasks)}): \
        \n-{completed_tasks}" if len(user_completed_tasks) + len(user_current_tasks) > 0 else ""

    with open(os.path.join(TASKS_DIR, f"{username}.txt"), "w", encoding="utf-8") as file:
        file.write(data)


def formated_title_task(title: str) -> str:
    if len(title) > 46:
        title = f"{title[:46]}..."

    return title


def processing_user_data(user_data: Dict[Union[str, id], Union[str, Dict[str, str]]],
                         todos_data: Dict[str, Union[int, str, bool]]) -> None:
    id = user_data.get("id")
    name = user_data.get("name")
    username = user_data.get("username")
    email = user_data.get("email")
    company_name = user_data["company"].get("name")

    values = [id, name, username, email, company_name]
    for value in values:
        if value is None:
            print(f"[-] Недостаточно данных для составления отчёта. Набор данных: {values}")

    user_completed_tasks: List[str] = []
    user_current_tasks: List[str] = []

    for task in todos_data:
        if task.get("userId") == id:
            if task.get("completed"):
                user_completed_tasks.append(
                    formated_title_task(task.get("title")))
            else:
                user_current_tasks.append(
                    formated_title_task(task.get("title")))

    create_file(name, username, email, company_name, user_current_tasks,
                user_completed_tasks)


def main():
    todos_response = requests.get(TODOS_URL)
    users_response = requests.get(USERS_URL)

    if (todos_response.status_code != 200 or users_response.status_code != 200):
        print(f"Произошла ошибка при запросе данных!\
            \nКод статуса запроса задач: {todos_response.status_code}\
            \nКод статуса запроса пользователей: {users_response.status_code}")
    else:
        todos_data: List[Dict[str, Union[int, str, bool]]
                         ] = todos_response.json()
        users_data: List[Dict[Union[str, id],
                              Union[str, Dict[str, str]]]] = users_response.json()

        if not os.path.exists(TASKS_DIR):
            os.makedirs(TASKS_DIR)

        for user_data in users_data:
            processing_user_data(user_data, todos_data)


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print("Возникла ошибка!")
        print(e)
