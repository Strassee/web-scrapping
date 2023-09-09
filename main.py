from bs4 import BeautifulSoup
import requests
import json
import re
import time

# https://github.com/netology-code/py-homeworks-advanced/tree/new_hw_scrapping/6.Web-scrapping
def get_vacs():
    # url = 'https://spb.hh.ru/search/vacancy?text=python&area=1&area=2'
    url = 'https://spb.hh.ru/search/vacancy'

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36 \
                        Improved debugging of missing stylesheets \
                        Find and fix issues with missing stylesheets with ease. \
                        Linear timing support in the Easing Editor \
                        Adjust the linear timing function for animations and transitions with a click in the Easing Editor. \
                        Storage buckets support and metadata view \
                        Application > Storage gets storage buckets support. Local, session, and cache storage sections get a unified metadata view.'


    }  

    payload = {
        'text' : 'python AND Django AND Flask',
        # 'text' : 'python',
        'area' : [1, 2],
        'page' : 0,
        'items_on_page' : 20
    }

    html = requests.get(url, headers=headers, data=payload)
    soup = BeautifulSoup(html.text,'html.parser')
    pattern = r"(?<=page=)(\d+)"
    pages = []
    a = soup.find_all('a', attrs={'data-qa' : 'pager-page'})
    for i in a:
        pages.append(int(re.search(pattern, i.get('href')).group()))

    pages.sort(reverse=True)
    # print(soup.find('h1', 'bloko-header-section-3').text)
    vacs = soup.find_all('div', 'vacancy-serp-item-body__main-info')
    for i in range(1, pages[0] + 1):
        time.sleep(0.1)
        payload['page'] = i
        html = requests.get(url, headers=headers, data=payload)
        soup = BeautifulSoup(html.text,'html.parser')
        vacs += soup.find_all('div', 'vacancy-serp-item-body__main-info')

    return vacs

def vac_json(vacs, usd = False):
    vacancies = {}
    i = 0
    for vac in vacs:
        sal = vac.find('span', attrs={'data-qa' : 'vacancy-serp__vacancy-compensation'}).text.replace(u'\u202f', u' ') \
                if vac.find('span', attrs={'data-qa' : 'vacancy-serp__vacancy-compensation'}) else 'Информация отсутствует'
        if usd and sal[-1] != '$':          
            continue
        vacancies[i] = {
                'Название вакансии' : vac.find('a', 'serp-item__title').text,
                'Вилка ЗП' : sal,
                'Компания' : vac.find('div', 'vacancy-serp-item__meta-info-company').text.replace(u'\xa0', u' '),
                'Город' : vac.find('div', attrs={'data-qa' : 'vacancy-serp__vacancy-address'}).text,
                'Ссылка' : vac.find('a', 'serp-item__title').get('href')
            }
        i += 1

    return vacancies
     
vacancies = vac_json(get_vacs(), usd = False)

with open("vacancies.json", "w", encoding="utf-8") as file:
    json.dump(vacancies, file, ensure_ascii=False)
    file.close()
