# Scrapy(1.4.0) for python 2.7 (ArticleSpider)


## 项目功能介绍：
* 1、主要爬取威胁情报来源文章。（文章html文件、文章内容、文章图片）
* 2、主要通过xpath解析页面。
* 3、文章内容以具体文章的 url 对应你的MD5值命名的json格式保存。
* 4、原始网页以具体文章的 url 对应你的MD5值命名的zip压缩方式保存。
* 5、主要数据目录结构, 在`main.py` 同目录下的`output`下。
	```
	output
	|
	|__网站域名
		|
		|__data
		|	|__2016-10-10
		|	|__2016-10-11
		|	|...
		|
		|__orig_html
		|	|__2016-10-10
		|	|__2016-10-11
		|	|...
	```


## 文章来源：
* 1、https://www.alienvault.com/blogs/labs-research
* 2、https://badcyber.com
* 3、https://citizenlab.ca/category/research/targeted-threats/
* 4、https://www.fireeye.com/blog/threat-research.html
* 5、http://blog.jpcert.or.jp/threats/
* 6、https://blog.malwarebytes.com/category/threat-analysis
* 7、https://www.malwarepatrol.net/blog/
* 8、https://myonlinesecurity.co.uk/
* 9、https://www.pwc.co.uk/issues/cyber-security-data-privacy/insights.html
* 10、http://securityaffairs.co/wordpress/category/malware
* 11、https://securityintelligence.com/category/x-force/
* 12、https://www.symantec.com/connect/symantec-blogs/symantec-security-response
* 13、http://blog.virustotal.com


## Scapy中item 保存数据要求：
* html: "html原始数据",
* title: "文章的标题",
* content: "文章的内容",
* publisher: "文章作者",
* publish_time: "文章的发布时间（格式：2017-01-02 08:07:06，精度不够用0来补上）",
* spider_time: "爬虫的爬取时间（时间戳，13位精度）",
* publisher_href: "作者的个人链接",
* prublisher_id: "文章作者的id ",
* url: "文章的url",
* article_id: "文章的id",
* img_urls: "文章中图片的url链接"
注：无法获取该字段填None, 相关数据统一采用utf-8编码
