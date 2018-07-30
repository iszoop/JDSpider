# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import datetime
import scrapy
import re
import redis
from scrapy.loader.processors import MapCompose,TakeFirst,Join
from scrapy.loader import ItemLoader
from  JDSpider.settings import SQL_DATETIME_FORMAT,SQL_DATE_FORMAT
from w3lib.html import remove_tags
# from ArticleSpider.utils.common import extract_num
# from ArticleSpider.settings import SQL_DATE_FORMAT,SQL_DATETIME_FORMAT
# from w3lib.html import remove_tags
# from models.es_types import ArticleType
# from elasticsearch_dsl.connections import connections


class ArticleItemLoader(ItemLoader):
    #自定义Itemloader,选择list第一位
    default_output_processor = TakeFirst()


def date_convert(value):
    """将时间转换为data格式"""
    try:
        create_date = datetime.datetime.strptime(value,"%Y/%m/%d").date()
    except  Exception as e:
        create_date = datetime.datetime.now().date()
    return create_date


def return_value(value):
    return value



def get_nums(value):
    """取数字"""
    unit = re.match(u".*([\u4e00-\u9fa5])+",value)
    match_re = re.match(".*?(\d+).*", value)
    if match_re:
        # unit = unit.group(1)
        if unit:
            nums = int(match_re.group(1)) * 10000
        else:
            nums = int(match_re.group(1))
    else:
        nums = 0
    return nums

def strip_title(value):
    title=value.strip()
    return title


class JdspiderItem(scrapy.Item):
    title = scrapy.Field(
        output_processor=MapCompose(strip_title),
    )
    url = scrapy.Field()
    url_object_id = scrapy.Field()
    front_image_url = scrapy.Field(
        output_processor=MapCompose(return_value),
    )
    front_image_path = scrapy.Field()
    shop_name = scrapy.Field()
    price = scrapy.Field(
        input_processor=MapCompose(get_nums),
    )
    brand = scrapy.Field()
    good_name = scrapy.Field()
    comment_nums = scrapy.Field(
        input_processor=MapCompose(get_nums),
    )
    crawl_time = scrapy.Field()

    def get_insert_sql(self):
        insert_sql = """
                           insert into jd_phone(title,url,url_object_id,front_image_url,shop_name,price,brand,
                           good_name,comment_nums,crawl_time)
                           VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
                           ON DUPLICATE KEY UPDATE title=VALUES(title), price=VALUES(price), comment_nums=VALUES(comment_nums),
                           crawl_time=VALUES(crawl_time)
              
                       """

        crawl_time = self["crawl_time"].strftime(SQL_DATETIME_FORMAT)
        title = self["title"].strip()


        params = (title, self["url"], self["url_object_id"], self["front_image_url"],self["shop_name"],
                  self["price"],self["brand"],self["good_name"],self["comment_nums"],crawl_time)

        return insert_sql,params

