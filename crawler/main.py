import os

from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings

if __name__ == "__main__":

    spider = 'fussballdaten'

    os.environ['SCRAPY_PROJECT'] = spider
    settings = get_project_settings()
    process = CrawlerProcess(settings)

    process.crawl(spider)
    process.start()