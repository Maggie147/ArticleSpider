# -*- coding: utf-8 -*-
#
# Project: ArticleCollect (https://www.symantec.com)
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
import json

class ForcepointSpider(scrapy.Spider):
    name = 'symantec'
    allowed_domains = ['symantec.com']
    url= 'https://www.symantec.com/connect/api/v1/content-search?facets=created,uid,language,im_vid_111&filters=im_crosspost_blogs:2261,im_vid_51:2261,OR&fl=nid&fq={"type":["blog"],"language":["en"]}&rows=20&sort=created+desc&start='
    start = 0
    total_num = 0
    mytotal = 0
    start_urls = [url+ str(start)]

    def parse(self, response):
        js = json.loads(response.body)                              # sites = json.loads(response.body_as_unicode())
        if "success" not in js['status'].lower():
            return

        try:
            self.total_num = int(str(js['numFound']).strip())
        except Exception as e:
            pass

        # rows = int(str(js['all']['rows']).strip())

        for js_item in js['items']:
            self.mytotal+=1
            meta = {}
            try:
                title = js_item['title']
                meta['title'] = title.strip() if title else None

                link = js_item['link']['href']
                meta['url'] = "https://www.symantec.com" + link.strip() if link else None

                content = js_item['content']
                meta['content'] = content if content else None

                article_id = js_item['contentId']
                meta['article_id'] = article_id if article_id else None

                publish_timeTmp = js_item['created']
                if publish_timeTmp:
                    publish_time = format_date(publish_timeTmp)
                    meta['publish_time'] = publish_time if publish_time else None

                author_tmp = js_item['author']
                if author_tmp:
                    meta['prublisher_id'] = author_tmp['uid'] if author_tmp['uid'] else None
                    meta['publisher'] = author_tmp['username'] if author_tmp['username'] else None
                    meta['publisher_href'] = "https://www.symantec.com"+author_tmp['userpath'] if author_tmp['userpath'] else None

                yield scrapy.Request(url=meta['url'], headers=response.headers, dont_filter=True, callback=self.parse_content, meta=meta)
            except Exception as e:
                print ">>>"*10, e, ">>>"*10

        self.start += 20
        if self.total_num <= self.start:
            return
        yield scrapy.Request(url=self.url +str(self.start), headers=response.headers, dont_filter=True, callback=self.parse)


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

        try:
            item['title'] = response.meta['title'].encode('utf-8') if response.meta['title'] else None
            item['content'] = response.meta['content']
            item['publisher'] = response.meta['publisher'].encode('utf-8') if response.meta['publisher'] else None
            item['publish_time'] = response.meta['publish_time']
            item['article_id'] = response.meta['article_id']
            item['publisher_href'] = response.meta['publisher_href']
            item['prublisher_id'] = response.meta['prublisher_id']
        except Exception as e:
            print "***"*10, e, "***"*10

        yield item


def format_date(value):
    if not value:
        return None
    try:
        strtime = value.strip()
        timesp = time.strptime(strtime, "%d %b %Y")
        timesf = time.strftime("%Y-%m-%d", timesp)
        return timesf
    except:
        timesf = time.strftime("%Y-%m-%d", time.localtime())
        return timesf

    return timesf