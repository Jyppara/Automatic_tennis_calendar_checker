from datetime import datetime
import time
from selenium import webdriver
from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.by import By
import requests
from bs4 import BeautifulSoup
import smtplib
from email.mime.text import MIMEText


def check_selected_day(date):
    date_object = datetime.strptime(date, "%d.%m.%Y")
    free_hours = soup.find_all("td", class_="state_white res_success")
    count = 0
    print("Tarkistetaan " + date + " vapaita vuoroja.")
    for slot in free_hours:
        time = slot.find_previous("th", class_="datarow").get_text()
        hours, minutes = map(int, time.split(" - ")[0].split(":"))
        if date_object.day == datetime.now().day:
            if hours < datetime.now().hour:
                continue
        elif date_object.weekday() < 5:
            if hours >= 16:
                print("\tVapaa vuoro kello " + time + " varattavissa.")
                vapaat_vuorot.append((time, date))
                count += 1
        elif date_object.weekday() > 4:
            print("Vapaa vuoro kello " + time + " varattavissa.")
            vapaat_vuorot.append((time, date))
            count += 1
    if count == 0:
        print("\tEi vapaita vuoroja")


def suomenna_viikonpaiva(viikonpaiva):
    if viikonpaiva == "Monday":
        return "Maanantaina"
    elif viikonpaiva == "Tuesday":
        return "Tiistaina"
    elif viikonpaiva == "Wednesday":
        return "Keskiviikkona"
    elif viikonpaiva == "Thursday":
        return "Torstaina"
    elif viikonpaiva == "Friday":
        return "Perjantaina"
    elif viikonpaiva == "Saturday":
        return "Lauantaina"
    elif viikonpaiva == "Sunday":
        return "Sunnuntaina"


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
            check_selected_day(option.get("value"))

        if len(vapaat_vuorot) > 0:
            message = "\nVAPAITA VUOROJA LÖYTYI SEURAAVASTI:\n \n"
            for vuoro in vapaat_vuorot:
                kellonaika, pvm = vuoro
                viikonpaiva = datetime.strptime(pvm, "%d.%m.%Y").strftime("%A")
                viikonpaiva = suomenna_viikonpaiva(viikonpaiva)
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
