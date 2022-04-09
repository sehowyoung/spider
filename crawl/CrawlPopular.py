import logging
import os
from concurrent import futures
from time import sleep

import requests
from lxml import etree

from domain.Book import Book
from domain.Chapter import Chapter
from tools import mysql
from tools.Log import Log

log = Log()
headers = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) '
                         'Chrome/99.0.4844.51 Safari/537.36',
           'Connection': 'close'}


def get_html(url):
    response = requests.get(url, headers)
    # response.encoding = 'utf-8'
    response.encoding = 'gbk'
    if response.status_code != 200:
        print("*********不能相应，状态码：" + str(response.status_code) + "**********")
    return response.text


def download_cover(url):
    path = 'doc/topList/cover/' + url.split('/')[-1]
    try:
        if not os.path.exists('doc/topList/cover/'):
            os.makedirs('doc/topList/cover/')

        if not os.path.exists(path):
            r = requests.get(url, headers=headers)
            with open(path, "wb") as f:
                f.write(r.content)
                f.close()
                log.log(target='download', level=logging.INFO, msg=url + '下载成功')
        else:
            log.log(target='download', level=logging.WARNING, msg=url + '已经存在')
    except:
        log.log(target='download', level=logging.ERROR, msg=url + '下载失败')
    return path


def get_chapter(url, book, index):
    html_str = get_html(url)
    html = etree.HTML(html_str)
    # print(html_str)

    name = html.xpath('//*[@id="main"]/h1/text()')[0]
    name = str(index) + '.' + name
    content = html.xpath('//*[@id="content"]/text()')
    del content[0]
    del content[0]
    con = ''
    for c in content:
        con = con + c + '\n'

    # print(content)

    chapter = Chapter(name, con)
    book.add_chapter(chapter)
    if content != '' or content is not None:
        log.log(target='reptile', level=logging.INFO, msg=name + "爬取成功")
        # print("爬取《" + book.name + "》\t" + name + "\t成功")
    try:
        if not os.path.exists("doc/books/" + book.name):
            os.makedirs('doc/books/' + book.name)
        path = 'doc/books/' + book.name + '/' + chapter.get_name() + '.txt'
        # print(path)
        with open(path, 'w+') as file:
            # print(content)
            for text in content:
                # print(text)
                file.write(text + '\n')
            file.close()
            print(path + '------------写入成功')
    except:
        log.log(target='reptile', level=logging.ERROR, msg="爬取小说《" + book.name + "》失败")


def get_book(url, book):
    html_str = get_html(url)
    html = etree.HTML(html_str)
    # print(html_str)

    cover = html.xpath('//*[@id="picbox"]/div/img/@src')[0]
    urls = html.xpath('/html/body/div[4]/dl/dd/a/@href')
    status = html.xpath('//*[@id="info"]/p/span[2]/text()')[0]
    hot = html.xpath('//*[@id="info"]/p/span[1]/text()')[0]
    description = html.xpath('//*[@id="intro"]/text()')

    book.set_hot(hot)
    book.set_cover(download_cover(cover))
    if status == '连载中':
        book.set_status(1)
    else:
        book.set_status(0)
    desc = ''
    for i in description:
        desc = desc + i + '\n'
    # print(desc)
    book.set_description(desc)

    # print(len(urls), urls[-1])
    # print(title)
    # print(status)
    # print(hot)
    # print(description)
    # print(book.tostring())

    # 单线程爬取
    # for i in range(len(urls)):
    #     print("正在爬取" + url + urls[i])
    #     get_chapter(url + urls[i], book)
    #     break

    # print(book.get_chapter())
    temp = True
    if len(mysql.select_book_by_name(book.name)) == 0:
        mysql.insert_book(book)
    else:
        temp = False

    # 使用线程池爬取
    if temp:
        future_list = []
        executor = futures.ThreadPoolExecutor(max_workers=100)
        if len(urls) > 500:
            num = 500
        else:
            num = len(urls)
        for i in range(num):
            fs = executor.submit(get_chapter, url + urls[i], book, i)
            future_list.append(fs)
        futures.wait(future_list)
    # print("*****************多线程已完成******************")
    # print(len(book.get_chapter()))

    # 输出到文本
    # try:
    #     if not os.path.exists("doc/books/" + book.name):
    #         os.makedirs('doc/books/' + book.name)
    #     for chapter in book.get_chapter():
    #         path = 'doc/books/' + book.name + '/' + chapter.get_name() + '.txt'
    #         # print(path)
    #         with open(path, 'w+') as file:
    #             for text in chapter.get_content():
    #                 file.write(text + '\n')
    #             file.close()
    #             print(path + '------------写入成功')
    # except:
    #     log.log(target='reptile', level=logging.ERROR, msg="爬取小说《" + book.name + "》失败")
    # print(book.tostring())
    # print(len(mysql.select_book_by_name(book.name)))
    files = os.listdir("doc/books/" + book.name)
    files.sort(key=lambda x: int(x.split('.')[0]))
    id = mysql.select_book_by_name(book.name)[0][0]
    mysql.insert_top(id)
    if temp:
        for filename in files:
            f = open(os.path.join("doc/books/" + book.name, filename), 'r')
            content = f.read()
            # print(content)
            mysql.insert_chapter(id, filename, content)


