# Scrip original:https://github.com/fake-news-detector/scrappers

import requests
from bs4 import BeautifulSoup
import unicodedata
import pandas as pd
from datetime import date
import re
import csv

site = "boatos.org"
search_query = '/tag/coronavirus'

def get_soup(url):
    page = requests.get(url)
    return BeautifulSoup(page.text, 'html.parser')

def should_ignore_paragraph(child):
    parent = child.parent
    if parent.name != 'p':
        parent = parent.parent
    p = parent.get_text()
    return ("Ps.:" in p or "PS:" in p or "PS.:" in p or "Se você quiser sugerir" in p or
            "Usted puede sugerir" in p or "Este artículo fue una sugerencia" in p)

def get_description_article(soup):
    text = soup.select('#content div[class="entry-content clearfix"] p strong')
    if text == []:
       text = soup.select('#content div[class="entry-content clearfix"] p b') 
    text = text[0].get_text()
    text = text.replace('Boato – ', '')
    return text


def scrape_hoax(link):
    print('> Scrapping', link)
    soup = get_soup(link)

    paragraphs = [
        p.get_text() for p in soup.select('#content [style="color: #ff0000;"]')
    ]
    
    if len(paragraphs) == 0:
        paragraphs = [p.get_text()
                      if not should_ignore_paragraph(p) else ""
                      for p in soup.select('#content em')]

    title = soup.find('title').get_text()
    classification = None
    rows = [
            'link',
            'timestamp',
            'title',
            'text',
            'classification'
        ]
    df2 = pd.DataFrame(columns=rows)

    paragraphs = ' '.join(paragraphs)
    paragraphs = paragraphs.strip()
    paragraphs = paragraphs.replace('Se inscreva no nosso canal no Youtube', '')

    print('---BEFORE---')
    print(paragraphs)

    if 'Versão' in paragraphs:
        paragraphs = re.sub('([1-9]:)', '', paragraphs)
        paragraphs = paragraphs.split('Versão')           
    elif 'versão' in paragraphs:
        paragraphs = re.sub('([1-9]:)', '', paragraphs)
        paragraphs = paragraphs.split('versão')
    elif 'Mensagem que circula online:' in paragraphs and 'Texto no site:' in paragraphs:
        paragraphs = paragraphs.replace('Mensagem que circula online:', '')
        paragraphs = paragraphs.split('Texto no site:')
    elif link == 'https://www.boatos.org/mundo/presidente-china-xi-jinping-discurso-nova-era-exercito-guerra-inevitavel.html':
        paragraphs = paragraphs.split('estejamos prontos ou não.')
        paragraphs[0] = paragraphs[0] + 'estejamos prontos ou não.'
    elif link == 'https://www.boatos.org/mundo/sopa-morcego-wuhan-china-causa-coronavirus.html':
        paragraphs = paragraphs.split('oficial”.')
        paragraphs[0] = paragraphs[0] + 'oficial”.'
    elif link == 'https://www.boatos.org/brasil/crianca-registrada-nome-alquingel-homenagem-covid-19-espirito-santo.html':
        paragraphs = paragraphs.split('pega?')
        paragraphs[0] = paragraphs[0] + 'pega?'
    else:
        paragraphs = paragraphs.split('”.')
    
    print('----AFTER----')
    print(paragraphs)
    
    if '#boato' in title:
        title = title.replace('#boato', '')
        classification = 1

        time = soup.select_one('time[datetime]')
        timestamp = pd.to_datetime(time['datetime'])
        
        i = -1
        for idx, paragraph in enumerate(paragraphs):
            if paragraph != 'Se inscreva no nosso canal no Youtube' and paragraph != '[…]':
                p = paragraph
                df2.loc[idx] = [link] + [timestamp] + [title] + [p] + [classification]
                i += 1
        if i == -1:
            p = get_description_article(soup)
            df2.loc[idx] = [link] + [timestamp] + [title] + [p] + [classification]
    else:
        print('Not fake news')
  
    return df2

def find_links_from_search_page(url):
    soup = get_soup(url)
    links = [a['href'] for a in soup.select('.more-link')]
    return links

def scrape_search_for_links(page_index):
    print('Scrapping page', page_index)
    links = find_links_from_search_page('http://www.' + site + search_query + '/page/' +
                                        str(page_index))
    print('> Found', len(links), 'links for page', page_index)
    return links

def get_struct_boatos(df):
    
    return {'link': df[1][1],
            'date': df[1][2].replace('-03:00', ''),
            'title': df[1][3],
            'text': df[1][4],
            'classification': df[1][5]
            }

if __name__ == "__main__":
    initial_page = 1
    final_page = 14  # View in site the numbers of pages
    print('Start scrapping ', site, 'from page', initial_page, 'to', final_page)

    all_links = []
    for number_page in range(initial_page, final_page):
        all_links.extend(scrape_search_for_links(number_page))
    cont_links = len(all_links)
    print('> Found', cont_links, 'total')

    rows = [
        'link',
        'timestamp',
        'title',
        'text',
        'classification'
    ]

    df = pd.DataFrame(columns=rows)
    t = 1

    """ link_test = 'https://www.boatos.org/politica/toffoli-maia-alcolumbre-quarentena-pacto-derrubar-bolsonaro.html'
    teste = scrape_hoax(link_test)
    print(teste) """

    for link in all_links:
        print ('> Link %d to %d' %(t, cont_links))
        df2 = scrape_hoax(link)
        if df2.shape[0] > 0:
            df = df.append(df2, ignore_index = True)
        t += 1

    df = pd.DataFrame(df)
    today = date.today()
    name = site + '-' + str(today) + ".csv" 

    df.to_csv(name, encoding='utf-8')

    dataset1 = pd.read_csv(name, encoding='utf-8')
    columns = ['link',
                'date',
                'title',
                'text',
                'classification']

    df = pd.DataFrame(columns=columns)

    print("Lets go clean")
    for row in dataset1.iterrows():
        df = df.append(get_struct_boatos(row), ignore_index = True)

    df.columns = df.columns.str.strip()
    df = df[df['text'].notnull()]
    df = df[df['classification'] == 1]
    df.drop_duplicates(subset=['text'], keep = False, inplace = True)

    df.to_csv('clean-' + name)
    print("The end!")
    