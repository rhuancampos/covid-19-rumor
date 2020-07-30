import requests
from bs4 import BeautifulSoup
import unicodedata
import pandas as pd
import numpy as np
import json
from PIL import Image
from PIL import ImageOps
import io
from io import BytesIO
from google.cloud import vision


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
    try:
        response = requests.get(url)
        img = Image.open(BytesIO(response.content))
    except:
        return -1
    return img

def get_text_img(url):
    path =  clean_img(url)
    if path == -1:
        return ''

    client = vision.ImageAnnotatorClient()
    print ('path > ' + path)
    with io.open('img/' + path, 'rb') as image_file:
            content = image_file.read()

    image = vision.types.Image(content=content)

    response = client.text_detection(image=image)
    p = response.text_annotations
    print('Texts:')

    texts = ''
    df = pd.DataFrame(columns=['description'])
    for text in p:
        df = df.append(
            dict(
                description=text.description
            ),
            ignore_index=True
        )

    texts = df['description'][0]
    texts = ''.join(texts)

    if response.error.message:
        raise Exception(
            '{}\nFor more info on error messages, check: '
            'https://cloud.google.com/apis/design/errors'.format(
                response.error.message))

    texts = texts.replace('\n',' ')
    return texts

def clean_img(url):
    
    img = get_img(url)
    if img == -1:
        return img
    path = url.replace('.','-')
    path = path.replace('/','')
    path = path.replace(':','')
    path =  path + '.jpg'
    if url != 'https://www.saude.gov.br/images/png/2019/janeiro/31/FakeNews-ervadoce.png':
        border = (0, 100, 0, 100)
        img = ImageOps.crop(img, border)

    img = img.convert('RGB')
    
    #font http://salgat.blogspot.com/2015/04/using-pythons-pil-library-to-remove.html
    pixdata = img.load()
    for y in range(img.size[1]):
        for x in range(img.size[0]):
            r, g, b = img.getpixel((x, y))  
            if (r < 42) and (g < 160) and (b < 22): 
                pixdata[x, y] = (255, 255, 255)  

    img.save('img\\' + path)
    return path

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

        pagination = '?limitstart=' + page
        urls = find_links_page(mont_url(search_query + pagination))

        all_querys.extend(urls)
        #print(all_querys)
    
    len_all_querys = len(all_querys)

    print('ALL OF QUERYS > %s' % len_all_querys)

    collect = [set()] * len_all_querys
    for index, query in enumerate(all_querys):
        print('Query > %s OF  %s' % (index + 1, len_all_querys))
        collect[index] = get_datas_pages(query)

    df = pd.DataFrame(collect)
    df.to_csv(site + ".csv")