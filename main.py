import requests
from bs4 import BeautifulSoup
import re
import time
import os

USERNAME = ""
PASSWORD = ""

LOGIN_URL = "https://sso.aau.at/cas/login?service=https%3A%2F%2Fmoodle.aau.at%2Flogin%2Findex.php%3FauthCAS%3DCAS"
COURSES_URL = "https://moodle.aau.at/my/courses.php"

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

response = session.get(COURSES_URL)

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

courses = []
for course_dict in response.json()[0]["data"]["courses"]:
    courses.append([course_dict["fullname"], course_dict["id"]])
if courses != []:
    print("extracted course data")

for course in courses:
    os.makedirs(course[0], exist_ok=True)
    print(f"created course folder or folder already exists: {course[0]}")

    response = session.get(f"https://moodle.aau.at/course/view.php?id={course[1]}")
    soup = BeautifulSoup(response.text, "html.parser")

    resource_links = []
    for tag in soup.find_all("a", href = True):
        href = tag['href']
        if "/mod/resource/view.php?id=" in href or ".pdf" in href:
            resource_links.append(href)
    print(f"found resource_links = {resource_links}")

    for link in resource_links:
        response = session.get(link, allow_redirects=True)
        if response.url == link:
            soup = BeautifulSoup(response.text, "html.parser")
            for tag in soup.find_all("a", href = True):
                href = tag["href"]
                if ".pdf" in href and href not in resource_links:
                    resource_links.append(href)
                    print(f"adding {href}")
                    
        final_url = response.url
        filename = os.path.basename(final_url).split("?")[0]

        if ".pdf" in filename.lower():
            try:
                with open(os.path.join(course[0],filename), "rb") as infile:
                    print(f"file already exists: {filename}")
            except:
                with open(os.path.join(course[0],filename), "wb") as outfile:
                    outfile.write(response.content)
                    print(f"Downloaded: {filename}")
        time.sleep(0.1)