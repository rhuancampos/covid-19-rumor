# Importing the required libraries.
import re, csv, pandas as pd, numpy as np, time
import os.path
import requests
from bs4 import BeautifulSoup
from datetime import date

########################################################################
# 1. Defining the required functions
########################################################################      
def get_soup(url):
    try:
        page = requests.get(url)
    except:
        return None
    return BeautifulSoup(page.text, 'html.parser')

def get_data(links, name_file, rows):
    df = pd.DataFrame(columns=rows)
    df.to_csv(name_file)
    
    print('Get datas')

    for idx, link in enumerate(links):
        print('URL > ' + link)
        print(idx)
        
        # Getting the web page.
        
        html_soup = get_soup(link)
        if html_soup != None:
            # Title.
            if html_soup.find("h1", class_="content-head__title"):
                title = html_soup.find("h1", class_="content-head__title").string
            elif html_soup.find("h1", class_="c-open__title"):
                title = html_soup.find("h1", class_="c-open__title").string
            else:
                title = ''

            # Subtitle.
            if html_soup.find("h2", class_="content-head__subtitle"):
                subtitle = html_soup.find("h2", class_="content-head__subtitle").string
            elif html_soup.find("p", class_="c-open__subtitle"):
                title = html_soup.find("p", class_="c-open__subtitle").string
            else:
                subtitle = ""

            # Authors.
            if html_soup.find("p", class_="content-publication-data__from"):
                author = html_soup.find("p", class_="content-publication-data__from").string
                author = str(author).replace('Por', '')
            else:
                author = ""

            # Date of Publication.
            if html_soup.find("p", class_="content-publication-data__updated"):
                time = html_soup.select_one('time[datetime]')
                date = pd.to_datetime(time['datetime'])
            else:
                date = ""
            
            classification = 0  

            df2 = pd.DataFrame([[idx, link, date, title, subtitle, author,classification]],
                                columns = rows)     

            df2.to_csv(name_file, mode='a', header=False, index=False)

    print('End get datas')

def find_links_from_search_page(url):
    soup = get_soup(url)
    links = [a['href'] for a in soup.select('.feed-post-link')]
    return links

def scrape_search_for_links(url, cont):
    if cont != 1:
        url = url + 'index/feed/pagina-'+str(cont)+'.ghtml'
    print('Scrapping page', cont)
    links = find_links_from_search_page(url)
    print('> Found', len(links), 'links for page', cont)
    return links

def main(url):
    cont = 1
    all_links = []
    while 1:
        links = scrape_search_for_links(url, cont)
        if links:
            all_links.extend(links)
            cont += 1
        else:
            break
    cont_links = len(all_links)
    print('> Found', cont_links, 'total')
    
    with open("links_bkp.txt", "w") as file:
        file.writelines([link + "\n" for link in all_links])

    today = date.today()
    name_file = 'g1-' + str(today) + '.csv'
    rows = [
            'link',
            'date',
            'title',
            'subtitle',
            'author',
            'classification'
    ]
    get_data(all_links, name_file, rows)


########################################################################
# 2. Getting the data from its URL
########################################################################

# Determining the URL of target page.
url = "https://g1.globo.com/bemestar/coronavirus/"

main(url)
