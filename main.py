# This project is for web scraping the calender data from
# website: https://varaus.hukka.net/index.php?func=mod_rc_v2.
# The program should be run every hour to get the latest data.
# When there is a free time slot, the program will send an email
# to the user. The time slot is 16:00-22:00 on monday to thursday,
# 16:00-21:00 on friday and 8:00-20:00 on saturday and sunday.
# The program will send an email to the user when there is a free # time slot.

# The calender data is stored in tbody tag. The rows are stored in
# tr tag and the cells are stored in td tag. The cells with class
# name "state_white res_success" are the cells/hours that are free.
# The unavailable cells/hours have class name "state_red".
# The cells/hours that are passed already have class name
# "state_white res_success". The program has to check the time
# so it won't
from datetime import datetime
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
                print("Vapaa vuoro kello " + time + " varattavissa.")
                vapaat_vuorot.append((time, date))
                count += 1
        elif date_object.weekday() > 4:
            print("Vapaa vuoro kello " + time + " varattavissa.")
            vapaat_vuorot.append((time, date))
            count += 1
    if count == 0:
        print("Ei vapaita vuoroja")


# kysy käyttäjältä haluaako aloittaa etsinnän vai sulkea ohjelman

while True:
    answer = input("Haluatko aloittaa etsinnän? (k/e)")
    if answer == "k":
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
                message = "Vapaita vuoroja löytyi seuravasti:\n \n"
                for vuoro in vapaat_vuorot:
                    time, date = vuoro
                    message += f"Päivämäärä: {date}, Kellonaika: {time}\n"  
                print(message)
                print("Linkki kalenteriin: \n" + url)
            else:
                print("Vapaita vuoroja ei löytynyt.")
    elif answer == "e":
        print("Ohjelma suljetaan.")
        break
    else:
        print("Vastaa k tai e")
