# -*- coding: utf-8 -*-
#
# Project: ArticleCollect (http://blog.virustotal.com)
# author : tx
# Update : 2017-12-05
#

# from w3lib.url import urljoin
import scrapy
from ArticleCollect.items import ArticlecollectItem
from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import CrawlSpider, Rule
import time
import re

class ForcepointSpider(CrawlSpider):
    name = 'virustotal'
    allowed_domains = ['virustotal.com']

    # start_urls = ["badcyber.com/page/{}/".format(str(i)) for i in range(0, 10, 1)]
    start_urls = ["http://blog.virustotal.com"]

    rules = [
        Rule(LinkExtractor(allow=('updated-max=')), callback='parse_item', follow=True),
    ]


    def parse_item(self, response):
        if not response.xpath('//div[@class="post hentry"]//h3[@class="post-title entry-title"]/a[@href]'):
            return
        # for blog_url in response.xpath('//div[@class="post hentry"]//h3[@class="post-title entry-title"]/a/@href').extract():
        for blog in response.xpath('//div[@class="post hentry"]//h3[@class="post-title entry-title"]/a[@href]'):
            blog_url = blog.xpath("./@href").extract_first()
            title = blog.xpath("./text()").extract_first().strip()
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

        publish_timeTmp = response.xpath('//div[@class="date-outer"]//h2[@class="date-header"]/span/text()').extract_first()
        if publish_timeTmp:
            publish_timeTmp = publish_timeTmp.split(',')[-1]
            publish_time = format_date(publish_timeTmp)
            item['publish_time'] = publish_time if publish_time else None

        title = response.xpath('//div[@class="post hentry"]/h3/text()').extract_first()
        item['title'] = title.encode('utf-8').strip() if title else response.meta['title'].encode('utf-8')

        content = response.xpath('//div[@class="date-posts"]//div[@class="post-body entry-content"]').extract_first()
        item['content'] = content if content else None

        publisher = response.xpath('//div[@class="post-footer"]//span[@class="fn"]/a[@href]/text()').extract_first()
        item['publisher'] = publisher.encode('utf-8').strip() if publisher else None

        publisher_href = response.xpath('//div[@class="post-footer"]//span[@class="fn"]/a[@href]/@href').extract_first()
        item['publisher_href'] = publisher_href.encode('utf-8') if publisher_href else None

        yield item


def format_date(value):
    if not value:
        return None
    str = value
    try:
        strtime = value.strip()
        # timesp = time.strptime(strtime, "%B %d %Y")
        timesp = time.strptime(strtime, "%d %B %Y")
        timesf = time.strftime("%Y-%m-%d", timesp)
        return timesf
    except:
        timesf = time.strftime("%Y-%m-%d", time.localtime())
        return timesf

    return timesf