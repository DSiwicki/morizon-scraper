from selenium import webdriver
from bs4 import BeautifulSoup

from datetime import datetime
from time import sleep
import unidecode

import os
import requests


def full_driver():
    
    driver_path = './src/chromedriver'
    
    chrome_options = webdriver.ChromeOptions()
    
    chrome_options.add_argument('--window-size=1360,700')
    driver = webdriver.Chrome(driver_path, options = chrome_options)
    driver.set_page_load_timeout(180)
    
    return driver



def get_type_trns(driver: webdriver.chrome.webdriver.WebDriver
                 ):
    
    url = 'https://www.morizon.pl/'
    driver.get(url)
    
    html = driver.page_source
    soup = BeautifulSoup(html, "html.parser")
    ps_type = ['nieruchomosci' if option.getText()  == "dowolny" else unidecode.unidecode(option.getText()) for option in soup.find("div", {"class": "ps_type fromSimpleBox"}).findAll("option")]
    ps_trns= [unidecode.unidecode(option.getText())  for option in soup.find("div", {"class": "ps_transaction fromSimpleBox"}).findAll("option")]
       
    print("Available property types: \n", ps_type, "\n Default property type is: mieszkania \n")
    print("Available transaction types: \n", ps_trns, "\n Default transaction type is: sprzedaz")



def get_links(driver: webdriver.chrome.webdriver.WebDriver,
                     city: str, 
                     sp_trns: str = "",
                     district: str = "", 
                     sp_type: str = "mieszkania", 
                     stop: int = 0
                    ):
    
    url = 'https://www.morizon.pl/'
    
    estates_all = []
    
    driver.get(url + sp_trns + sp_type + "/" + city + "/" + district)
        
    while True:
        
        if stop and driver.current_url == url + sp_trns + sp_type + "/" + city + "/" + district + '/?page=' + str(stop):
            break
    
        html = driver.page_source
        soup = BeautifulSoup(html, "html.parser")

        lista = soup.findAll(class_ = 'row-content row-property single-result mz-card mz-card_no-animation mz-card--listing')

        elementy = [[datetime.now(),
                    item.find('section').find('a').get('href'),
                    item.find('section').find('a').find('h2', attrs = {'class' : "single-result__title"}).getText(),
                    item.find('section').find('a').find('span', attrs = {'class': "single-result__category single-result__category--date"}).getText(),
                    item.find('section').find('a').find('meta', attrs = {'itemprop' : 'price'}).get('content'),
                    item.find('section').find('a').find('meta', attrs = {'itemprop' : 'priceCurrency'}).get('content'),
                    item.find('section').find('div', {"class" : "info-description single-result__info"}).ul.findAll('li')[0].getText(),
                    item.find('section').find('div', {"class" : "info-description single-result__info"}).ul.findAll('li')[1].getText(),
                    item.find('section').find('div', {"class" : "info-description single-result__info"}).ul.findAll('li')[2].getText(),
                    item.section.find('div', {"class" : "description single-result__description"}).p.getText()
                    ] for item in lista if "property-url" in item.find('section').find('a').get('class')]

        estates_all = estates_all + elementy
        
        print(driver.current_url)
        
        next_button = driver.find_element_by_css_selector("a.mz-pagination-number__btn.mz-pagination-number__btn--next")
        next_button.click()
        
    return estates_all
        

    
def get_offers(driver: webdriver.chrome.webdriver.WebDriver,
               urls: list
              ):
    
    offers_data = []
    
    for url in urls:
    
        driver.get(url)
        html = driver.page_source
        soup = BeautifulSoup(html, "html.parser")

        params = {}

        # geographical coordiates
        params["latitude"] = soup.find('div', {'class': "GoogleMap"}).get('data-lat')
        params["longitude"] = soup.find('div', {'class': "GoogleMap"}).get('data-lng')

        # offer id 
        data_id = soup.find('span', {"class": "ucFavourite"}).a.get("data-id")
        params["data_id"] = data_id

        dir = "img/" + data_id

        if not os.path.exists(dir):
            os.mkdir(dir)
            for image in soup.find("ul", {"class": "list-unstyled list-inline imageBoxList"}).findAll('li'):

                if image.img.get("style"):
                    href = str(image.img.get("src"))
                else:
                    href =  str(image.img.get('data-original'))

                n = image.img.get("data-number")

                page = requests.get(href.replace('144/100/4', '832/468/2'))

                with open(dir + "/" + str(n) + ".jpg", 'wb') as f:
                    f.write(page.content)

        try:
            for row in soup.find("section", {"class" : "params clearfix"}).findAll("table")[0].tbody.findAll('tr'):
                params[row.th.getText().replace("\n", "")] = row.td.getText().replace("\n", "")
        except:
            continue
            
        try:
            for row in soup.find("section", {"class" : "params clearfix"}).findAll("table")[1].tbody.findAll('tr'):
                params[row.th.getText().replace("\n", "")] = row.td.getText().replace("\n", "")
        except:
            continue

        try:
            for h3 in soup.find("section", {"class" : "params clearfix"}).findAll('h3')[2:]:
                params[h3.getText().replace("\n", "")] = h3.find_next('p').getText().replace("\n", "")
        except:
            continue

        params[soup.find("section", {'class': "descriptionContent"}).h3.getText().replace("\n", "")
              ] = soup.find("section", {'class': "descriptionContent"}).getText().replace("\n", " ").replace("\u200b", " ")
        
        offers_data.append(params)
        
    return offers_data
