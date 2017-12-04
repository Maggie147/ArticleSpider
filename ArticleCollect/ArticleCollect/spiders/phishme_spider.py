# -*- coding: utf-8 -*-
#
# Project: ArticleCollect (https://phishme.com/blog)
# author : tx
# Update : 2017-12-04
#

# from w3lib.url import urljoin
import scrapy
from ArticleCollect.items import ArticlecollectItem
from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import CrawlSpider, Rule
import time
import re

class ForcepointSpider(CrawlSpider):
    name = 'phishme'
    allowed_domains = ['phishme.com']

    # start_urls = ["https://phishme.com/blog/{}/".format(str(i)) for i in range(0, 80, 5)]
    start_urls = ["https://phishme.com/blog"]

    rules = [
        Rule(LinkExtractor(allow=('phishme.com/blog/page/\d+/')), callback='parse_item', follow=True),
    ]


    def parse_item(self, response):
        if not response.xpath('//div[@class="binfo"]//div[@class="binfo-inner"]/h2/a[@href]'):
            return
        for blog_url in response.xpath('//div[@class="binfo"]//div[@class="binfo-inner"]/h2/a/@href').extract():
            domians = 'https://phishme.com'
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

        title = response.xpath('//h1[@class="entry-title landing-page-title"]/a/text()').extract_first()
        item['title'] = title.encode('utf-8') if title else str(response.url).split('/')[-1]

        publish_timeTmp = response.xpath('//div[@class="entry-meta"]/span[@class="date"]/text()').extract_first()
        if publish_timeTmp:
            print publish_timeTmp
            publish_timeTmp= publish_timeTmp.replace('Posted On', '').strip()
            print publish_timeTmp
            publish_time = format_date(publish_timeTmp)
            print publish_time
            item['publish_time'] = publish_time if publish_time else None
            print item['publish_time']

        publisher = response.xpath('//div[@class="entry-meta"]/a[@href]//text()').extract_first()
        item['publisher'] = publisher.encode('utf-8') if publisher else None

        publisher_href = response.xpath('//div[@class="entry-meta"]/a/@href').extract_first()
        item['publisher_href'] = publisher_href.encode('utf-8') if publisher_href else None

        content = response.xpath('//div[@class="entry-content"]').extract_first()
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