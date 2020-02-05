import requests
from bs4 import BeautifulSoup as bs
#search = 'php'
search = input('Введите название вакансии: ')
sites = {
    'superjob': {
        'search_link': f'https://www.superjob.ru/vacancy/search/?keywords={search}&geo%5Bc%5D%5B0%5D=1',
        'base_url': 'https://www.superjob.ru',
    },
    'hh': {
        'search_link': f'https://mukachevo.hh.ua/search/vacancy?L_save_area=true&clusters=true&currency_code=UAH&enable_snippets=true&search_field=name&text={search}&showClusters=true',
        'base_url': 'https://hh.ua',
    }
}

# hh.ru не могу сделать, т.к. отдаёт 404 через requests. В браузере всё нормально.
# '<html>
# <head><title>404 Not Found</title></head>
# <body>
# <center><h1>404 Not Found</h1></center>
# <hr><center>nginx</center>
# </body>
# </html>
# '
#pages = 2
pages = int(input('Введите кол-во страниц для поиска: '))
results = []
for site in sites:
    search_link = sites[site]['search_link']
    for i in range(pages):
        response = requests.get(search_link)
        soup = bs(response.text, 'lxml')
        items = []
        if sites[site]['base_url'] == 'https://www.superjob.ru':
            items = soup.find_all('div', class_='f-test-vacancy-item')
        # elif sites[site]['base_url'] == 'https://kiev.hh.ua':
        #     items = soup.find_all('div', class_='f-test-vacancy-item') # todo
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
                                min_salary = '0'
                        else:
                            if 'от' in min_salary:
                                min_salary = min_salary
                    min_salary = ''.join([s for s in min_salary.split() if s.isdigit()])
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
                                max_salary = '0'
                    max_salary = ''.join([s for s in max_salary.split() if s.isdigit()])
                link_tag = item.find('a', class_='icMQ_')
                link = ''
                if link_tag:
                    link = link_tag.get('href')
                result = {
                    'name': name,
                    'min_salary': min_salary,
                    'max_salary': max_salary,
                    'link': sites[site]['base_url'] + link,
                    'site': sites[site]['base_url']
                }
                results.append(result)
        if sites[site]['base_url'] == 'https://www.superjob.ru':
            next_page_url = soup.find('a', class_='f-test-button-dalshe').get('href')
            if next_page_url:
                search_link = sites[site]['base_url'] + next_page_url
            else:
                break
        # elif sites[site]['base_url'] == 'https://kiev.hh.ua':
        #     next_page_url = soup.find('a', class_='f-test-button-dalshe').get('href') # todo
        #     if next_page_url:
        #         search_link = sites[site]['base_url'] + next_page_url
        #     else:
        #         break
        else:
            break


print(results)




