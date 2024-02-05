import json
from typing import TypedDict

import requests
import os
import re

PATH_TO_DB = "data/issues.txt"
BASE_URL = "https://cyberleninka.ru"


class Issue(TypedDict):
    id: int
    name: str
    year: int


def get_all_issued() -> list[Issue]:
    response = requests.get(f"{BASE_URL}/journal/n/russkiy-ornitologicheskiy-zhurnal")
    text_issues = re.findall(r"issues: \[.*\],", response.text)[0][8:-1]
    return json.loads(text_issues)


def notification_text(issue: Issue) -> list[str]:
    result = [f"*{issue['name']}*"]
    response = requests.get(f"{BASE_URL}/api/issue/{issue['id']}/articles")
    articles = response.json()
    result += [f"- [{article['name']}]({BASE_URL}{article['link']})" for article in articles]
    return result


def send_notification(bot_token: str, user_channel: str, text: list[str]) -> None:
    message = "\n".join(text).replace("-", "\\-")
    # for char in r"\_*[]()~`>#+-=|{}.!":
    #     message = message.replace(char, f"\\{char}")
    response = requests.get(
        f'https://api.telegram.org/bot{bot_token}/sendMessage?chat_id={user_channel}&text={message}&parse_mode=MarkdownV2&disable_web_page_preview=true')
    assert response.status_code == 200


def run(bot_token: str | None, user_channel: str | None):
    with open(PATH_TO_DB, "r") as src:
        handled = [key[:-1] for key in src.readlines()]

    text = []
    for issue in get_all_issued():
        key = str(issue["id"])
        if key not in handled:
            handled.append(key)
            text += notification_text(issue)

    if text and bot_token:
        send_notification(bot_token, user_channel, text)
    else:
        print(text)

    with open(PATH_TO_DB, "w") as dst:
        dst.writelines(row + "\n" for row in handled)


if __name__ == "__main__":
    run(os.environ["BOT_TOKEN"], os.environ["USER_CHANNEL"])
