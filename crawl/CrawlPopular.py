import logging
import os

import requests
from lxml import etree

from domain.Book import Book
from tools.Log import Log


class CrawlPopular:
    def __init__(self):
        self.root = 'https://www.bbiquge.net'
        url = self.root + '/top/monthvisit/'
        self.getList(url)

    def getHtml(self, url):
        headers = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) '
                                 'Chrome/99.0.4844.51 Safari/537.36',
                   'Connection': 'close'}
        response = requests.get(url, headers)
        # response.encoding = 'utf-8'
        response.encoding = 'gbk'
        return response.text

    def getList(self, url):
        html_str = self.getHtml(url)
        html = etree.HTML(html_str)
        # print(html)

        name_path = '//*[@id="main"]/div[1]/ul/li/a/text()'
        url_path = '//*[@id="main"]/div[1]/ul/li/a/@href'
        names = html.xpath(name_path)
        urls = html.xpath(url_path)
        if urls.count('/top/toptime/') != 0:
            names.insert(-2, '本站推荐')
        # print(names)
        # print(urls)
        # print(len(names), len(urls))
        for i in range(len(names)):
            self.getBooks(self.root + urls[i], names[i])
            break

    def getBooks(self, url, attr):
        html_str = self.getHtml(url)
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
            if i < 100:
                book.setAllList(i + 1)
            # print(urls[i])
            self.getBook(urls[i], book)
            break

    def getBook(self, url, book):
        html_str = self.getHtml(url)
        html = etree.HTML(html_str)
        # print(html_str)

        cover = html.xpath('//*[@id="picbox"]/div/img/@src')[0]
        urls = html.xpath('/html/body/div[4]/dl/dd/a/@href')
        status = html.xpath('//*[@id="info"]/p/span[2]/text()')[0]
        hot = html.xpath('//*[@id="info"]/p/span[1]/text()')[0]
        description = html.xpath('//*[@id="intro"]/text()')

        book.setHot(hot)
        book.setCover(self.downloadCover(cover))
        book.setStatus(status)
        book.setDescription(description)

        # print(urls)
        # print(title)
        # print(status)
        # print(hot)
        # print(description)
        # print(book.toString())

        for i in range(len(urls)):
            self.getChapter(url + urls[i], book)
            break

    def getChapter(self, url, book):
        htmlstr = self.getHtml(url)
        html = etree.HTML(htmlstr)
        # print(htmlstr)

        content = html.xpath('//*[@id="content"]/text()')
        del content[0]
        del content[0]
        print(content)

        # soup = BeautifulSoup(htmlstr, "lxml")
        # content = soup.find(id='content')
        # print(type(content))
        # temp = content.split("<br/><br/>")
        # print(temp)

    def downloadCover(self, url):
        headers = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) '
                                 'Chrome/99.0.4844.51 Safari/537.36'}

        log = Log()
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
