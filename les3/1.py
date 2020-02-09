import requests
from pymongo import MongoClient
from pprint import pprint
from bs4 import BeautifulSoup as bs
search = 'php'
# search = input('Введите название вакансии: ')
sites = {
    'superjob': {
        'search_link': f'https://www.superjob.ru/vacancy/search/?keywords={search}&geo%5Bc%5D%5B0%5D=1',
        'base_url': 'https://www.superjob.ru',
    },
    # 'hh': {
    #     'search_link': f'https://mukachevo.hh.ua/search/vacancy?L_save_area=true&clusters=true&currency_code=UAH&enable_snippets=true&search_field=name&text={search}&showClusters=true',
    #     'base_url': 'https://hh.ua',
    # }
}



pages = 5
# pages = int(input('Введите кол-во страниц для поиска: '))
results = []
for site in sites:
    search_link = sites[site]['search_link']
    for i in range(pages):
        response = requests.get(search_link)
        soup = bs(response.text, 'lxml')
        items = []
        if sites[site]['base_url'] == 'https://www.superjob.ru':
            items = soup.find_all('div', class_='f-test-vacancy-item')
        else:
            break
        for item in items:
            if sites[site]['base_url'] == 'https://www.superjob.ru':
                name = item.find('div', class_='_3mfro').getText()
                salary_tag = item.find('span', class_='f-test-text-company-item-salary')
                salary = ''
                if salary_tag:
                    salary = salary_tag.getText()
                min_salary = salary
                if min_salary != 'По договорённости':
                    if '—' in min_salary:
                        min_salary = min_salary.split('—')[0]
                    else:
                        if 'до' in min_salary:
                            min_salary = min_salary.split('до')
                            if len(min_salary) > 1:
                                min_salary = min_salary[0]
                            else:
                                min_salary = None
                        else:
                            if 'от' in min_salary:
                                min_salary = min_salary
                    if min_salary:
                        min_salary = ''.join([s for s in min_salary.split() if s.isdigit()])
                else:
                    min_salary = None
                max_salary = salary
                if max_salary != 'По договорённости':
                    if '—' in max_salary:
                        max_salary = max_salary.split('—')[1]
                    else:
                        if 'до' in max_salary:
                            max_salary = max_salary.split('до')
                            if len(max_salary) > 1:
                                max_salary = max_salary[1]
                            else:
                                max_salary = max_salary[0]
                        else:
                            if 'от' in max_salary:
                                max_salary = None
                    if max_salary:
                        max_salary = ''.join([s for s in max_salary.split() if s.isdigit()])
                else:
                    max_salary = None
                link_tag = item.find('a', class_='icMQ_')
                link = ''
                if link_tag:
                    link = link_tag.get('href')

                if min_salary:
                    min_salary = int(min_salary)
                if max_salary:
                    max_salary = int(max_salary)
                result = {
                    'name': name,
                    'min_salary': min_salary,
                    'max_salary': max_salary,
                    'link': sites[site]['base_url'] + link,
                    'site': sites[site]['base_url']
                }
                results.append(result)
        if sites[site]['base_url'] == 'https://www.superjob.ru':
            a = soup.find('a', class_='f-test-button-dalshe')
            next_page_url = None
            if a:
                next_page_url = a.get('href')
            if next_page_url:
                search_link = sites[site]['base_url'] + next_page_url
            else:
                break
        else:
            break


def upsert_records(collection, records):
    collection.create_index([('link', 1)], unique=True)
    for doc in records:
        collection.update({'link': doc['link']}, doc, upsert=True)


def find_records_by_salary(collection, salary_from, salary_to):
    return collection.find({'min_salary':{'$gt':salary_from},'max_salary':{'$lt':salary_to}})


client = MongoClient('localhost', 27017)
db = client.job
vacancy = db.vacancy
upsert_records(vacancy, results)
filtered_records = find_records_by_salary(vacancy, 50000, 250000)
for filtered_record in filtered_records:
    pprint(filtered_record)





