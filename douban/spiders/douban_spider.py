# -*- coding: utf-8 -*-
import scrapy
from douban.items import DoubanItem

class DoubanSpiderSpider(scrapy.Spider):
    #爬虫名字
    name = 'douban_spider'

    #允许访问的域名，不在该域名范围的不会访问
    allowed_domains = ['movie.douban.com']

    #入口url
    start_urls = ['https://movie.douban.com/top250']

#默认解析方法
    def parse(self, response):

        #找到电影列表
        movie_list = response.xpath("//ol[@class='grid_view']/li")

        #循环遍历电影列表，找出所有自己需要的信息
        for i_item in movie_list:

            #实例化DoubanItem类
            douban_item = DoubanItem()

            #通过xpath解析获取想要的信息，注意后面要写extract_first()
            douban_item['serial_number'] = i_item.xpath(".//div[@class='item']//em/text()").extract_first()
            douban_item['movie_name'] = i_item.xpath(".//div[@class='info']//a/span[1]/text()").extract_first()

            #电影介绍信息比较复杂，有多行，需要进行处理
            content = i_item.xpath(".//div[@class='bd']/p[1]/text()").extract()
            for i_content in content:
                content_s = "".join(i_content.split())
                douban_item['introduce'] = content_s

            douban_item['star'] = i_item.xpath(".//div[@class='star']/span[2]/text()").extract_first()
            douban_item['evaluate'] = i_item.xpath(".//div[@class='star']/span[4]/text()").extract_first()
            douban_item['describe'] = i_item.xpath(".//p[@class='quote']/span[1]/text()").extract_first()
            douban_item['movie_url'] = i_item.xpath(".//div[@class='hd']/a/@href").extract()

            #将获取到的数据提交到Item Pipeline进行处理，如进行数据清洗和持久化处理
            yield douban_item

        #找到下一页
        next_link = response.xpath("//span[@class='next']/link/@href").extract()

        #如果下一页存在，则继续爬取下一页
        if next_link:
            next_link = next_link[0]
            yield scrapy.Request("https://movie.douban.com/top250" + next_link, callback=self.parse)