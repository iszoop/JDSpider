# -*- coding: utf-8 -*-
import datetime
import re
import scrapy
import time
from scrapy.http import Request
from urllib import parse
from selenium import webdriver
from scrapy.xlib.pydispatch import dispatcher
from scrapy import signals
from scrapy_redis.spiders import RedisSpider
from JDSpider.items import JdspiderItem,ArticleItemLoader
from JDSpider.utils.common import get_md5


class JdSpider(RedisSpider):
    name = 'JD'
    allowed_domains = ['item.jd.com','search.jd.com']
    redis_key = "JD:start_urls"
    # start_urls = ['https://search.jd.com/Search?keyword=%E6%89%8B%E6%9C%BA&enc=utf-8&wq=%E6%89%8B%E6%9C%BA&pvid=a6198e2c7a654b36b90332574b661063']

    headers = {
        "HOST": "www.jingdong.com",
        "Referer": "https://www.jingdong.com",
        'User-Agent': "Mozilla/5.0 (Windows NT 6.1; WOW64; rv:51.0) Gecko/20100101 Firefox/51.0"
    }

    def __init__(self,**kwargs):
        chrome_opt = webdriver.ChromeOptions()
        prefs = {"profile.managed_default_content_settings.images": 2}
        chrome_opt.add_experimental_option("prefs", prefs)
        self.browser = webdriver.Chrome(executable_path="C:\Mycode\爬虫资源\chromedriver.exe",chrome_options=chrome_opt)
        super(JdSpider, self).__init__()
        dispatcher.connect(self.spider_closed, signals.spider_closed)

    def spider_closed(self, spider):
        # 爬虫退出的时候关闭chorme
        print("spider closed")
        self.browser.quit()


    def parse(self, response):
        if response.status == 404:
            self.fail_urls.append(response.url)
            self.crawler.stats.inc_value("failed_url")

        post_noods = response.css("#J_goodsList li[class='gl-item']")
        for post_nood in post_noods:
            # image_url = post_nood.css("a img::attr(src)").extract_first("")
            post_url = post_nood.css("::attr(href)").extract_first("")
            yield Request(url=parse.urljoin(response.url,str(post_url)),callback=self.parse_detail)

        self.browser.get(response.url)
        time.sleep(2)
        self.browser.find_element_by_css_selector('#J_bottomPage a[class="pn-next"]').click()
        next_url = self.browser.current_url
        # url = parse.urljoin(response.url, str(next_url))
        yield Request(url=parse.urljoin(response.url,str(next_url)),callback=self.parse)


    def parse_detail(self, response):
        item_loader = ArticleItemLoader(item=JdspiderItem(), response=response)
        phone_title = response.css(".sku-name::text").extract()[0].strip()
        match_re = re.match(u".*[\u4e00-\u9fa5]+",phone_title)
        if match_re:
            item_loader.add_css("title",".sku-name::text")
        else:
            title = response.xpath("/html/body/div[8]/div/div[2]/div[1]/text()").extract()[1].strip()
            item_loader.add_value("title", title)
        item_loader.add_value("url",response.url)
        item_loader.add_value("url_object_id",get_md5(response.url))
        item_loader.add_css("front_image_url","#spec-n1 img::attr(src)")
        shop_name =response.css(".name a::text")
        if shop_name:
            item_loader.add_css("shop_name",".name a::text")
        else:
            shop_name = "null"
            item_loader.add_value("shop_name", shop_name)
        price_item = response.xpath("/html/body/div[8]/div/div[2]/div[3]/div/div[1]/div[2]/span[1]/span[2]/text()")
        if price_item:
            price_item = price_item.extract()[0]
            item_loader.add_value("price",price_item)
        else:
            item_price = response.css('.dd .p-price .price::text').extract()[0]
            item_loader.add_value("price", item_price)
        item_loader.add_css("brand",".p-parameter a::text")
        item_loader.add_xpath("good_name","//*[@id='crumb-wrap']/div/div[1]/div[9]/text()")
        item_loader.add_xpath("comment_nums","//*[@id='comment-count']/a/text()")
        item_loader.add_value("crawl_time",datetime.datetime.now())

        phone_item = item_loader.load_item()
        yield phone_item


    # def start_requests(self):
    #     browser = webdriver.Chrome(executable_path="C:\Mycode\爬虫资源\chromedriver.exe")
    #     browser.get("https://passport.jd.com/new/login.aspx")
    #     import time
    #     time.sleep(5)
    #
    #
    #     browser.find_element_by_css_selector(".login-form  a[clstag='pageclick|keycount|login_pc_201804112|10']").click()
    #     browser.find_element_by_css_selector("#loginname").send_keys("12222")
    #     browser.find_element_by_css_selector("#nloginpwd").send_keys("****")
    #     browser.find_element_by_css_selector("#loginsubmit").click()
    #
    #     time.sleep(5)
    #     Cookies = browser.get_cookies()
    #     print(Cookies)
    #     cookie_dict = {}
    #     import pickle
    #     for cookie in Cookies:
    #         f = open('C:\Mycode\JDSpider\cookies\JD'+cookie['name']+'.JD','wb')
    #         pickle.dump(cookie,f)
    #         cookie_dict[cookie['name']] = cookie['value']
    #     browser.close()
    #     return [scrapy.Request(url=self.start_urls[0], dont_filter=True, headers=self.headers, cookies=cookie_dict)]
