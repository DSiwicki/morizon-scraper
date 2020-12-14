# morizon-scraper

The following scraper was created in order to gather data for purposes of my paper _The Application of Machine Learning Algorithms for Spatial Analysis: Predicting of Real Estate Prices in Warsaw_. Codes were refreshed in December 2020.

The project include 4 functions:

```python 

def full_driver()

```

That establish connection with Chrome and set chrome_options.

```python 

def get_type_trns(driver: webdriver.chrome.webdriver.WebDriver
                 )

```

That allows to list available transaction and estate types. Function is not neccesary to run, in such case the default parameters are used.

```python

def get_links(driver: webdriver.chrome.webdriver.WebDriver,
                     city: str, 
                     sp_trns: str = "",
                     district: str = "", 
                     sp_type: str = "mieszkania", 
                     stop: int = 0
                    )
                    
```

That function allows to get links to estate offers (with some basic information from listing's elements).

```python

def get_offers(driver: webdriver.chrome.webdriver.WebDriver,
               urls: list
              )
              
```

That function allows to gather whole data available for provided offers - including quantitative characteristics and description. Additionally, new version includes gathering images that offer contains.