def get_books(url, attr):
    html_str = get_html(url)
    html = etree.HTML(html_str)

    category_path = '//*[@id="articlelist"]/ul[2]/li/span[1]/text()'
    url_path = '//*[@id="articlelist"]/ul[2]/li/span[2]/a/@href'
    name_path = '//*[@id="articlelist"]/ul[2]/li/span[2]/a/text()'
    author_path = '//*[@id="articlelist"]/ul[2]/li/span[3]/text()'
    word_path = '//*[@id="articlelist"]/ul[2]/li/span[5]/text()'
    update_path = '//*[@id="articlelist"]/ul[2]/li/span[7]/text()'

    categories = html.xpath(category_path)
    urls = html.xpath(url_path)
    names = html.xpath(name_path)
    authors = html.xpath(author_path)
    words = html.xpath(word_path)
    updates = html.xpath(update_path)

    # print(categories)
    # print(urls)
    # print(names)
    # print(authors)
    # print(words)
    # print(recommends)
    # print(updates)
    # print(len(categories), len(urls), len(names), len(authors), len(words), len(recommends), len(updates))

    for i in range(len(urls)):
        book = Book(categories[i], names[i], authors[i])
        book.set_word(words[i])
        book.set_update(updates[i])
        book.add_attribute(attr)
        get_book(urls[i], book)
        sleep(1)
        # if not os.path.exists("doc/books/" + book.name):
        #     get_book(urls[i], book)
        #     sleep(1)
        #     print("*********************************\t《" + book.name + "》爬取完毕\t************************************")
        # else:
        #     print("*********************************\t《" + book.name + "》\t已存在")
        #     continue
        # break


class CrawlPopular:
    def __init__(self):
        self.root = 'https://www.bbiquge.net'
        url = self.root + '/top/monthvisit/'
        self.get_list(url)

    def get_list(self, url):
        # html_str = get_html(url)
        # html = etree.HTML(html_str)
        # # print(html)
        #
        # name_path = '//*[@id="main"]/div[1]/ul/li/a/text()'
        # url_path = '//*[@id="main"]/div[1]/ul/li/a/@href'
        # names = html.xpath(name_path)
        # urls = html.xpath(url_path)
        # if urls.count('/top/toptime/') != 0:
        #     names.insert(-2, '本站推荐')
        #
        # for i in range(len(names)):
        #     url = self.root + urls[i] + str(1) + '.html'
        #     # print(url)
        #     get_books(url, names[i])
        #     break
        get_books('https://www.bbiquge.net/top/toptime/', 'recommends')
