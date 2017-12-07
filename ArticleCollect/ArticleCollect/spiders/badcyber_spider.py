# -*- coding: utf-8 -*-
#
# Project: ArticleCollect (https://badcyber.com)
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
    name = 'badcyber'
    allowed_domains = ['badcyber.com']

    # start_urls = ["badcyber.com/page/{}/".format(str(i)) for i in range(0, 10, 1)]
    start_urls = ["https://badcyber.com"]

    rules = [
        Rule(LinkExtractor(allow=('badcyber.com/page/\d+')), callback='parse_item', follow=True),
    ]


    def parse_item(self, response):
        if not response.xpath('//h2[@class="entry-title"]//a[@href]'):
            return
        for blog_url in response.xpath('//h2[@class="entry-title"]//a/@href').extract():
            # domians = 'https://badcyber.com'
            # blog_url = domians + blog_url if 'http' not in blog_url else blog_url
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
        item['publisher_id'] = None

        html = response.xpath('/html').extract_first()
        item['html'] = html if html else None

        article_id = response.xpath('//main[@id="main"]/article[@id]/@id').extract_first()
        item['article_id'] = article_id.encode('utf-8') if article_id else None

        title = response.xpath('//header[@class="entry-header"]/h1[@class="entry-title"]/text()').extract_first()
        item['title'] = title.encode('utf-8') if title else str(response.url).split('/')[-1]

        publisher = response.xpath('//span[@class="author vcard"]/a[@href]/text()').extract_first()
        item['publisher'] = publisher.encode('utf-8') if publisher else None

        publisher_href = response.xpath('//span[@class="author vcard"]/a[@href]/@href').extract_first()
        item['publisher_href'] = publisher_href.encode('utf-8') if publisher_href else None

        publish_timeTmp = response.xpath('//span[@class="posted-on"]//time[@class="entry-date published updated"]/text()').extract_first()
        if not publish_timeTmp:
            publish_timeTmp = response.xpath('//span[@class="posted-on"]//time[@class="entry-date published"]/text()').extract_first()
            if not publish_timeTmp:
                publish_timeTmp = response.xpath('//span[@class="posted-on"]//time[@class="updated"]/text()').extract_first()
        if publish_timeTmp:
            publish_time = format_date(publish_timeTmp)
            item['publish_time'] = publish_time if publish_time else None

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