import pandas as pd 
import csv

def get_struct_boatos(df):
    
    return {'id': df[1][0],
            'link': df[1][1],
            'date': df[1][2].replace('-03:00', ''),
            'title': df[1][3],
            'text': df[1][4],
            'classification': df[1][5]
            }

path1 = 'boatos.org.csv'

dataset1 = pd.read_csv(path1, encoding='utf-8')

columns = ['id',
            'link',
            'date',
            'title',
            'text',
            'classification']

df = pd.DataFrame(columns=columns)

print("Lets go")
for row in dataset1.iterrows():
    df = df.append(get_struct_boatos(row), ignore_index = True)


df = df[df['text'].notnull()]
df = df[df['classification'] == 1]
df.drop_duplicates(subset=['text'], keep = False, inplace = True)

df.to_csv('boatos.org-2021-01-11.csv')
print("The end!")