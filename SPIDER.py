import requests
from bs4 import BeautifulSoup
import time
import re
import pymysql
from channel import channel  # 这是我们第一个程序爬取的链接信息
import random
from random import choice

# 用户代理
hds = [{
    'User-Agent': 'Mozilla/5.0 (Windows; U; Windows NT 6.1; en-US; rv:1.9.1.6) Gecko/20091201 Firefox/3.5.6'
},
    {
        'User-Agent': 'Mozilla/5.0 (Windows NT 6.2) AppleWebKit/535.11 (KHTML, like Gecko) Chrome/17.0.963.12 Safari/535.11'
    },
    {
        'User-Agent': 'Mozilla/5.0 (compatible; MSIE 10.0; Windows NT 6.2; Trident/6.0)'
    },
    {
        'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/69.0.3497.100 Safari/537.36'
    }
]


def get_header():
    return choice(hds)

#获取代理IP
def get_ip():
    #获取代理IP，返回列表
    httpResult=[]
    httpsResult=[]
    try:
        for page in range(1,2):
            IPurl = 'http://www.xicidaili.com/nn/%s' %page
            headers = get_header()
            rIP=requests.get(IPurl,headers=headers)
            IPContent=rIP.text.encode("utf-8")
            # print(IPContent)
            soupIP = BeautifulSoup(IPContent,'html.parser')
            trs = soupIP.find_all('tr')
            for tr in trs[1:]:
                tds = tr.find_all('td')
                ip = tds[1].getText()
                port = tds[2].getText()
                protocol = tds[5].getText()
                if protocol == 'HTTP':
                    httpResult.append( 'http://' + ip + ':' + port)
                elif protocol == 'HTTPS':
                    httpsResult.append( 'https://' + ip + ':' + port)
    except:
        pass
    return httpResult

def get_book_comments(url):
    hd = get_header()
    wb_data = requests.get(url, headers=hd)
    soup = BeautifulSoup(wb_data.text.encode("utf-8"), "html.parser")


def get_book_reviews(url):
    hd = get_header()
    wb_data = requests.get(url, headers=hd)
    soup = BeautifulSoup(wb_data.text.encode("utf-8"), "html.parser")

def ceshi_person(person):
    try:
        person = person.get_text().split()[0][1:len(person.get_text().split()[0]) - 4]
    except ValueError:
        person = 10
    return person


def ceshi_priceone(detil):
    price = detil.get_text().split("/", 4)[4].split()
    if re.match("USD", price[0]):
        price = float(price[1]) * 6
    elif re.match("CNY", price[0]):
        price = price[1]
    elif re.match("\A$", price[0]):
        price = float(price[1:len(price)]) * 6
    else:
        price = price[0]
    return price


def ceshi_pricetwo(detil):
    price = detil.get_text().split("/", 3)[3].split()
    if re.match("USD", price[0]):
        price = float(price[1]) * 6
    elif re.match("CNY", price[0]):
        price = price[1]
    elif re.match("\A$", price[0]):
        price = float(price[1:len(price)]) * 6
    else:
        price = price[0]
    return price


def get_book_infor(url): #进入到www.douban.com/subject/获取图书的详细信息
    re = []
    print(url)
    hd = get_header()
    ip_length = len(ips)-1
    ip_index = random.randint(0, ip_length)#选择一个随机IP
    proxies = {'http': ips[ip_index]}
    wb_data = requests.get(url, proxies=proxies,headers=hd)
    soup = BeautifulSoup(wb_data.text.encode("utf-8"), "html.parser")

    info = soup.find('div', {'id': 'info'})
    intro = soup.find_all('div', {'class': 'intro'})
    tag = soup.find_all('a', {'class': 'tag'})
    img_l = soup.find('a', {'class': 'nbg'})

    info = info.get_text().split()
    if len(intro) >= 1:
        re.append((intro[0].get_text()[1:]).encode('utf8'))
    else:
        re.append('')
    if len(intro) >= 2:
        re.append((intro[1].get_text()[1:]).encode('utf8'))
    else:
        re.append('')
    re.append(info[len(info)-1])
    re.append(img_l.find('img').get('src'))
    tags = ''

    for t in tag:
        tags = tags + t.get_text() + '/'

    re.append(tags)

    return re         #返回包含[book_intro, author_intro, isbn, img_l, tags]
    # comments_url = url + 'comments/'
    # reviews_url = url + 'reviews/'
    # get_book_comments(comments_url)
    # get_book_reviews(reviews_url)

