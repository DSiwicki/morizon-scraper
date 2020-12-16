from selenium import webdriver
from bs4 import BeautifulSoup
from selenium.common.exceptions import NoSuchElementException, NoSuchAttributeException

from datetime import datetime
from time import sleep
import unidecode
from numpy.random import uniform

import os
import requests



def sleeper(str):
    if str == 's':
        sleep(uniform(0.1,2))
    elif str == 'm':
        sleep(uniform(2,3.5))
    elif str == 'l':
        sleep(uniform(3.5,7))
    else:
        print("Wrong string provided to sleeper!")
        


def full_driver():
    
    """Establish chrome driver with provided settings
    
    Returns
    -------
    driver
        running Chrome driver 
    """
    
    driver_path = './src/chromedriver'
    
    chrome_options = webdriver.ChromeOptions()
    
    chrome_options.add_argument('--window-size=1360,700')
    driver = webdriver.Chrome(driver_path, options = chrome_options)
    driver.set_page_load_timeout(180)
    
    return driver



def get_type_trns(driver: webdriver.chrome.webdriver.WebDriver
                 ):
    """Crawling morizon.pl home page in order to print available transaction and property types
    
    Parameters
    ----------
    driver: webdriver.chrome.webdriver.WebDriver
        running Chrome driver
    """
    
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
    """ Crawling provided sub-pages in order to gain offers' urls and basic information about estates 
    
    Parameters
    ----------
    driver: webdriver.chrome.webdriver.WebDriver
        running Chrome driver
        
    city: str
        name of the city to crawl
    
    sp_trns: str, optional
        type of transaction to crawl 
    
    district: str, optional
        name of the city's district to crawl 
    
    sp_type: str, optional
        type of property to crawl
    
    stop: int, optional
        number of pages to crawl for provided arguments, if 0 scraper will be running until last available page
       
    Returns
    -------
    estates_all: list
        list of lists containing basic information about estates
    """
    
    url = 'https://www.morizon.pl/'
    
    estates_all = []
    
    driver.get(url + sp_trns + sp_type + "/" + city + "/" + district)
    
    sleeper("m")
        
#     if driver.find_element_by_css_selector("button.sc-ifAKCX.dvvOSu"):
#         driver.find_element_by_css_selector("button.sc-ifAKCX.dvvOSu").click()

    try:
        driver.find_element_by_css_selector("button.sc-ifAKCX.dvvOSu").click()
    except NoSuchElementException:
        pass
        
    while True:
        
        if stop and driver.current_url == url + sp_trns + sp_type + "/" + city + "/" + district + '/?page=' + str(stop):
            break
    
        html = driver.page_source
        soup = BeautifulSoup(html, "html.parser")

        lista = soup.findAll(class_ = 'row-content row-property single-result mz-card mz-card_no-animation mz-card--listing')

        elementy = [[datetime.now(),
                    item.find('section').find('a').get('href'),
                    item.find('section').find('a').find('h2', attrs = {'class' : "single-result__title"}).getText().replace("\n", ""),
                    item.find('section').find('a').find('span', attrs = {'class': "single-result__category single-result__category--date"}).getText().replace("\n", ""),
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
    """Gathering estates data for provided urls
    
    Parameters
    ----------
    driver: webdriver.chrome.webdriver.WebDriver
        running Chrome driver
    
    urls: list
        list with links to offers to crawl
        
    Returns
    -------
    offers_data
        list of lists containing all scraper data
    """
    
    offers_data = []
    i = 1
    
    for url in urls:
        
        sleeper("s")
        
        driver.get(url)
        html = driver.page_source
        soup = BeautifulSoup(html, "html.parser")
        
        sleeper("s")
       
        try:
            driver.find_element_by_css_selector("button.sc-ifAKCX.dvvOSu").click()
        except NoSuchElementException:
            pass

        params = {}

        # geographical coordiates
        try:
            params["latitude"] = soup.find('div', {'class': "GoogleMap"}).get('data-lat')
        except AttributeError:
            params["latitude"] = ""
        try:
            params["longitude"] = soup.find('div', {'class': "GoogleMap"}).get('data-lng')
        except AttributeError:
            params["longitude"] = ""

        # offer id 
        data_id = soup.find('span', {"class": "ucFavourite"}).a.get("data-id")
        params["data_id"] = data_id

        dir = "img/" + data_id
        
#         if soup.find("a", {"data-tab-name": "multimediaBoxPhotos"})["class"] = "tab":
#             soup.find("a", {"data-tab-name": "multimediaBoxView3d"})["class"] = "tab"
#             soup.find("a", {"data-tab-name": "multimediaBoxPhotos"})["class"] = "tab selected"
            
        sleeper("s")

        if not os.path.exists(dir):
            os.mkdir(dir)
            
            try:
                for image in soup.find("ul", {"class": "list-unstyled list-inline imageBoxList"}).findAll('li'):
                    if image.img.get("style"):
                        href = str(image.img.get("src"))
                    else:
                        href =  str(image.img.get('data-original'))

                    n = image.img.get("data-number")

                    page = requests.get(href.replace('144/100/4', '832/468/2'))

                    with open(dir + "/" + str(n) + ".jpg", 'wb') as f:
                        f.write(page.content)
            except AttributeError:
                pass
        
        try:
            n = 0
            for table in soup.find("section", {"class" : "params clearfix"}).findAll("table"):
                for row in table.tbody.findAll('tr'):
                    params[row.th.getText().replace("\n", "")] = row.td.getText().replace("\n", "")
                n += 1
        except NoSuchElementException:
            continue
        
#         try:
#             for row in soup.find("section", {"class" : "params clearfix"}).findAll("table")[0].tbody.findAll('tr'):
#                 params[row.th.getText().replace("\n", "")] = row.td.getText().replace("\n", "")
#         except NoSuchElementException:
#             continue
            
#         try:
#             for row in soup.find("section", {"class" : "params clearfix"}).findAll("table")[1].tbody.findAll('tr'):
#                 params[row.th.getText().replace("\n", "")] = row.td.getText().replace("\n", "")
#         except NoSuchElementException:
#             continue

        try:
            for h3 in soup.find("section", {"class" : "params clearfix"}).findAll('h3')[n:]:
                params[h3.getText().replace("\n", "")] = h3.find_next('p').getText().replace("\n", "")
        except NoSuchElementException:
            continue

        params[soup.find("section", {'class': "descriptionContent"}).h3.getText().replace("\n", "")
              ] = soup.find("section", {'class': "descriptionContent"}).getText().replace("\n", " ").replace("\u200b", " ")
        
        print(str(i), driver.current_url)
        i += 1
        offers_data.append(params)
        
        sleeper("m")
        
    return offers_data
