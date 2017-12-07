# -*- coding: utf-8 -*-
#
# Project: ArticleCollect (http://securityaffairs.co)
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
import sys
reload(sys)
sys.setdefaultencoding('utf-8')

class ForcepointSpider(CrawlSpider):
    name = 'securityaffairs'
    allowed_domains = ['securityaffairs.co']

    # start_urls = ["badcyber.com/page/{}/".format(str(i)) for i in range(0, 10, 1)]
    start_urls = ["http://securityaffairs.co/wordpress/category/malware"]

    rules = [
        Rule(LinkExtractor(allow=('/malware/page/\d+')), callback='parse_item', follow=True),
    ]


    def parse_item(self, response):
        if not response.xpath('//div[@class="post_header single_post"]//h3/a[@href]'):
            return
        for blog in response.xpath('//div[@class="post_header single_post"]//h3/a[@href]'):
            blog_url = blog.xpath("./@href").extract_first()
            title = blog.xpath("./text()").extract_first().strip()
            # print "==="*30
            # print blog_url
            # print title
            # yield scrapy.Request(url=blog_url, headers=response.headers, dont_filter=True, callback=self.parse_content, meta={'title':title})
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

        title = response.xpath('//h1[@class="post_title"]/text()').extract_first()
        item['title'] = title.encode('utf-8').strip() if title else response.meta['title'].encode('utf-8')

        publish_timeTmp = response.xpath('//div[@class="post_detail"]/text()').extract_first()

        if publish_timeTmp:
            publish_timeTmp = publish_timeTmp.replace('By', '').strip()
            publish_time = format_date(publish_timeTmp)
            item['publish_time'] = publish_time if publish_time else None

        publisher = response.xpath('//div[@class="post_detail"]/a[@href]/text()').extract_first()
        item['publisher'] = publisher.encode('utf-8', ).strip() if publisher else None

        publisher_href = response.xpath('//div[@class="post_detail"]/a[@href]/@href').extract_first()
        item['publisher_href'] = publisher_href.encode('utf-8') if publisher_href else None

        content = response.xpath('//div[@class="post_inner_wrapper"]').extract_first()
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