# -*- coding: utf-8 -*-
from scrapy import FormRequest
import re
from newscrapy.items import NewscrapyItem
from scrapy.spiders import Rule, CrawlSpider
from scrapy.linkextractors import LinkExtractor
from newscrapy.tools import dateGen
from urllib import parse


class mySpider(CrawlSpider):
    name = "tachengdaily"
    newspapers = "塔城日报"
    allowed_domains = ['szb.tcxw.cc']
    
    def start_requests(self):
        dates = dateGen(self.start, self.end, "%Y%m/%d")
        template = "http://szb.tcxw.cc/pc/layout/{date}/node_01.html"
        for d in dates:
            yield FormRequest(template.format(date = d))

    rules = (
        Rule(LinkExtractor(allow=('pc/layout/\d+/\d+/node\w+.html'))),
        Rule(LinkExtractor(allow=('pc/content/\d+/\d+/content\w+.html')), callback="parse_item")
    )

    def parse_item(self, response):
        try:
            title0 = response.xpath("//h3[@id='Title']").xpath("string(.)").get()
            subtitle = response.xpath("//p[@id='SubTitle']").xpath("string(.)").get()
            if subtitle != '':
                title = ' '.join(title0, subtitle)
            else:
                title = title0
            content = response.xpath("//div[@class='newsdetatext']//founder-content").xpath("string(.)").get()
            url = response.url
            date = re.search("content/(\d+/\d+)/content", url).group(1)
            date = '-'.join([date[0:4], date[4:6], date[7:9]])
            imgs = response.xpath("//div[@class='newsdetatext']//img/@src").getall()
            imgs = [parse.urljoin(url, imgurl) for imgurl in imgs]
            html = response.text
        except Exception as e:
            return
        
        item = NewscrapyItem()
        item['title'] = title
        item['content'] = content
        item['date'] = date
        item['imgs'] = imgs
        item['url'] = response.url
        item['newspaper'] = self.newspapers
        item['html'] = html
        yield item
