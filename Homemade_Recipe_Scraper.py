import requests
from bs4 import BeautifulSoup
import re


def homemade_webscraper(url):
    '''
    Used to scrape data from general cooking websites and output object with json data mimicing git repo
    '''
    # other method to check urls not listed in git repo
    # have to predict what tags are used and search through text for key words

    html = requests.get(url).text
    web_html = BeautifulSoup(html, 'html.parser')

    # find all following details:
    # print(
    #     scraper.host(), '\n',
    #     scraper.title(), '\n',
    #     scraper.total_time(), '\n',
    #     scraper.image(), '\n',
    #     scraper.ingredients(), '\n',
    #     scraper.instructions(), '\n',
    #     scraper.instructions_list(), '\n',
    #     scraper.yields(), '\n',
    #     scraped_url.to_json(), '\n',
    #     scraper.links(), '\n',
    #     scraper.nutrients(),  # if available
    # )

    find_ingredients(web_html)


def find_ingredients(web_html):
    html_tags = ['title', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6']
    search_tags = ['Ingredients', 'ingredients']

    for tag in html_tags:
        for search_tag in search_tags:
            try:
                ing_list = web_html.find(tag, text=[re.compile(search_tag)])
                if len(ing_list) > 0:
                    print(f'found for html tag: {tag}; and search tag: {search_tag}!')
                    # print(ing_list)
                    # print('\nnext sibling')
                    # print(ing_list.find_next_sibling('div'))
                    # print('\nnext div')
                    # print(ing_list.find_next('div'))
                    parent_ing = ing_list.parent

                    # strip white space or filler divs
                    while len(parent_ing.get_text().lower().strip().replace("ingredients", "")) == 0:
                        parent_ing = parent_ing.parent
                    print(parent_ing.get_text())
                    return parent_ing.get_text()
            except Exception as ex:
                template = "An exception of type {0} occurred. Arguments:\n{1!r}"
                message = template.format(type(ex).__name__, ex.args)
                # print(message)