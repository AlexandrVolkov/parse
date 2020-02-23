import requests
from lxml import html
from pymongo import MongoClient
from pprint import pprint
from bs4 import BeautifulSoup as bs

#Сайты news.mail.ru и yandex.news заблокированы на Украине и не открываются без vpn

lenta_base_url = 'https://lenta.ru'
headers = {'User-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.116 Safari/537.36'}
response = requests.get(lenta_base_url, headers=headers)
response_text = html.fromstring(response.text)

results = list()
source_name = 'lenta.ru'
result = {
    'source_name': source_name,
    'title': response_text.xpath('//div[@class="first-item"]/h2/a/text()')[0],
    'url': lenta_base_url + response_text.xpath('//div[@class="first-item"]/h2/a/@href')[0],
    'published_at': response_text.xpath('//div[@class="first-item"]/h2/a/time/@datetime')[0],
}
results.append(result)


titles = response_text.xpath('//div[@class="item"]/a/text()')
urls = response_text.xpath('//div[@class="item"]/a/@href')
published_ats = response_text.xpath('//div[@class="item"]/a/time/@datetime')
articles_count = len(titles)
for i in range(articles_count):
    try:
        result = {
            'source_name': source_name,
            'title': titles[i],
            'url': lenta_base_url + urls[i],
            'published_at': published_ats[i],
        }
        results.append(result)
    except Exception:
        pass


client = MongoClient('localhost', 27017)
db = client.news
articles = db.articles
for doc in results:
    articles.update({'url': doc['url']}, doc, upsert=True)







