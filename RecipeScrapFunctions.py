from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import NoSuchElementException
from recipe_scrapers import scrape_me, scrape_html, scraper_exists_for
from Homemade_Recipe_Scraper import homemade_webscraper


def get_search_input(inp_str, num_max_recipes):
    # Taking input from user
    # search_string = input("Input the URL or string you want to search for: ").lower()
    search_string = inp_str
    if ('recipe' or 'recipes') in search_string:
        print('Search contains recipe already')
    else:
        search_string += ' recipe'
        print(f'Added recipe to search input, now searching for: {search_string}')

    # get max number of links to find
    # num_max_recipes = input("Input the number of recipes to extract:")
    num_max_recipes = num_max_recipes
    while (type(num_max_recipes) != int):
        try:
            num_max_recipes = int(float(num_max_recipes) // 1)  # rounds down to int
        except:
            num_max_recipes = input("Try again with a number:")

    # This is done to structure the string
    # into search url.(This can be ignored)
    search_string = search_string.replace(' ', '+')
    page_start = "0"
    google_string = "https://www.google.com/search?q=" + search_string + "&start=" + page_start
    return google_string, num_max_recipes


def accept_cookies(wd):
    '''
    used to bypass cookies on google page
    '''
    # find cookie text and accept
    try:
        cookie = wd.find_element(By.XPATH, "//*[text()='Accept all']")
        cookie.click()
    except:
        print('no cookies found?')


def show_more_recipes(num_max_recipes, wd):
    '''
    used to  expand the recipes section on google search to capture more recipe links
    '''

    # used to expand to the desired number of recipes on google site
    num_recipes = len(wd.find_elements(By.XPATH, "//div[contains(@class,'v1uiFd')]"))
    while num_recipes < num_max_recipes:
        try:
            num_recipes = len(wd.find_elements(By.XPATH, "//div[contains(@class,'v1uiFd')]"))
        except:
            print('Cannot find any recipes, game over')
            break

        try:
            show_more = wd.find_element(By.XPATH, "//span[@class='M1YrRd']")
            show_more.click()
            # print('More results shown')
            while len(wd.find_elements(By.XPATH, "//div[contains(@class,'v1uiFd')]")) <= num_recipes:
                elem = WebDriverWait(wd, 1)  # this stops the while loop speeding around, runs in 1 sec loops
        except:
            print('failed show more search')
            break


def check_recipe_git(url):
    '''
    check if scraper format exists for url, and if so returns scraper object. Else returns url string.
    '''
    if scraper_exists_for(url):
        # html = requests.get(url).content
        # scraped_url = scrape_html(html=html, org_url=url)
        try:
            scraped_url = scrape_me(url, wild_mode=True)
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
            print(f'Scraper found for: {url}')
            if scraped_url.ingredients() \
                    and scraped_url.instructions() \
                    and scraped_url.host() \
                    and scraped_url.title():
                # print(scraped_url)
                print('Key scraped details found, returning json')
                # scraped_url.total_time = str(float(scraped_url.total_time)//1) + ' mins'
                return scraped_url
            else:
                return url

        except:
            # scraped_url = homemade_webscraper(url)
            print(f'No scraper for: {url}')
            return url
    else:
        # scraped_url = homemade_webscraper(url)
        print(f'No scraper for: {url}')
        return url


def get_recipe_links(num_max_recipes, wd):
    '''
    Used to get links from main google search pages, and move to next pages until max link nums is reached
    '''
    scraped_links = []
    unscraped_links = []
    while len(scraped_links) < num_max_recipes:
        results = wd.find_elements(By.CLASS_NAME, "yuRUbf")

        # iterate to get links until max link num reached
        for a in range(len(results)):
            if len(scraped_links) < num_max_recipes:
                try:
                    search_link = results[a].find_element(By.TAG_NAME, "a")
                    search_link_url = search_link.get_attribute("href")
                    if search_link_url not in scraped_links:
                        scrape_obj = check_recipe_git(search_link_url)
                        print(type(scrape_obj))
                        if type(scrape_obj) is not str:  # may need to change this
                            scraped_links.append(scrape_obj)
                        else:
                            unscraped_links.append(search_link_url)
                except NoSuchElementException:
                    print("Link elements not found")
                    break

        # go to next page if need more results
        if len(scraped_links) < num_max_recipes:
            try:
                # next_page = wd.find_element(By.XPATH, "//td/a[contains(.,'Next')]")
                next_page = wd.find_element(By.XPATH, "//*[@id='pnnext']")
                # pnnext
                next_page.click()
            except NoSuchElementException:
                print("Next page element not found")
                break
    return scraped_links, unscraped_links





