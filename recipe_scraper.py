from http import cookiejar
from selenium import webdriver
from selenium.webdriver.common.by import By
import requests
import pandas as pd
from bs4 import BeautifulSoup
import io
import time
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager

import RecipeScrapFunctions as rsf
from recipe_scrapers import scrape_me, scrape_html, scraper_exists_for
def scrape_me_baby(search_str, num_links):
    # selenium web driver method
    chrome_options = Options()
    chrome_options.add_experimental_option("detach", True)  # used to hold chrom open
    chrome_options.add_experimental_option('excludeSwitches', ['enable-logging'])  # used to stop bluetooth errors
    # chrome_options.add_argument("start-maximized")
    wd = webdriver.Chrome(service=Service(ChromeDriverManager(version='114.0.5735.90').install()), options=chrome_options)
    # driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager(version='114.0.5735.90').install()))

    # run scraper
    google_string, num_max_recipes = rsf.get_search_input(search_str, num_links)  # get user search input
    print(f"search string: {google_string}")
    print(f"searching for {num_max_recipes} recipes")
    wd.get(google_string)  # open google search string
    rsf.accept_cookies(wd)  # remove cookies
    search_links, unscraped_links = rsf.get_recipe_links(num_max_recipes, wd)
    print(f'Scraped links: {search_links}')
    print(f'length: {len(search_links)}')
    print(f'Unscraped links: {unscraped_links}')
    print(f'length: {len(unscraped_links)}')
    return search_links, unscraped_links

# scrape_me_baby('lemon cake', 2)


# # selenium web driver method
# chrome_options = Options()
# chrome_options.add_experimental_option("detach", True) #used to hold chrom open
# chrome_options.add_experimental_option('excludeSwitches', ['enable-logging']) #used to stop bluetooth errors
# # chrome_options.add_argument("start-maximized")
# wd = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
#
# # run scraper
# google_string, num_max_recipes = rsf.get_search_input()  # get user search input
# print(f"search string: {google_string}")
# print(f"searching for {num_max_recipes} recipes")
# wd.get(google_string)  # open google search string
# rsf.accept_cookies(wd)  # remove cookies
# search_links, unscraped_links = rsf.get_recipe_links(num_max_recipes, wd)
# print(f'Scraped links: {search_links}')
# print(f'length: {len(search_links)}')
# print(f'Unscraped links: {unscraped_links}')
# print(f'length: {len(unscraped_links)}')
#
# # loop through urls





