import requests
from typing import List, Dict, Union
import os
from datetime import datetime


class User:
    def __init__(self, id: int, name: str, username: str, email: str, company_name: str) -> None:
        self.id = id
        self.name = name
        self.username = username
        self.email = email
        self.company_name = company_name

        self.completed_tasks: List[Dict[str, Union[int, str, bool]]] = []
        self.current_tasks: List[Dict[str, Union[int, str, bool]]] = []

    def _formated_task(self, task: Dict[str, Union[int, str, bool]]) -> Dict[str, int | str | bool]:
        if len(task.get("title")) > 46:
            task["title"] = f"{task['title'][:46]}..."

        return task

    def add_task(self, task: Dict[str, Union[int, str, bool]]) -> None:
        task = self._formated_task(task)
        self.completed_tasks.append(task) if task.get("completed") else self.current_tasks.append(task)

    def total_tasks(self) -> int:
        return len(self.completed_tasks) + len(self.current_tasks)

    def total_current_tasks(self) -> int:
        return len(self.current_tasks)

    def total_completed_tasks(self) -> int:
        return len(self.completed_tasks)

    def completed_task_titles(self) -> list[int | str | bool | None]:
        return [task.get("title") for task in self.completed_tasks]

    def current_task_titles(self) -> list[int | str | bool | None]:
        return [task.get("title") for task in self.current_tasks]


TODOS_URL = "https://json.medrocket.ru/todos"
USERS_URL = "https://json.medrocket.ru/users"
TASKS_DIR = os.path.join(os.getcwd(), "tasks")


def create_users(users_data: List[Dict[Union[str, id], Union[str, Dict[str, str]]]], todos_data: List[Dict[str, Union[int, str, bool]]]) -> list[User]:
    users: List[User] = []

    for user_data in users_data:
        id = user_data.get("id")
        name = user_data.get("name")
        username = user_data.get("username")
        email = user_data.get("email")
        company_name = user_data["company"].get("name")

        values = [id, name, username, email, company_name]
        next_user_data = False
        for value in values:
            if value is None:
                print(f"[-] Недостаточно данных для составления отчёта. Набор данных: {values}")
                next_user_data = True
                break
        
        if next_user_data:
            continue

        user = User(*values)
        for task in todos_data:
            if task.get("userId") == user.id:
                user.add_task(task)

        users.append(user)

    return users


def create_files(users: List[User]):
    for user in users:
        file_path = os.path.join(TASKS_DIR, f"{user.username}.txt")

        if os.path.exists(file_path):
            os.rename(file_path, os.path.join(
                TASKS_DIR, f"old_{user.username}_{datetime.now().strftime('%Y-%m-%dT%H:%M')}.txt"))

        current_tasks = "\n-".join(user.current_task_titles())
        completed_tasks = "\n-".join(user.completed_task_titles())

        data = f"# Отчёт для {user.company_name}.\
            \n{user.name} <{user.email}> {datetime.now().strftime('%d.%m.%Y %H:%M')} \
            \nВсего задач: {user.total_tasks()}"

        if user.total_completed_tasks() > 0:
            data += f"\n \
                \n## Актуальные задачи ({user.total_current_tasks()}): \
                \n-{current_tasks} \
                \n \
                \n## Завершённые задачи ({user.total_completed_tasks()}): \
                \n-{completed_tasks}"
        else:
            print(f"[!] У пользователя {user.username} 0 задач")

        with open(os.path.join(TASKS_DIR, f"{user.username}.txt"), "w", encoding="utf-8") as file:
            file.write(data)


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

        users: List[User] = create_users(users_data, todos_data)

        if not os.path.exists(TASKS_DIR):
            os.makedirs(TASKS_DIR)

        create_files(users)


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print("Возникла ошибка!")
        print(e)