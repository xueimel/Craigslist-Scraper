import urllib.request
import re
import sys
import tqdm
from tqdm import tqdm
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import NoSuchElementException


#
#opens the webpage with the query and sets topic, then finds all possible pages with more results.
#returns URLS
#
def query_url_retriever(url, queryIn, page_limit=None):
    #Controls headless Chrome browser
    opts = webdriver.ChromeOptions()
    opts.add_argument("--headless") # remove this line to see interaction with webdriver
    opts.add_argument("--log-level=3") # silences debug output from chomedriver

    #accesss the website
    driver = webdriver.Chrome(ATTENTION!! INSERT PATH TO CHROMEDRIVER HERE, chrome_options=opts) #insert relative path to chromedriver.exe
    driver.get(url)
    print("\nGetting Web Page(s) \nGathering Web Pages. Please wait...\n")

    #find query box and enter query input
    queryBox = driver.find_element_by_name('query')
    queryBox.send_keys(queryIn + '\n')

    #manage first page of results
    retrievedUrls = []
    retrievedUrls.append(driver.current_url)
    pages_opened=1

    #get how many pages to be read
    if(page_limit is None):
        try:
            tot_count_results = (driver.find_element_by_class_name("totalcount").text)
            tot_number_pages = set_count(int(tot_count_results))
        except(NoSuchElementException):
            tot_number_pages = 0

        #make progress bar with upper limit as number of pages
        pbar = tqdm(total=int(tot_number_pages), initial=1)

        #accessing and storing pages
        try:
            while(driver.find_element_by_partial_link_text('next')):#while another page hyperlink
                pages_opened+=1
                thing = driver.find_element_by_partial_link_text('next')
                thing.click()
                retrievedUrls.append(driver.current_url)
                pbar.update(1)
        except NoSuchElementException:
             return retrievedUrls

    #access the specified amount of pages
    else:
        try:
            #make progress bar
            pbar = tqdm(total=page_limit, initial=1)

            #access and storing pages
            while(driver.find_element_by_partial_link_text('next') and page_limit > pages_opened):
                pages_opened+=1
                thing = driver.find_element_by_partial_link_text('next')
                thing.click()
                retrievedUrls.append(driver.current_url)
                pbar.update(1)
        except NoSuchElementException:
             return retrievedUrls
        return retrievedUrls
    return retrievedUrls


#
#Parses retrieved pages for relevent information
#returns links, titles, and prices
#
def url_info_grab(url_in):
#opens webpage results and only pulls the neccessities
    sauce = urllib.request.urlopen(url_in)
    soup = BeautifulSoup(sauce, 'lxml') #parses raw html from webpage
    ind_item = soup.find_all('li', class_="result-row") # seperates individual search results
    item_scanner = BeautifulSoup(str(ind_item), 'lxml') # makes scanner for ind_item
    water = item_scanner.find_all('a', class_="result-title hdrlnk")
    ingredients = item_scanner.find_all('span', class_="result-meta") # contains prices
    tot_count_url = soup.find_all('span', class_="totalcount")

#captures url links
    links=[]
    ind = 0
    for html in water: #grabs html text with prices unseperated
        link = (re.findall("href=\"([\S]+.html)", str(html)))
        links.append(str(*link))# combines chars to form full url string
        ind+=1

#captures prices
    prices=[]
    temp=[]
    for i in range(len(ingredients)):
        temp.append(re.findall('(\$\d{1,4})', str(ingredients[i]))) #prices seperated from html
    temp = flatten_earth(temp) #insures proper format for output
    for t in range(len(temp)):
        temp1 = str(temp[t])
        if (temp1 == ""):
            temp[t] = "N/A"
            prices.append("N/A")
        else:
            prices.append(temp1)

#captures titles
    titles=[]
    for tit in range (len(links)):
        titles.append(re.findall(r'\/d\/([-\w]+)\/\d', links[tit]))
    titles = flatten_earth(titles) #insures proper format for output
    for i in range(len(titles)):
        temp = titles[i]
        titles[i] = (temp.replace("-", " "))

    return links, prices, titles


#
#updates global variable tot_number_pages
#
def set_count(tot_num_results):
    tot_number_pages = 0
    tot_number_pages = tot_num_results / 120 #number of items per page craigslist
    return tot_number_pages

#
#Some pages parse differently, this boils the parsed info and insures that it's not in a list format
#
def flatten_earth(round):
    flat = []
    for i in round:
        for j in i:
            flat.append(j)
    return flat


if __name__ == '__main__':
    to_b_ret = []
    ret_urls = []
    ret_info = []
    page_count = 0
    url = 'https://boise.craigslist.org/' #alter url for desired location
    orig_query = str(input("Enter query to be searched: "))
    max_page = str(input("There are 120 results per page, Enter maximum number of pages to be searched \n"
    + "(NOTE: if you have no desired amount, leave this entry blank):"))
    if max_page == "":
        ret_urls = query_url_retriever(url, orig_query)
    else:
        ret_urls = query_url_retriever(url, orig_query, int(max_page))
    print("*"*80)
    index = 1
    for i in range(len(ret_urls)):
        print("\nPAGE: ", i, "\n")
        links, prices, titles = url_info_grab(ret_urls[i])
        all = zip(prices, titles, links)
        if(len(prices)>0):
            for j in all:
                print(index,"\t", '{:20s}{:40s}{}'.format(*j))
                index+=1
        else:
            print("\nSorry, there were no results for the query you searched :(\n")
    print("*"*80)
