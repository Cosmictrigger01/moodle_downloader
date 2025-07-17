import requests
from bs4 import BeautifulSoup
import re
import time
from random import randint
import os

USERNAME = ""
PASSWORD = ""

LOGIN_URL = "https://sso.aau.at/cas/login?service=https%3A%2F%2Fmoodle.aau.at%2Flogin%2Findex.php%3FauthCAS%3DCAS"
COURSES = "https://moodle.aau.at/my/courses.php"

session = requests.Session()

response = session.get(LOGIN_URL)
soup = BeautifulSoup(response.text, "html.parser")

def get_input(name):
    tag = soup.find('input', {'name': name})
    return tag['value'] if tag else ''

lt = get_input('lt')
execution = get_input('execution')

payload = {
    "username": USERNAME,
    "password": PASSWORD,
    "lt": lt,
    "execution": execution,
    "_eventId": "submit"
}

login = session.post(LOGIN_URL, data=payload)

response = session.get(COURSES)

if "Logout" in response.text:
    print("Login succsesfull")
else:
    print("Login failed")


match = re.search(r"sesskey=([a-zA-Z0-9]+)", response.text)
if match:
    sesskey = match.group(1)
    print("Found sesskey:", sesskey)
else:
    print("sesskey not found")

payload = [{
    "index": 0,
    "methodname": "core_course_get_enrolled_courses_by_timeline_classification",
    "args": {
        "classification": "all",
        "limit": 0,
        "offset": 0,
        "sort": "fullname"
    }
}]

response = session.post(f"https://moodle.aau.at/lib/ajax/service.php?sesskey={sesskey}&info=core_course_get_enrolled_courses_by_timeline_classification",json= payload)
print(response.text)