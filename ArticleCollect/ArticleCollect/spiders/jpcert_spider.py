# -*- coding: utf-8 -*-
#
# Project: ArticleCollect (http://blog.jpcert.or.jp)
# author : tx
# Update : 2017-11-29
#

# from w3lib.url import urljoin
import scrapy
from ArticleCollect.items import ArticlecollectItem
from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import CrawlSpider, Rule
import time
import re

class ForcepointSpider(CrawlSpider):
    name = 'jpcert'
    allowed_domains = ['blog.jpcert.or.jp']

    # start_urls = ["http://blog.jpcert.or.jp/threats/?p={}".format(str(i)) for i in range(1, 5)]
    start_urls = ["http://blog.jpcert.or.jp/threats/"]

    rules = [
        Rule(LinkExtractor(allow=('/?p=\d+')), callback='parse_item', follow=True),
    ]

    def parse_item(self, response):
        print response.body
        if not response.xpath('//div[@class="entry"]/h3[@class="entry-header"]/a[@href]'):
            return
        for blog_url in response.xpath('//div[@class="entry"]/h3[@class="entry-header"]/a/@href').extract():
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
        item['prublisher_id'] = None

        html = response.xpath('/html').extract_first()
        item['html'] = html if html else None

        publish_timeTmp = response.xpath('//div[@id="alpha-inner"]/h2[@class="date-header"]/text()').extract_first()
        if publish_timeTmp:
            publish_time = format_date(publish_timeTmp)
            item['publish_time'] = publish_time if publish_time else None


        article_id = response.xpath('//div[@class="entry"]/@id').extract_first()
        item['article_id'] = article_id.encode('utf-8') if article_id else None

        body = response.xpath('//div[@class="entry"]')

        title = body.xpath('./h3[@class="entry-header"]/text()').extract_first()
        item['title'] = title.encode('utf-8') if title else None

        content = body.xpath('./div[@class="entry-content"]').extract_first()
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
            timesp = time.strptime(strtime, "%b %d %Y")
            timesf = time.strftime("%Y-%m-%d", timesp)
            return timesf
        except:
            timesf = time.strftime("%Y-%m-%d", time.localtime())
            return timesf
    timesf = time.strftime("%Y-%m-%d", time.localtime())
    return timesf