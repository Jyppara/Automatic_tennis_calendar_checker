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


def check_selected_day(date, vapaat_vuorot, soup):
    date_object = datetime.strptime(date, "%d.%m.%Y")
    free_hours = soup.find_all("td", class_="state_white res_success")
    count = 0
    print("Tarkistetaan " + date + " vapaita vuoroja.")
    for slot in free_hours:
        time = slot.find_previous("th", class_="datarow").get_text()
        hours, minutes = map(int, time.split(" - ")[0].split(":"))
        if date_object.day == datetime.now().day:  # tänään
            if date_object.weekday() < 5:  # jos tänään on arkipäivä
                if (
                    hours > 16 and hours > datetime.now().hour
                ):  # jos tänään on arkipäivä ja tunti on jo mennyt
                    print("\tVapaa vuoro kello " + time + " varattavissa.")
                    vapaat_vuorot.append((time, date))
                    count += 1
            elif (
                date_object.weekday() > 4 and hours > datetime.now().hour
            ):  # jos tänään on viikonloppu ja tunti on jo mennyt
                print("\tVapaa vuoro kello " + time + " varattavissa.")
                vapaat_vuorot.append((time, date))
                count += 1
        elif date_object.weekday() < 5:  # arkipäivä, ei tänään
            if hours >= 16:
                print("\tVapaa vuoro kello " + time + " varattavissa.")
                vapaat_vuorot.append((time, date))
                count += 1
        elif date_object.weekday() > 4:  # viikonloppu, ei tänään
            print("\tVapaa vuoro kello " + time + " varattavissa.")
            vapaat_vuorot.append((time, date))
            count += 1
    if count == 0:
        print("\tEi vapaita vuoroja")


def translate_to_finnish(viikonpaiva):
    if viikonpaiva == datetime.now():
        return "Tänään"
    elif viikonpaiva == datetime.now() + timedelta(days=1):
        return "Huomenna"
    elif viikonpaiva.strftime("%A") == "Monday":
        return "Maanantaina"
    elif viikonpaiva.strftime("%A") == "Tuesday":
        return "Tiistaina"
    elif viikonpaiva.strftime("%A") == "Wednesday":
        return "Keskiviikkona"
    elif viikonpaiva.strftime("%A") == "Thursday":
        return "Torstaina"
    elif viikonpaiva.strftime("%A") == "Friday":
        return "Perjantaina"
    elif viikonpaiva.strftime("%A") == "Saturday":
        return "Lauantaina"
    elif viikonpaiva.strftime("%A") == "Sunday":
        return "Sunnuntaina"


@app.route("/")
def main_loop():
    logo_text = " _____                _     _               _       _\n|_   _|__ _ __  _ __ (_)___| | _____  _   _| |_ ___(_)\n  | |/ _ \ '_ \| '_ \| / __| |/ / _ \| | | | __/ __| |\n  | |  __/ | | | | | | \__ \   < (_) | |_| | |_\__ \ |\n  |_|\___|_| |_|_| |_|_|___/_|\_\___/ \__,_|\__|___/_|\n"
    print(logo_text)
    while True:
        url = "https://varaus.hukka.net/index.php?func=mod_rc_v2"
        vapaat_vuorot = []
        # Avaa selain ja lataa sivu
        response = requests.get(url)
        if response.status_code == 200:
            html = response.text
            soup = BeautifulSoup(html, "html.parser")
            for option in soup.find_all("option"):
                response = requests.get(url + "&pageId=12&cdate=" + option.get("value"))
                html = response.text
                soup = BeautifulSoup(html, "html.parser")
                check_selected_day(option.get("value"), vapaat_vuorot, soup)

            if len(vapaat_vuorot) > 0:
                message = "\nVAPAITA VUOROJA LÖYTYI SEURAAVASTI:\n \n"
                for vuoro in vapaat_vuorot:
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

main_loop()
