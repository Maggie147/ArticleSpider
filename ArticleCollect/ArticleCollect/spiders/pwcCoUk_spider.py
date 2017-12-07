# -*- coding: utf-8 -*-
#
# Project: ArticleCollect (https://www.pwc.co.uk)
# author : tx
# Update : 2017-12-06
#

# from w3lib.url import urljoin
import scrapy
from ArticleCollect.items import ArticlecollectItem
from scrapy.linkextractors import LinkExtractor
# from scrapy.spiders import CrawlSpider, Rule
import time
import re

class ForcepointSpider(scrapy.Spider):
    name = 'pwcCoUk'
    allowed_domains = ['www.pwc.co.uk']

    start_urls = ["https://www.pwc.co.uk/issues/cyber-security-data-privacy/insights.html"]

    # rules = [
    #     Rule(LinkExtractor(allow=('')), callback='parse_item', follow=True),
    # ]

    def parse(self, response):
        if not response.xpath('//a[@class="collection__item-link"]'):
            return
        for blog in response.xpath('//a[@class="collection__item-link"]'):
            blog_url = blog.xpath('./@href').extract_first()
            blog_time = blog.xpath('.//time/text()').extract_first().strip()
            blog_tile = blog.xpath('.//h3/text()').extract_first().strip()
            # print blog_url
            # print blog_time
            # print blog_tile
            meta={'blog_time':blog_time, 'blog_tile':blog_tile}
            yield scrapy.Request(url=blog_url, headers=response.headers, dont_filter=True, callback=self.parse_content, meta=meta)


        if not response.xpath('//div[@class="collection__load-more"]/a[@class="btn btn--transparent"]'):
            print "!!!!"*30, "no next page!!"
            return

        page_start = 0
        page_tmp = response.xpath('//div[@class="collection__load-more"]/a[@class="btn btn--transparent"]/@onclick').extract_first()
        for onclick in page_tmp.split(','):
            if "start=" in onclick:
                page_start = onclick.split('=')[-1].replace("'", '').strip()
                break
        if page_start:
            print page_start
            domians = 'https://www.pwc.co.uk/content/pwc/uk/en/issues/cyber-security-data-privacy/insights/jcr:content/content-free-1-06d2-par/collection.dynamic.html?filter=&start='
            page_url = domians+page_start
            # print  page_url
            yield scrapy.Request(url=page_url, headers=response.headers, dont_filter=True, callback=self.parse)


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

        # title = response.xpath('//div[@class="container"]//h1[@class="title-strip__heading"]/text()').extract_first()
        # item['title'] = title.encode('utf-8') if title else response.meta['blog_tile'].encode('utf-8')
        title = response.xpath('//div[@class="container"]/div[@class="row"]/h1/text()').extract_first()
        item['title'] = title.encode('utf-8') if title else response.meta['blog_tile'].encode('utf-8')

        publish_timeTmp = response.meta['blog_time'] if response.meta['blog_time'] else None
        if publish_timeTmp:
            publish_time = format_date(publish_timeTmp)
            item['publish_time'] = publish_time if publish_time else None

        content = response.xpath('//div[@class="text-component"]').extract_first()
        item['content'] = content if content else None

        yield item


def format_date(value):
    if not value:
        return None
    try:
        timesp = time.strptime(value, "%d/%m/%y")
        timesf = time.strftime("%Y-%m-%d", timesp)
        return timesf
    except:
        timesf = time.strftime("%Y-%m-%d", time.localtime())
        return timesf