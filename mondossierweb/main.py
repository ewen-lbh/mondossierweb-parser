#!/usr/bin/env python
"""
Usage: mondossierweb [SAVE_AS] [URL] [GRADE_CODE] [USERNAME] [PASSWORD_COMMAND]  
       mondossierweb --help 

Environment variables:
    MDW_USE_CACHE: if set, the HTML will be cached to mdw.html and will be reused if it exists.
"""

from pathlib import Path
import json
from subprocess import run
from time import sleep
from docopt import docopt
from bs4 import BeautifulSoup
from helium import write, click, S, start_firefox, kill_browser
from typing import NamedTuple, Literal
import selenium.common.exceptions
import sys
import os


class Grade(NamedTuple):
    code: str
    label: str
    grade: float | Literal["ABJ"] | Literal["ABI"]
    indentation: int

    def __str__(self):
        return f"[{self.code}] {self.label}: {self.grade}"


def configure():
    opts = docopt(__doc__)

    def cli_arg_or(key, ask_message):
        if (arg := opts.get(key)) is not None:
            return arg
        return input(ask_message)

    username = cli_arg_or("USERNAME", "Username: ")
    password_command = cli_arg_or("PASSWORD_COMMAND", "Command to get password: ")
    grade_code = cli_arg_or("GRADE_CODE", "Grade code (e.g. N7I51 for SN 1A): ")
    save_as = Path(cli_arg_or("SAVE_AS", "Save JSON file as: "))
    url = cli_arg_or("URL", "URL de mondossierweb: ")
    return username, password_command, grade_code, save_as, url


def get_password(password_command):
    result = run(password_command, shell=True, capture_output=True)
    error = result.stderr.decode("utf-8")

    if f"{password_command}: command not found" in error:
        print(
            f"\t\tPassword command {password_command} not found, trying to use it as a password."
        )
        return password_command

    if result.returncode != 0:
        raise RuntimeError(
            f"Command {password_command} failed with code {result.returncode}: {error}"
        )

    return result.stdout.decode("utf-8").strip()


def get_html(username, password_command, grade_code, url):
    if Path("mdw.html").exists():
        print("\tUsing cached HTML")
        return BeautifulSoup(Path("mdw.html").read_text(), features="lxml")
    print(f"\tOpening {url}…")
    start_firefox(url, headless=True)
    print("\tTyping username")
    write(username, into="Username")
    print("\tTyping password")
    write(get_password(password_command), into="Password")
    print("\tLogging in…")
    click("Login")
    try:
        if "Invalid credentials" in S("body").web_element.text:
            print("\t\tInvalid credentials, exiting.")
            kill_browser()
            sys.exit(2)
    except selenium.common.exceptions.StaleElementReferenceException:
        pass

    print("\tWaiting for page to load…")
    sleep(3)
    print("\tClosing reminder")
    click("Fermer")
    print("\tNavigating to grades page")
    click("Notes & résultats")
    print("\tOpening grades table")
    click(grade_code)
    print("\tClosing annoying reminder")
    click("Fermer")
    print("\tCapturing page body")
    html = S("body").web_element.get_attribute("innerHTML")
    if os.getenv("MDW_USE_CACHE"):
        print("\tCaching HTML to mdw.html") 
        Path("mdw.html").write_text(html)
    parsed = BeautifulSoup(html, features="lxml")
    kill_browser()
    return parsed


def grade_or_none(string):
    if string.upper() in {"ABJ", "ABI"}:
        return string.upper()
    try:
        return float(string)
    except ValueError:
        return None


def to_dict(document, grade_code):
    print("\tGetting the right table")
    table = [t for t in document("table") if grade_code in t.strings][0]
    print("\tExtracting cells")
    cells = [
        [cell.replace("\xa0", "\t") for cell in row.strings] for row in table("tr")
    ]
    Path("mdw-cells.json").write_text(json.dumps(cells, indent=4))
    print("\tExtracting grades")
    grades = {}
    for row in cells:
        label = [cell for cell in row[1:] if cell.strip()][0]
        label, indentation = label.strip(), label.count("\t")
        numbers = [grade_or_none(cell) for cell in row if grade_or_none(cell)]
        if not numbers:
            print(f"\t\tSkipping row {label}: no grades found")
            continue
        grades[label] = {
            "code": row[0],
            "label": label,
            "grade": numbers[0],
            "indentation": indentation,
        }
    return grades


def diff_with_previous(new_grades):
    changes = {}
    if not Path("grades.json").exists():
        return
    print("Previous grades file found, checking for differences.")
    print("\tLoading previous grades")
    old_grades = json.loads(Path("grades.json").read_text())

    print("\n")
    for key in new_grades.keys() - old_grades.keys():
        print(f"- New grade: {Grade(**new_grades[key])}")
        changes[key] = new_grades[key]

    for key in new_grades.keys() & old_grades.keys():
        if (new_grade := new_grades[key]["grade"]) != (
            old_grade := old_grades[key]["grade"]
        ):
            print(f"- Grade for {key} changed: {old_grade} -> {new_grade}.")
            changes[key] = new_grade

    if not changes:
        print("No changes found.")

    print("\n")

    return changes


def main():
    username, password_command, grade_code, save_as, url = configure()
    print("Getting HTML")
    document = get_html(username, password_command, grade_code, url)
    print("Parsing HTML table into dict")
    grades = to_dict(document, grade_code)
    print(f"Got grades: {grades}")
    changed = diff_with_previous(grades)
    print(f"Writing to {save_as}")
    save_as.write_text(json.dumps(grades, indent=4))

    sys.exit(1 if changed else 0)

if __name__ == "__main__":
    main()
