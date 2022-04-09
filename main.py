from crawl.CrawlByCategory import get_books
from crawl.CrawlPopular import CrawlPopular

if __name__ == '__main__':
    # hot = CrawlPopular()
    get_books('https://www.bbiquge.net/fenlei/3_1/', '都市小说')
