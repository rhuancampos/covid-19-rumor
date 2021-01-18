import pandas as pd 
import csv

path1 = 'g1-2021-01-15.csv'

df = pd.read_csv(path1, encoding='utf-8')

print("Lets go")
print(df.shape)
df = df[df['subtitle'].notnull()]
df = df[df['date'].notnull()]
df = df[df['classification'] == 0]
df.drop_duplicates(subset=['subtitle'], keep = False, inplace = True)
print(df.shape)

df.to_csv('clean-' + path1)
print("The end!")