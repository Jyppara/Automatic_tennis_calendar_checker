from datetime import datetime, timedelta
import time
from selenium import webdriver
from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.by import By
import requests
from bs4 import BeautifulSoup
import smtplib
from email.mime.text import MIMEText
from flask import Flask, request, render_template

app = Flask(__name__)

# This program checks for free tennis court slots from the certain tennis court
# in Finland. It uses Selenium to open the browser and BeautifulSoup to parse
# the HTML. It checks the slots for the next 14 days and prints the results.
# It checks the slots every 10 minutes and prints the results if there are any
# free slots available.


def check_selected_day(date, free_shifts, soup):
    # This function checks the selected day for free slots. It checks the day
    # for free slots if the day is today or the day is in the future. If the
    # day is today, it checks the time and only prints the free slots that are
    # in the future. If the day is in the future, it checks if the day is
    # weekend or weekday and prints the free slots accordingly.
    date_object = datetime.strptime(date, "%d.%m.%Y")
    free_hours = soup.find_all("td", class_="state_white res_success")
    count = 0
    print("Tarkistetaan " + date + " vapaita vuoroja.")
    for slot in free_hours:
        time = slot.find_previous("th", class_="datarow").get_text()
        hours, minutes = map(int, time.split(" - ")[0].split(":"))
        if date_object.day == datetime.now().day:  # today
            if date_object.weekday() < 5:  # if today is weekday
                if (
                    hours > 16 and hours > datetime.now().hour
                ):  # if today is weekday and the hour has passed
                    print("\tVapaa vuoro kello " + time + " varattavissa.")
                    free_shifts.append((time, date))
                    count += 1
            elif (
                date_object.weekday() > 4 and hours > datetime.now().hour
            ):  # if today is weekend and the hour has passed
                print("\tVapaa vuoro kello " + time + " varattavissa.")
                free_shifts.append((time, date))
                count += 1
        elif date_object.weekday() < 5:  # weekday, not today
            if hours >= 16:
                print("\tVapaa vuoro kello " + time + " varattavissa.")
                free_shifts.append((time, date))
                count += 1
        elif date_object.weekday() > 4:  # weekend, not today
            print("\tVapaa vuoro kello " + time + " varattavissa.")
            free_shifts.append((time, date))
            count += 1
    if count == 0:
        print("\tEi vapaita vuoroja")


def translate_to_finnish(weekday):
    # This function translates the weekdays to Finnish.
    if weekday == datetime.now():
        return "Tänään"
    elif weekday == datetime.now() + timedelta(days=1):
        return "Huomenna"
    elif weekday.strftime("%A") == "Monday":
        return "Maanantaina"
    elif weekday.strftime("%A") == "Tuesday":
        return "Tiistaina"
    elif weekday.strftime("%A") == "Wednesday":
        return "Keskiviikkona"
    elif weekday.strftime("%A") == "Thursday":
        return "Torstaina"
    elif weekday.strftime("%A") == "Friday":
        return "Perjantaina"
    elif weekday.strftime("%A") == "Saturday":
        return "Lauantaina"
    elif weekday.strftime("%A") == "Sunday":
        return "Sunnuntaina"


@app.route("/")
def main():
    logo_text = " _____                _     _               _       _\n|_   _|__ _ __  _ __ (_)___| | _____  _   _| |_ ___(_)\n  | |/ _ \ '_ \| '_ \| / __| |/ / _ \| | | | __/ __| |\n  | |  __/ | | | | | | \__ \   < (_) | |_| | |_\__ \ |\n  |_|\___|_| |_|_| |_|_|___/_|\_\___/ \__,_|\__|___/_|"
    print(logo_text)
    print(' "Keskity pelaamiseen eläkä varaamiseen." -Tenniskoutsi™\n')
    while True:
        url = "https://varaus.hukka.net/index.php?func=mod_rc_v2"
        free_shifts = []
        # Avaa selain ja lataa sivu
        response = requests.get(url)
        if response.status_code == 200:
            html = response.text
            soup = BeautifulSoup(html, "html.parser")
            for option in soup.find_all("option"):
                response = requests.get(url + "&pageId=12&cdate=" + option.get("value"))
                html = response.text
                soup = BeautifulSoup(html, "html.parser")
                check_selected_day(option.get("value"), free_shifts, soup)

            if len(free_shifts) > 0:
                message = (
                    "\nHaku suoritettu kello "
                    + datetime.now().strftime("%H:%M")
                    + "\n\nVAPAITA VUOROJA LÖYTYI SEURAAVASTI:\n \n"
                )
                for vuoro in free_shifts:
                    kellonaika, pvm = vuoro
                    viikonpaiva = datetime.strptime(pvm, "%d.%m.%Y")
                    viikonpaiva = translate_to_finnish(viikonpaiva)
                    message += f"{viikonpaiva}\t{pvm} kello {kellonaika}\n"
                print(message)
                print("Linkki kalenteriin: \n" + url + "\n")
            else:
                print("Vapaita vuoroja ei löytynyt.")

            for i in range(10):
                b = "Seuraava tarkistus " + str(10 - i) + " minuutin kuluttua. "
                print(b, end="\r")
                time.sleep(60)
            print(
                "Uusi tarkistus aloitettu kello "
                + datetime.now().strftime("%H:%M:%S")
                + "\n"
            )
        else:
            print("Virhe sivun latauksessa. Koodi: " + str(response.status_code))
            for i in range(5):
                b = "Yritetään uudelleen " + str(5 - i) + " minuutin kuluttua. "
                print(b, end="\r")
                time.sleep(60)


if __name__ == "__main__":
    main()
