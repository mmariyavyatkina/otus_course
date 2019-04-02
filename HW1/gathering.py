import logging
import sys
import requests
import json
import datetime
from ast import literal_eval
import pandas as pd
import matplotlib.pyplot as plt

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

SCRAPPED_FILE = 'scrapped_data.txt'
TABLE_FORMAT_FILE = 'data.csv'

def gather_process():
    logger.info("gather")
    
    # gathere data and save as txt
    access_token = '729b0277fb967bdce86ea3b62ea8470188e1c3914ce2dc7e147fcf1ea872967edde474f6b4838fe200094'
    owner_id = '29534144'
    count=100
    offset=-1
    result=[]

    for _ in range(20):
        url = 'https://api.vk.com/method/wall.get?owner_id=-{}&count={}&offset={}&v=5.52&access_token={}'.format(owner_id,count,offset+1,access_token)
        respond = requests.get(url)
        result.append(respond.json())
        offset+=count
        
    with open(SCRAPPED_FILE, 'w') as outfile:
        json.dump(result, outfile)

def convert_data_to_table_format():
    logger.info("transform")
    
    # transform gathered data from txt file to pandas DataFrame and save as csv
    result = literal_eval(open(SCRAPPED_FILE, 'r').read())
    n = 100
    l = len(result)
    ids = []
    dates = []
    comments = []
    likes = []
    reposts = []
    text = []

    for i in range(l):
        for j in range(n):
            ids.append(result[i]['response']['items'][j]['id'])
            dates.append(datetime.datetime.fromtimestamp(result[i]['response']['items'][j]['date']))
            comments.append(result[i]['response']['items'][j]['comments']['count'])
            likes.append(result[i]['response']['items'][j]['likes']['count'])
            reposts.append(result[i]['response']['items'][j]['reposts']['count'])
            text.append(result[i]['response']['items'][j]['text'].encode('utf-16','surrogatepass').decode('utf-16'))
            
            
    df = pd.DataFrame({
        "id": ids, 
        "date": dates, 
        "comments_count": comments, 
        "likes_count": likes,
        "reposts_count": reposts,
        "text": text,
    })

    df.to_csv(TABLE_FORMAT_FILE, sep='\t')
    pass

def stats_of_data():
    logger.info("stats")
    
    # Load pandas DataFrame and print to stdout different statistics about the data.
    df = pd.read_csv(TABLE_FORMAT_FILE, sep = '\t')
    df.describe()
    print('\n', '\033[1m' + '\n','Maximum likes (', df['likes_count'].max(), ') had the following news:' + '\033[0m', '\n')
    print(df['text'].iloc[df['likes_count'].idxmax()], '\n')
    print('\033[1m' + '\n','Maximum reposts (', df['reposts_count'].max(), ') had the following news:' + '\033[0m', '\n')
    print(df['text'].iloc[df['reposts_count'].idxmax()], '\n')
    print('\033[1m' + 'Maximum comments (', df['comments_count'].max(), ') had the following news:' + '\033[0m', '\n')
    print(df['text'].iloc[df['comments_count'].idxmax()], '\n')
    print('\033[1m' + '\n','Minimum likes (', df['likes_count'].min(), ') had the following news:' + '\033[0m', '\n')
    print(df['text'].iloc[df['likes_count'].idxmin()], '\n')



if __name__ == '__main__':
    """
    why main is so...?
    https://stackoverflow.com/questions/419163/what-does-if-name-main-do
    """
    logger.info("Work started")

    if sys.argv[1] == 'gather':
        gather_process()

    elif sys.argv[1] == 'transform':
        convert_data_to_table_format()

    elif sys.argv[1] == 'stats':
        stats_of_data()

    logger.info("work ended")