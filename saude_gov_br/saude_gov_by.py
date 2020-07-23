import requests
from bs4 import BeautifulSoup
import unicodedata
from multiprocessing import Pool
import pandas as pd
import json
import pytesseract
from PIL import Image
from io import BytesIO

site = "saude.gov.br"
search_query = '/component/tags/tag/novo-coronavirus-fake-news'

def get_soup(url):
    page = requests.get(url)
    return BeautifulSoup(page.text, 'html.parser')

def find_links_page(url):
    soup = get_soup(url)

    links = [a['href'] for a in soup.select('.list-title a')]
    for index, a in enumerate(links):
        links[index] = a.replace('?Itemid=101', '')

    return links

def mont_url(query):
    url = 'https://www.' + site + query
    print('Mont URL > ' + url)
    return url

def get_img(url):
    response = requests.get(url)
    img = Image.open(BytesIO(response.content))
    return img

def get_text_img(url):
    try:
        text = pytesseract.image_to_string(get_img(url), lang='por')
    except:
        return "Image error"
        
    return text

def get_datas_pages(query):
    url = mont_url(query)

    soup = get_soup(url)

    title = soup.select('h1[class="documentFirstHeading"]')[0]
    title = title.get_text()
    title = unicodedata.normalize("NFKD", title).strip()
    classification = None

    if '- É VERDADE!' in title:
        classification = 0
        title = title.replace('- É VERDADE!', '')
        print('IS TRUE!')

    if '- É FAKE NEWS!' in title:
        classification = 1
        title = title.replace('- É FAKE NEWS!', '')
        print('IS FAKE!')
    

    data = soup.select('[type="application/ld+json"]')[0]
    data = ''.join(data)

    theJson = json.loads(data)

    datePublished = theJson['datePublished']
    dateModified = theJson['dateModified']
    image = theJson['image']
    image = ''.join(image)
    image = mont_url(image)

    datePublished = pd.to_datetime(datePublished)
    dateModified = pd.to_datetime(dateModified)
    text = get_text_img(image)
    print('text > ' + text)


    return {'link': url, 'datePublished': datePublished, 'dateModified': dateModified,'title': title, 'text': text, 'linkImage': image, 'classification': classification}


if __name__ == "__main__":

    num_of_pages = 5
    all_querys = []
    for x in range(num_of_pages):
        page = str(x * 20)
        print (page)
        pagination = '?limitstart=' + page
        urls = find_links_page(mont_url(search_query + pagination))
        print(urls)
        all_querys.extend(urls)
        print(all_querys)
    
    len_all_querys = len(all_querys)

    print('ALL OF QUERYS > %s' % len_all_querys)

    collect = [set()] * len_all_querys
    for index, query in enumerate(all_querys):
        print('Query > %s OF  %s' % (index + 1, len_all_querys))
        collect[index] = get_datas_pages(query)

    df = pd.DataFrame(collect)
    df.to_csv(site + ".csv")





