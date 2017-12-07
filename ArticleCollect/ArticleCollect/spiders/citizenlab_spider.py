# -*- coding: utf-8 -*-
#
# Project: ArticleCollect (https://citizenlab.ca)
# author : tx
# Update : 2017-12-06
#

# from w3lib.url import urljoin
import scrapy
from ArticleCollect.items import ArticlecollectItem
from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import CrawlSpider, Rule
import time
import re

class ForcepointSpider(CrawlSpider):
    name = 'citizenlab'
    allowed_domains = ['citizenlab.ca']

    # start_urls = ["badcyber.com/page/{}/".format(str(i)) for i in range(0, 10, 1)]
    start_urls = ["https://citizenlab.ca/category/research/targeted-threats/"]

    rules = [
        Rule(LinkExtractor(allow=('/page/\d+')), callback='parse_item', follow=True),
    ]


    def parse_item(self, response):
        if not response.xpath('//article[@id]//div[@class="w-two-thirds-ns w-100-ns ml2-ns"]/a[@href]'):
            return
        for blog in response.xpath('//article[@id]//div[@class="w-two-thirds-ns w-100-ns ml2-ns"]/a[@href]'):
            blog_url = blog.xpath('./@href').extract_first()
            title = blog.xpath('.//h1[@class="f5 f4-ns mt0 lh-title black"]/text()').extract_first().strip()
            yield scrapy.Request(url=blog_url, headers=response.headers, dont_filter=True, callback=self.parse_content, meta={'title':title})
            # yield scrapy.Request(url=blog_url, headers=response.headers, dont_filter=True, callback=self.parse_content)


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

        # title = response.xpath('//div[@class="post hentry"]/h3/text()').extract_first()
        # item['title'] = title.encode('utf-8').strip() if title else response.meta['title'].encode('utf-8')
        item['title'] = response.meta['title'].encode('utf-8')

        publisher_tmp = response.xpath('//div[@class="f5 mr4 b dark-gray dib"]//a[@class="author url fn"]')
        # print "***"*30
        if publisher_tmp:
            print "==="*30
            publisher = publisher_tmp.xpath('./text()').extract()
            print publisher
            item['publisher'] = ",".join(publisher).encode('utf-8') if publisher else None
            publisher_href = publisher_tmp.xpath('./@href').extract()
            print publisher_href
            item['publisher_href'] = ",".join(publisher_href).encode('utf-8') if publisher_href else None

        publish_timeTmp = response.xpath('//div[@class="mt2"]//time/text()').extract_first()
        if publish_timeTmp:
            publish_time = format_date(publish_timeTmp)
            item['publish_time'] = publish_time if publish_time else None

        content = response.xpath('//section[@class="article-body mb4 mt4 pt2 bt b--light-gray"]').extract_first()
        item['content'] = content if content else None

        yield item


def format_date(value):
    if not value:
        return None
    try:
        strtime = value.strip()
        timesp = time.strptime(strtime, "%B %d, %Y")
        # timesp = time.strptime(strtime, "%d %B %Y")
        timesf = time.strftime("%Y-%m-%d", timesp)
        return timesf
    except:
        timesf = time.strftime("%Y-%m-%d", time.localtime())
        return timesf

    return timesf