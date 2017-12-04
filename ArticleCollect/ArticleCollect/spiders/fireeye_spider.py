# -*- coding: utf-8 -*-
#
# Project: ArticleCollect("https://www.fireeye.com/")
# author : xxx
# Update : 2017-11-30
#

# from w3lib.url import urljoin
import scrapy
# from ThreatCollect.items import ThreatcollectItem
from ArticleCollect.items import ArticlecollectItem
from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import CrawlSpider, Rule
import time
import re

class FireeyeSpider(CrawlSpider):
    name = 'fireeye'
    allowed_domains = ['www.fireeye.com']

    # start_urls = ["https://www.fireeye.com/blog/threat-research.html?blog_entries_start={}".format(str(i*5)) for i in range(1, 3)]
    start_urls = ["https://www.fireeye.com/blog/threat-research.html"]

    rules = [
        Rule(LinkExtractor(allow=('blog_entries_start=\d+')), callback='parse_item', follow=True),
    ]

    def parse_item(self, response):
        if not response.xpath('//ul[@class="blog"]//h2[@itemprop="headline"]/a[@href]'):
            return
        for blog_url in response.xpath('//ul[@class="blog"]//h2[@itemprop="headline"]/a/@href').extract():
            domians = 'https://www.fireeye.com'
            blog_url = domians + blog_url if 'http' not in blog_url else blog_url
            yield scrapy.Request(url=blog_url, headers=response.headers, dont_filter=True, callback=self.parse_content)


    def parse_content(self, response):
        item = ArticlecollectItem()
        item['url'] = response.url
        item['spider_time'] = time.time()
        item['html'] = None
        item['title'] = None
        item['content'] = None
        item['publisher'] = None
        item['publish_time'] = None
        item['article_id'] = None
        item['publisher_href'] = None
        item['img_urls'] = None
        item['prublisher_id'] = None

        html = response.xpath('/html').extract_first()
        item['html'] = html if html else None

        title = response.xpath('//div[@class="title entrytitle"]/h1[@itemprop="headline"]/text()').extract_first()
        item['title'] = title.encode('utf-8') if title else None

        publish_timeTmp = response.xpath('//div[@class="title entrytitle"]//time[@class="entry-date"]/text()').extract_first()
        if publish_timeTmp:
            publish_time = format_date(publish_timeTmp)
            item['publish_time'] = publish_time if publish_time else None

        publisher = response.xpath('//span[@class="by-author"]/a/text()').extract()
        item['publisher'] = ",".join(publisher).encode('utf-8') if publisher else None

        publisher_href = response.xpath('//span[@class="by-author"]/a/@href').extract()
        item['publisher_href'] = ",".join(publisher_href).encode('utf-8') if publisher_href else None

        content = response.xpath('.//div[@class="entrytext section"]').extract_first()
        item['content'] = content if content else None

        yield item


def format_date(value):
    if not value:
        return None
    str = value
    restr = r'.*\ .*,\ .*'        # time_value = "November 10, 2015"
    pattern = re.compile(restr,re.VERBOSE | re.IGNORECASE |re.DOTALL)
    ret = pattern.findall(str)
    if ret:
        try:
            strtime = ret[0].replace(',', '')
            timesp = time.strptime(strtime, "%B %d %Y")
            timesf = time.strftime("%Y-%m-%d", timesp)
            return timesf
        except:
            timesf = time.strftime("%Y-%m-%d", time.localtime())
            return timesf
    timesf = time.strftime("%Y-%m-%d", time.localtime())
    return timesf