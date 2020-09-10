import pandas as pd 
import csv

def get_struct_boatos(df):
    
    return {'id': df[1][0],
            'link': df[1][1],
            'date': df[1][2].replace('-03:00', ''),
            'title': df[1][3],
            'text': df[1][4],
            'imageLink': '',
            'subtitle': '',
            'explanation': '',
            'source': '',
            'text_analysis': df[1][4],
            'classification': df[1][5]
            }

def get_struct_saude(df):
    return {'id': df[1][0],
            'link': df[1][1],
            'date': df[1][2],
            'title': df[1][3],
            'text': df[1][4],
            'imageLink': df[1][5],
            'subtitle': '',
            'explanation': '',
            'source': '',
            'text_analysis': df[1][4],
            'classification': df[1][6]
            }

def get_struct_oglobo(df):
    df[1][3] = df[1][3].replace('É #FAKE que ', '')
    df[1][3] = df[1][3].replace('É #FAKE ', '')

    df[1][2] = df[1][2].split('/ Atualizado')[0]
    df[1][2] = df[1][2].replace('-', '')
    date = df[1][2].replace('/', '-')

    return {'id': df[1][0],
            'link': df[1][1],
            'date': date,
            'title': df[1][3],
            'text': '',
            'imageLink': '',
            'subtitle': df[1][4],
            'explanation': df[1][5],
            'source': df[1][6],
            'text_analysis': df[1][3],
            'classification': df[1][7]
            }

path1 = 'new-boatos.org.csv'
path2 = 'saude.gov.csv'
path3 = 'oglobo.com.csv'

dataset1 = pd.read_csv(path1, encoding='utf-8')
dataset2 = pd.read_csv(path2, encoding='utf-8')
dataset3 = pd.read_csv(path3)

columns = ['id',
            'link',
            'date',
            'title',
            'text',
            'imageLink',
            'subtitle',
            'explanation',
            'source',
            'text_analysis',
            'classification']

df = pd.DataFrame(columns=columns)

for row in dataset1.iterrows():
    df = df.append(get_struct_boatos(row), ignore_index = True)

for row in dataset2.iterrows():
    df = df.append(get_struct_saude(row), ignore_index = True)

for row in dataset3.iterrows():
    df = df.append(get_struct_oglobo(row), ignore_index = True)

df = df[df['text_analysis'].notnull()]
df = df[df['classification'] == 1]
df.drop_duplicates(subset=['text_analysis'])

df.to_csv('data.mendeley.csv')