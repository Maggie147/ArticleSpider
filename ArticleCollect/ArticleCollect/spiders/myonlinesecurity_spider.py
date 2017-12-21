# -*- coding: utf-8 -*-
#
# Project: ArticleCollect (https://myonlinesecurity.co.uk/)
# author : tx
# Update : 2017-12-21
#

# from w3lib.url import urljoin
import scrapy
from ArticleCollect.items import ArticlecollectItem
from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import CrawlSpider, Rule
import time
import re

class ForcepointSpider(CrawlSpider):
    name = 'myonlinesecurity'
    allowed_domains = ['myonlinesecurity.co.uk']

    start_urls = ["https://myonlinesecurity.co.uk/"]

    rules = [
        Rule(LinkExtractor(allow=('/page/\d+')), callback='parse_item', follow=True),
    ]

    def parse_item(self, response):
        print response.body
        if not response.xpath('//header[@class="entry-header"]/h2[@class]/a[@href]'):
            return
        for blog_url in response.xpath('//header[@class="entry-header"]/h2[@class]/a/@href').extract():
            yield scrapy.Request(url=blog_url, callback=self.parse_content)


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
        item['publisher_id'] = None

        html = response.xpath('/html').extract_first()
        item['html'] = html if html else None

        article_id = response.xpath('//article[@id]/@id').extract_first()
        item['article_id'] = article_id.encode('utf-8') if article_id else None

        title = response.xpath('//header[@class="page-header"]/h1[@class]/text()').extract_first()
        item['title'] = title.encode('utf-8') if title else None

        publish_timeTmp = response.xpath('//header[@class="page-header"]//time[@class="entry-date"]/text()').extract_first()
        if publish_timeTmp:
            publish_time = format_date(publish_timeTmp)
            item['publish_time'] = publish_time if publish_time else None

        content = response.xpath('//div[@class="entry-content clearfix"]').extract_first()
        item['content'] = content if content else None

        yield item


def format_date(value):
    if not value:
        return None
    ret = value.split(' ')
    if not ret:
        return None
    new_value = ' '.join(ret[0:3])
    # print new_value

    try:                                # 15 December 2017
        timesp = time.strptime(str(new_value), "%d %B %Y")
        timesf = time.strftime("%Y-%m-%d", timesp)
        return timesf
    except:
        timesf = time.strftime("%Y-%m-%d", time.localtime())
        return timesf