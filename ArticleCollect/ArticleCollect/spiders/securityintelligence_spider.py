# -*- coding: utf-8 -*-
#
# Project: ArticleCollect (https://securityintelligence.com)
# author : tx
# Update : 2017-12-21
#

# from w3lib.url import urljoin
import scrapy
from ArticleCollect.items import ArticlecollectItem
from scrapy.linkextractors import LinkExtractor
# from scrapy.spiders import CrawlSpider, Rule
import time
import re

class ForcepointSpider(scrapy.Spider):
    name = 'securityintelligence'
    allowed_domains = ['securityintelligence.com']

    start_urls = ["https://securityintelligence.com/category/x-force/"]

    def parse(self, response):
        if not response.xpath('//article[@id]//div[@class="content col-lg-9 col-md-9 col-sm-12 col-xs-12"]'):
            return

        for blog in response.xpath('//article[@id]//div[@class="content col-lg-9 col-md-9 col-sm-12 col-xs-12"]'):
            blog_url = blog.xpath('.//a[@href]/@href').extract_first()
            blog_tile = blog.xpath('.//a[@href]/text()').extract_first().strip()
            blog_time = blog.xpath('.//span[@class="date-time"]/text()').extract_first().strip()
            blog_author = blog.xpath('.//span[@class="author"]/a/text()').extract_first().strip()
            # print blog_url
            # print blog_time
            # print blog_tile
            meta={'blog_time':blog_time, 'blog_tile':blog_tile}
            yield scrapy.Request(url=blog_url, headers=response.headers, dont_filter=True, callback=self.parse_content, meta=meta)


        if not response.xpath('//div[@class="load-more"]'):
            print "!!!!"*30, "no next page!!"
            return

        load_more = response.xpath('//div[@class="load-more"]/button[@class="load"]')
        data_catid = load_more.xpath('./@data-catid').extract_first()
        data_count = load_more.xpath('./@data-count').extract_first()
        data_offset = load_more.xpath('./@data-offset').extract_first()
        data_action = load_more.xpath('./@data-action').extract_first()

        offset = 0
        if data_offset:
            print data_offset
            offset += int(data_offset)
            page_url = 'https://securityintelligence.com/wp-admin/admin-ajax.php'
            format_date = {'catid':data_catid, 'action':data_action, 'count':data_count, 'offset':offset}
            # print  page_url
            # yield scrapy.Request(url=page_url, headers=response.headers, dont_filter=True, callback=self.parse)
            yield scrapy.FormRequest(url=page_url, headers=response.headers, formdata =format_date, callback=self.parse)


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

        title = response.xpath('//div[@class="single-header"]//h1/text()').extract_first()
        item['title'] = title.encode('utf-8') if title else response.meta['blog_tile'].encode('utf-8')

        publish_timeTmp = response.xpath('//div[@class="post-meta"]/span[@class="date-time"]/text()').extract_first()
        if publish_timeTmp:
            publish_time = format_date(publish_timeTmp)
            item['publish_time'] = publish_time if publish_time else None

        publisher_tmp = response.xpath('//div[@class="post-meta"]/span[@class="author"]/a/text()').extract_first()
        item['title'] = title.encode('utf-8') if title else response.meta['blog_tile'].encode('utf-8')

        content = response.xpath('//div[@class="text-component"]').extract_first()
        item['content'] = content if content else None

        yield item


def format_date(value):
    if not value:
        return None
    try:                            #July 8, 2016
        timesp = time.strptime(value, "%B %d, %Y")
        timesf = time.strftime("%Y-%m-%d", timesp)
        return timesf
    except:
        timesf = time.strftime("%Y-%m-%d", time.localtime())
        return timesf