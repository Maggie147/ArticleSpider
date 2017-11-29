# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html
import os
import json
import zipfile
import hashlib
import shutil
from scrapy.http import Request
from scrapy.exceptions import DropItem
from scrapy.pipelines.images import ImagesPipeline #pip install pillow

class ArticlecollectPipeline(object):
    def process_item(self, item, spider):
        url_md5 = get_buf_md5(item['url'])

        orig_path = "output/%s/orig_html/%s/" % (spider.allowed_domains[0], item['publish_time'])
        writ_data(item, orig_path, url_md5+'.html', zipFlag=1)

        date_path = "output/%s/data/%s/" % (spider.allowed_domains[0], item['publish_time'])
        writ_data(item, date_path, url_md5+'.json', zipFlag=0)
        return item

def writ_data(item, fpath, filename, zipFlag=0):
    if not os.path.exists(fpath):
        os.makedirs(fpath)
    file_head = os.path.splitext(filename)[0]
    file_tail = os.path.splitext(filename)[1]

    # write web html to zip
    if ".html" in file_tail:
        if item['html'] and is_str(item['html']):
            with open (filename, 'w') as fhtml:
                fhtml.write(item['html'].encode('utf-8', 'ignore'))
        if zipFlag:
            fzip = zipfile.ZipFile(fpath+str(file_head)+'.zip', 'w', zipfile.ZIP_DEFLATED)
            if item['img_urls'] and item['image_paths']:
                for img_each in item['image_paths'][0]:
                    try:
                        img_file = os.path.basename(img_each)
                        img_orig = "img_tmp/"+img_each
                        print img_orig
                        shutil.move(img_orig, img_file)
                        fzip.write(img_file)
                        os.remove(img_file)
                    except:
                        print "=====", item
                        pass
            fzip.write(str(file_head) + '.html')
            fzip.close()
            os.remove(str(file_head) + '.html')

    # write item to json file
    elif ".json" in file_tail:
        item_tmp = item
        del(item_tmp['html'])
        with open(fpath + str(filename), 'w') as fjson:
            json.dump(dict(item_tmp), fjson)
    else:
        pass

class MyImagesPipeline(ImagesPipeline):
    def get_media_requests(self, item, info):
        if not os.path.exists("img_tmp"):
            os.makedirs("img_tmp")
        if item['img_urls']:
            for image_url in item['img_urls']:
                yield Request(image_url)

    def item_completed(self, results, item, info):
        if item['img_urls']:
            image_paths = [x['path'] for ok, x in results if ok]
            if not image_paths:
                raise DropItem("Item contains no images")
            item['image_paths'].append(image_paths)
            return item
        else:
            return item

    def file_path(self, request, response=None, info=None):
        image_guid = request.url.split('/')[-1]
        return 'full/%s' % (image_guid)


def get_buf_md5(buf):
    try:
        hashObj = hashlib.md5()
        hashObj.update(buf)
        return hashObj.hexdigest()
    except Exception as e:
        print e
        return None

def is_str(s):
    return isinstance(s, basestring)