#在www.douban.com/tag/页面获取初步书籍信息
def mains(url):
    hd = get_header()
    ip_length = len(ips)-1
    ip_index = random.randint(0, ip_length)#选择一个随机代理IP
    print(ip_index, ip_length)
    proxies = {'http': ips[ip_index]}
    wb_data = requests.get(url, proxies=proxies, headers=hd)
    print(wb_data)
    soup = BeautifulSoup(wb_data.text.encode("utf-8"), "html.parser")

    detils = soup.select("#subject_list > ul > li > div.info > div.pub")
    scors = soup.select("#subject_list > ul > li > div.info > div.star.clearfix > span.rating_nums")
    persons = soup.select("#subject_list > ul > li > div.info > div.star.clearfix > span.pl")
    titles = soup.select("#subject_list > ul > li > div.info > h2 > a")
    content = soup.select("#subject_list > ul > li > div.info > p")
    information = []
    for detil, scor, person, titl, conten in zip(detils, scors, persons, titles, content):

        try:
            author = detil.get_text().split("/", 4)[0].split('\n')[3]
            translator = detil.get_text().split("/", 4)[1]
            publisher = detil.get_text().split("/", 4)[2]
            pubdate = detil.get_text().split("/", 4)[3].split()[0].split("-")[0]
            price = ceshi_priceone(detil)
            rating = scor.get_text() if True else ""
            numRaters = ceshi_person(person)
            title = titl.get_text().split()[0]
            info_url = titl.get('href')
            summary = conten.get_text()

        except IndexError:
            try:
                author = detil.get_text().split("/", 3)[0].split('\n')[3]
                translator = ""
                publisher = detil.get_text().split("/", 3)[1]
                pubdate = detil.get_text().split("/", 3)[2].split()[0].split("-")[0]
                price = ceshi_pricetwo(detil)
                rating = scor.get_text() if True else ""
                numRaters = ceshi_person(person)
                title = titl.get_text().split()[0]
                info_url = titl.get('href')
                summary = conten.get_text()

            except (IndexError, TypeError):
                continue

        except TypeError:
            continue


        intro = get_book_infor(info_url)
        information.append([rating, numRaters, author, pubdate, translator, publisher, title, summary, price] + intro)


    print(len(information), information)
    sql = "INSERT INTO doubanbooks values(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"  # 这是一条sql插入语句
    cur.executemany(sql, information)  # 执行sql语句，并用executemary()函数批量插入数据库中
    conn.commit()



# 这是通过api.daouban接口获取的主函数但是由于api.douban已经被关闭无法获取
# def mains(url):
#     wb_data = requests.get(url)
#     soup = BeautifulSoup(wb_data.text.encode("utf-8"), "html.parser")
#     content = wb_data.json()
#     print(content)
#     print(type(content))
#
#     for book in content['books']:
#         l = []
#         try:
#             rating = book['rating']['average']
#             numRaters = book['rating']['numRaters']
#             subtitle = book['subtitle']
#             author = '/'.join(book['author'])
#             pubdate = book['pubdate']
#             tags = '/'.join((tag['title'] for tag in book['tags'])) #将所有的标签生产一个字符串
#             origin_title = book['origin_title']
#             image_s = book['images']['small']
#             image_m = book['images']['medium']
#             image_l = book['images']['large']
#             translator = '/'.join(book['translator'])
#             publisher = book['publisher']
#             isbn10 = book['isbn10']
#             isbn13 = book.get('isbn13', None)
#             title = book['title']
#             alt_title = book['alt_title']
#             author_intro = book['author_intro']
#             summary = book['summary']
#             price = book['price']
#             l.append([rating, numRaters, subtitle, author, pubdate, tags, origin_title, image_s, image_m, image_l, translator, publisher, isbn10, isbn13, title, alt_title, author_intro, summary, price])
#             # 将爬取的数据依次填入列表中
#             sql = "INSERT INTO books values(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"  # 这是一条sql插入语句
#             cur.executemany(sql, l)  # 执行sql语句，并用executemary()函数批量插入数据库中
#             conn.commit()
#         except IndexError:
#             continue

# 主函数到此结束

#获取代理ip
ips = get_ip()

# 将Python连接到oracle中的python数据库中
# conn = cx_Oracle.connect('ill/ill123@10.3.210.74:1521/orcl')
# 将Python连接到MySQL中的python数据库中
conn = pymysql.Connect(
    host='188.131.247.10',
    port=3306,
    user="dwj",
    password="DWJ2128033qaz!",
    database="test",
    charset='utf8mb4'
)
cur = conn.cursor()

cur.execute('DROP TABLE IF EXISTS doubanbooks')  # 如果数据库中有books的数据库则删除
sql = """CREATE TABLE doubanbooks(    
        rating VARCHAR(255),
        numRaters VARCHAR(255), 
        author VARCHAR(255),
        pubdate VARCHAR(255),
        translator VARCHAR(255),
        publisher VARCHAR(255),
        title VARCHAR(255),
        summary VARCHAR(4000),
        price VARCHAR(255),
        boook_intro TEXT(10000),
        author_intro TEXT(10000),
        isbn13 VARCHAR(255),
        image_l VARCHAR(255),
        tags VARCHAR(255)
 )"""
cur.execute(sql)  # 执行sql语句，新建一个books的数据表

start = time.clock()  # 设置一个时钟，这样我们就能知道我们爬取了多长时间了
for urls in channel.split():
    urlss = [urls + "?start={}&type=T".format(str(i)) for i in range(0, 1000, 20)]  # 从channel中提取url信息，并组装成每一页的链接
    for url in urlss:
        mains(url)  # 执行主函数，开始爬取
        print(url)  # 输出要爬取的链接，这样我们就能知道爬到哪了，发生错误也好处理
        time.sleep(int(format(random.randint(0, 9))))  # 设置一个随机数时间，每爬一个网页可以随机的停一段时间，防止IP被封
end = time.clock()
print('Time Usage:', end - start)  # 爬取结束，输出爬取时间
count = cur.execute('select * from allbooks')
print('has %s record' % count)  # 输出爬取的总数目条数

# 释放数据连接
if cur:
    cur.close()
if conn:
    conn.close()