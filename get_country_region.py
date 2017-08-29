import requests
from bs4 import BeautifulSoup
import re
import sys
import sqlite3

reload(sys)
sys.setdefaultencoding('utf-8')

china_top_url = 'http://www.stats.gov.cn/tjsj/tjbz/xzqhdm/'


UA = "Mozilla/5.0 (Windows NT 6.3; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/49.0.2623.13 Safari/537.36"
header = {
    "User-Agent": UA,
    "Host": 'www.stats.gov.cn'
}


def create_table(cursor):
    sql = 'create table if not exists city(code text,name text)'
    cursor.execute(sql)


def insert_data(cursor, city_list):
    sql = 'insert into city(code,name) values(?,?)'

    for i in city_list:
        sql2 = "select code from city where code='%s'" % i[0]
        cursor.execute(sql2)
        if not cursor.fetchall():
            print i
            cursor.execute(sql, tuple(i))


def db_handle(city_list):
    conn = sqlite3.connect('./city.db')
    cursor = conn.cursor()
    create_table(cursor)
    insert_data(cursor, city_list)
    conn.commit()
    cursor.close()
    conn.close()


def get_child_page(content):
    soup = BeautifulSoup(content, "html.parser", from_encoding='utf-8')
    ret = soup.find_all('ul', attrs={'class': 'center_list_contlist'})
    for item in ret:
        soup_ul = BeautifulSoup(repr(item), "html.parser")
        ret_li = soup_ul.find_all('li')
        for i in ret_li:
            if i.a['href']:
                return i.a['href']


def get_city_info(content):
    soup = BeautifulSoup(content, "html.parser")
    ret = soup.find_all('p', attrs={'class': 'MsoNormal'})
    a = ''
    code_city = []
    for p in ret:
        code_str = []
        for i in p.children:
            if i.name == 'b':
                for string in i.stripped_strings:
                    code_str.append(string)
                #a = str(i).replace(u'\xa0', u' ').decode('utf-8')
                # print a
            else:
                for string in i.stripped_strings:
                    code_str.append(string)
                #a = str(i).replace(u'\xa0', u' ').decode('utf-8')
                pass
        if code_str:
            code_city.append(code_str)
        pass
    return code_city


def get_info():
    session = requests.Session()
    ret = session.get(china_top_url, headers=header)
    page_url = get_child_page(ret.content)
    if page_url:
        ret = session.get(china_top_url + page_url, headers=header)
        city_list = get_city_info(ret.content)
        db_handle(city_list)


if __name__ == '__main__':
    get_info()

    pass
