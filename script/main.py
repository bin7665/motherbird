'''
http://www.detizen.com/	- 대티즌
https://www.campuspick.com/contest - 캠퍼스픽
https://linkareer.com/list/contest - 링커리어
http://gongmo.incruit.com/ - 인크루트
http://www.spectory.net/contest - 스펙토리
https://www.culture.go.kr/bigdata/user/board/list.do?board_code=contest - 빅데이터 마켓
https://www.wevity.com/?c=find - 위비티
https://dacon.io/ - 데이콘
https://campusmon.jobkorea.co.kr/ - 캠퍼스몬
https://www.all-con.co.kr/ - 올콘테스트
https://www.gov.kr/portal/cnstexhb - 정부24
https://www.thinkcontest.com/ - 씽굿
https://www.contestkorea.com/main/index.php - 콘테스트 코리아
'''

import io
import os
import csv
import requests
from selenium import webdriver
from bs4 import BeautifulSoup
from PIL import Image


def driver_options():
    # chrome driver options
    options = webdriver.ChromeOptions()
    options.add_argument('headless')
    options.add_argument('window-size=1920x1080')
    options.add_argument("disable-gpu")

    # add UserAgent
    options.add_argument("user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.100 Safari/537.36")

    return options

def get_driver(driver, url):
    driver.get(url)
    driver.implicitly_wait(3)
    return driver

def run_driver(path, options, url):
    # run chrome driver
    print("Initialize driver")
    driver = webdriver.Chrome(path, options=options)
    driver = get_driver(driver, url)
    return driver

def get_soup(driver):
    # html parser
    html = driver.page_source
    soup = BeautifulSoup(html, 'html.parser')
    return soup

def get_column_urls(soup):
    # get column urls
    columns = soup.select('section.widget-contest > div.widget-contents > ul > li > div.main-info > h4 > a.btn-blank')
    col_urls = []
    for column in columns:
        col_urls.append(column['href'])
    return col_urls

def pagination(driver, soup, url):
    # get pages and crawling
    col_urls = []
    last_page = soup.select('div.pager-slider > a')[-2].text
    print(f"There are {last_page} pages")
    for i in range(int(last_page)):
        temp_url = url.format(i+1)
        print(f"get page {i+1} columns: {temp_url}")

        d = get_driver(driver, temp_url)
        s = get_soup(d)
        col_urls += get_column_urls(s)

    print("-----------------------------------------------")
    print(f"There are {len(col_urls)} activities")
    return col_urls

def check_directory(path):
    try:
        if not os.path.exists(path):
            os.makedirs(path)
    except Exception as e:
        print(f"ERROR: Can't make directory - {e}")

def get_post_image(url, path, name):
    # get image and save it
    try:
        image_content = requests.get(url).content
    except Exception as e:
        print(f"ERROR: Could not download {url} - {e}")
        return 0

    try:
        image_file = io.BytesIO(image_content)
        post_image = Image.open(image_file).convert('RGB')
        check_directory(path)
        file_path = os.path.join(path, name + ".jpg")
        with open(file_path, 'wb') as f:
            post_image.save(f, "JPEG", quality=85)
        # print(f"SUCCESS - saved {url} - as {file_path}")
        return file_path

    except Exception as e:
        print(f"ERROR: Could not save {url} - {e}")
        return 0

def get_activity_data(soup, path, url, name):
    # get activity datas
    activity_name = soup.find('span', {'class': 'on'}).text

    image_url = soup.find('a', {'class': 'btn-layout btn-radius-3'})['href']
    image_path = get_post_image(url + image_url, path, name)

    activity_table = soup.select('tbody > tr > td')
    categories = ",".join(activity_table[0].text.replace("#", "").split(", "))
    host = activity_table[1].text

    try:
        link = activity_table[8].find('a')['href']
    except:
        link = ""

    date = activity_table[3].text.strip().split(" ")
    start_date = date[0]
    end_date = date[2].split("\n")[0]
    info = soup.find('ul', {'class': 'summary-info'})

    return {'activity_name': activity_name, 'image_path': image_path, 'categories': categories, 'host': host, 'link': link, 'start_date': start_date, 'end_date': end_date, 'information': info}




csv_headers = ['activity_name', 'image_path', 'categories', 'host', 'link', 'start_date', 'end_date', 'information']
contest_datas = {0: {'name': '대티즌',
                     'url': 'http://www.detizen.com',
                     'base': 'http://www.detizen.com/contest/?IngYn=Y&PC={0}'}}

# test values, urls, page and path
PAGE = 1
URL = "http://www.detizen.com"
BASE_URL = "http://www.detizen.com/contest/?IngYn=Y&PC={0}"
START_URL = BASE_URL.format(PAGE)           # http://www.detizen.com/contest/?IngYn=Y&PC=1
PATH = "C:/Crwaling/activities/대티즌"

# to ignore Image.DecompressionBombWarning
Image.MAX_IMAGE_PIXELS = None

# initialize crawler
chromedriver = "C:/Program Files (x86)/Google/Chrome/Application/chromedriver.exe"
options = driver_options()
driver = run_driver(chromedriver, options, START_URL)
soup = get_soup(driver)
col_urls = pagination(driver, soup, BASE_URL)

# initialize csv
check_directory(PATH)
f = open(PATH + '/대티즌.csv', 'w', newline='')
csv_writer = csv.writer(f)
csv_writer.writerow(csv_headers)

count = 0
for col in col_urls:
    # get activity datas
    activity_url = START_URL + '&' + col[1:]
    driver = get_driver(driver, activity_url)
    soup = get_soup(driver)
    activity_data = get_activity_data(soup, PATH + '/images', URL, col[5:])
    csv_writer.writerow(activity_data.values())

    # check progress
    count += 1
    if count % 5 == 0:
        print(f"get {count} acitvity datas")

    # for test values
    # print(activity_data)
    # break

print("Crwaling is done!!!")
driver.quit()


# test codes
# print(col_urls)
# print(activity_data)
