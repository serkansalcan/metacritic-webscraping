from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from time import sleep
import pandas as pd

PATH = "C:\Program Files\chromedriver.exe"
driver = webdriver.Chrome(PATH)

platform = 'pc'  # selecting the platform: pc or ps4
years = [2017, 2018, 2019, 2020, 2021]  # selecting which year's games to scrape

# collecting games' links for selected years and platform
game_links = []
for year in years:
    driver.get(
        f'https://www.metacritic.com/browse/games/score/metascore/year/{platform}/filtered?year_selected={year}&page=0')
    driver.implicitly_wait(5)
    num_pages = driver.find_element_by_css_selector('li.page.last_page > a.page_num').text
    pages = list(range(0, int(num_pages)))

    for page in pages:
        driver.get(
            f'https://www.metacritic.com/browse/games/score/metascore/year/{platform}/filtered?year_selected={year}&page={page}')
        select_links = driver.find_elements_by_css_selector('a.title')
        links = [link.get_attribute('href') for link in select_links]
        game_links.extend(links)

# visiting each link and scraping the data
all_games = []
for link in game_links:

    scraped = {
        'platform': platform
    }

    driver.get(link)

    try:
        scraped['title'] = driver.find_element_by_css_selector('div.product_title > a.hover_none').text
        scraped['meta_score'] = driver.find_element_by_xpath('//span[@itemprop="ratingValue"]').text
        scraped['user_score'] = driver.find_element_by_css_selector(
            'div.userscore_wrap.feature_userscore > a.metascore_anchor').text
        scraped['num_critics'] = driver.find_element_by_xpath('//a[contains(@href,"/critic-reviews")]/span').text
        scraped['num_users'] = driver.find_element_by_xpath('//p/span/a[contains(@href,"/user-reviews")]').text

        genres = driver.find_elements_by_css_selector('li.summary_detail.product_genre > span.data')
        scraped['genres'] = [genre.text for genre in genres]

        scraped['developer'] = driver.find_element_by_css_selector('li.summary_detail.developer > span.data').text
        scraped['release_date'] = driver.find_element_by_css_selector('li.summary_detail.release_data > span.data').text
    except NoSuchElementException as exc:
        print(link, exc)

    all_games.append(scraped)
    sleep(2)

# saving the data as a .csv file
df = pd.DataFrame(all_games)
df.to_csv(platform + '.csv', index=False)
driver.quit()
