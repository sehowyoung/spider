import os
from concurrent import futures
from time import sleep

from lxml import etree

from crawl import CrawlPopular
from domain.Book import Book
from tools import mysql


def get_book(url, book):
    html_str = CrawlPopular.get_html(url)
    html = etree.HTML(html_str)
    # print(html_str)

    cover = html.xpath('//*[@id="picbox"]/div/img/@src')[0]
    urls = html.xpath('/html/body/div[4]/dl/dd/a/@href')
    status = html.xpath('//*[@id="info"]/p/span[2]/text()')[0]
    hot = html.xpath('//*[@id="info"]/p/span[1]/text()')[0]
    description = html.xpath('//*[@id="intro"]/text()')
    update = html.xpath('//*[@id="info"]/div[1]/text()[2]')[0][1:-2]

    book.set_update(update)
    book.set_hot(hot)
    book.set_cover(CrawlPopular.download_cover(cover))
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
    # print(update)
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
            fs = executor.submit(CrawlPopular.get_chapter, url + urls[i], book, i)
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
    # mysql.insert_top(id)
    if temp:
        for filename in files:
            f = open(os.path.join("doc/books/" + book.name, filename), 'r')
            content = f.read()
            # print(content)
            mysql.insert_chapter(id, filename, content)


def get_books(url, attr):
    html_str = CrawlPopular.get_html(url)
    html = etree.HTML(html_str)

    url_path = '//*[@id="main"]/div[3]/div/ul/li/span[1]/a/@href'
    name_path = '//*[@id="main"]/div[3]/div/ul/li/span[1]/a/text()'
    author_path = '//*[@id="main"]/div[3]/div/ul/li/span[2]/text()'

    urls = html.xpath(url_path)
    names = html.xpath(name_path)
    authors = html.xpath(author_path)

    # print(categories)
    print(urls)
    print(names)
    print(authors)
    # print(words)
    # print(recommends)
    # print(updates)
    # print(len(categories), len(urls), len(names), len(authors), len(words), len(recommends), len(updates))

    for i in range(len(urls)):
        book = Book(category=attr, name=names[i], author=authors[i])
        get_book(urls[i], book)
        sleep(1)
        if i == 15:
            break


# def _get(name):
#     key = str(name.encode('gbk')).upper().replace("\\X", '%')[2:][:-1]
#     html_str = CrawlPopular.get_html('https://www.bbiquge.net/modules/article/search.php?searchkey=' + key)
#     html = etree.HTML(html_str)
#
#     word_path = '//*[@id="articlelist"]/ul[2]/li/span[5]/text()'
#     update_path = '//*[@id="articlelist"]/ul[2]/li/span[7]/text()'
