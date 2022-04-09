import logging
import math
import os

from concurrent import futures
from time import sleep
import cn2an
import requests
from lxml import etree

from domain.Book import Book
from domain.Chapter import Chapter
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


def get_chapter(url, book):
    print("正在爬取《" + book.name + "》" + url)
    html_str = get_html(url)
    html = etree.HTML(html_str)
    # print(html_str)

    temp = html.xpath('//*[@id="main"]/h1/text()')[0].replace(' ', '')
    content = html.xpath('//*[@id="content"]/text()')
    del content[0]
    del content[0]
    index = temp.find(u'章')
    if index != -1:
        str = temp[1:index]
        name = temp[index + 1:]
        id = math.trunc(cn2an.cn2an(str, 'smart'))
    else:
        name = temp
    # print(id, name)
    # print(content)

    chapter = Chapter(id, name, content)
    book.add_chapter(chapter)
    if content == '' or content is None:
        log.log(target='reptile', level=logging.INFO, msg="第" + id + "章" + "爬取成功")


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
    book.set_status(status)
    book.set_description(description)

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

    # 使用线程池爬取
    future_list = []
    executor = futures.ThreadPoolExecutor(max_workers=128)
    for i in range(len(urls)):
        fs = executor.submit(get_chapter, url + urls[i], book)
        future_list.append(fs)
    futures.wait(future_list)
    # print("*****************多线程已完成******************")
    # print(len(book.get_chapter()))

    # 输出到文本
    try:
        if not os.path.exists("doc/books/" + book.name):
            os.makedirs('doc/books/' + book.name)
        for chapter in book.get_chapter():
            path = 'doc/books/' + book.name + '/' + str(chapter.get_id()) + chapter.get_name() + '.txt'
            print(path)
            with open(path, 'w+') as file:
                for text in chapter.get_content():
                    file.write(text + '\n')
                file.close()
                print(path + '------------写入成功')
    except:
        log.log(target='reptile', level=logging.ERROR, msg="爬取小说《" + book.name + "》失败")


def get_books(url, attr):
    html_str = get_html(url)
    html = etree.HTML(html_str)

    category_path = '//*[@id="articlelist"]/ul[2]/li/span[1]/text()'
    url_path = '//*[@id="articlelist"]/ul[2]/li/span[2]/a/@href'
    name_path = '//*[@id="articlelist"]/ul[2]/li/span[2]/a/text()'
    author_path = '//*[@id="articlelist"]/ul[2]/li/span[3]/text()'
    word_path = '//*[@id="articlelist"]/ul[2]/li/span[5]/text()'
    recommend_path = '//*[@id="articlelist"]/ul[2]/li/span[6]/text()'
    update_path = '//*[@id="articlelist"]/ul[2]/li/span[7]/text()'

    categories = html.xpath(category_path)
    urls = html.xpath(url_path)
    names = html.xpath(name_path)
    authors = html.xpath(author_path)
    words = html.xpath(word_path)
    recommends = html.xpath(recommend_path)
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
        book = Book(categories[i], names[i], authors[i], words[i], recommends[i], updates[i])
        book.add_attribute(attr)
        get_book(urls[i], book)
        sleep(10)
        print("*********************************" + book.name + "爬取完毕************************************")
        # break


class CrawlPopular:
    def __init__(self):
        self.root = 'https://www.bbiquge.net'
        url = self.root + '/top/monthvisit/'
        self.get_list(url)

    def get_list(self, url):
        html_str = get_html(url)
        html = etree.HTML(html_str)
        # print(html)

        name_path = '//*[@id="main"]/div[1]/ul/li/a/text()'
        url_path = '//*[@id="main"]/div[1]/ul/li/a/@href'
        names = html.xpath(name_path)
        urls = html.xpath(url_path)
        if urls.count('/top/toptime/') != 0:
            names.insert(-2, '本站推荐')

        for i in range(len(names)):
            get_books(self.root + urls[i], names[i])
            break
