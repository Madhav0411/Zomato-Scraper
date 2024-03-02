from selenium import webdriver
from selenium.webdriver.common.by import By
import webbrowser
from bs4 import BeautifulSoup
import pandas as pd
import xlsxwriter
from selenium.common.exceptions import NoSuchElementException
import time
from random_user_agent.user_agent import UserAgent
from random_user_agent.params import SoftwareName,OperatingSystem
from selenium.webdriver.chrome.options import Options
import json
from selenium.webdriver.common.action_chains import ActionChains

url = input("Enter the Zomato City URL (Ex. https://www.zomato.com/hyderabad): ")
driver = webdriver.Chrome()
categories = ["dine-out","delivery","drinks-and-nightlife"]

for category in categories:
    driver.get(url+"/"+category)

    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    time.sleep(10)

    soup = BeautifulSoup(driver.page_source, "html.parser")
    hotels = ["https://www.zomato.com"+hotel.find("a")['href'] for hotel in soup.find_all("div",{"class":"sc-hAcydR"})]
    print(hotels)

    data = []
    page = 1
    total_hotels = len(hotels)
    for hotel in hotels:
        try:
            print(f"Hotel no. {page} out of {total_hotels} Hotels in Category - {category}")
            
            driver.get("/".join(hotel.split("/")[:5]))
            time.sleep(2)
            soup = BeautifulSoup(driver.page_source, "html.parser")
            name = soup.find("h1",{"class":"sc-7kepeu-0 sc-iSDuPN fwzNdh"}).text
            location = soup.find("p",{"class":"sc-1hez2tp-0 clKRrC"}).text
            dining_rating = soup.find_all("div",{"class":"sc-1q7bklc-1 cILgox"})[0].text
            delivery_rating = soup.find_all("div",{"class":"sc-1q7bklc-1 cILgox"})[1].text

            driver.get("/".join(hotel.split("/")[:-1])+"/order")
            time.sleep(2)
            soup = BeautifulSoup(driver.page_source,"html.parser")
            items = soup.find_all("div",{"class":"sc-1s0saks-11 cYGeYt"})
            for item in items:
                item_name = item.find("h4",{"class":"sc-1s0saks-15 iSmBPS"}).text
                item_price = item.find("span",{"class":"sc-17hyc2s-1 cCiQWA"}).text
                
                new_data = {
                    "Name" : name,
                    "Location" : location,
                    "Dining Ratings" : dining_rating,
                    "Delivery Ratings" : delivery_rating,
                    "Item Name" : item_name,
                    "Item Price" : item_price,
                    "Restaurant URL" : hotel
                }

                data.append(new_data)
            page += 1
        except Exception as e:
            print(e)
            continue

    df = pd.DataFrame(data)
    df.to_excel("Data/"+url.split("/")[3]+"-"+category+".xlsx", index=False)
