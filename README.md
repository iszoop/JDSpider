
京东手机信息爬虫
====

*JD.py*

```python
     def __init__(self,**kwargs):
        chrome_opt = webdriver.ChromeOptions()
        prefs = {"profile.managed_default_content_settings.images": 2}
        chrome_opt.add_experimental_option("prefs", prefs)
        self.browser = webdriver.Chrome(executable_path="C:\Mycode\爬虫资源\chromedriver.exe",chrome_options=chrome_opt)
        super(JdSpider, self).__init__()
        dispatcher.connect(self.spider_closed, signals.spider_closed)
```

因为京东是动态加载的网页，所以使用__init__方法利用selenium加载网页，具体使用方法见middleware.Py

```python
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
        yield Request(url=parse.urljoin(response.url,str(next_url)),callback=self.parse)
```

parse方法用来获取搜索页面的主页以及定义翻页逻辑

**middleware.py**
```python
class JSPageMiddleware(object):
    # 通过chorme请求动态网页
    def process_request(self,request,spider):
        if spider.name == "JD":
            spider.browser.get(request.url)
            import time
            time.sleep(1)
            print("访问{0}".format(request.url))
            import re
            match_search = re.match(".*(search).*",request.url)
            if match_search:
                for i in range(2):
                    spider.browser.execute_script(
                        "window.scrollTo(0,document.body.scrollHeight); var lenOfPage=document.body.scrollHeight;return lenOfPage;")
                    time.sleep(2)
            return HtmlResponse(url=spider.browser.current_url, body=spider.browser.page_source, encoding="utf-8",
                            request=request)
```

这里用了chormedriver来请求网页，更换spider的时候，同时需要更改spider.name；

**使用redies**
拷贝scrapy_redis到主目录，需要将JD.py继承的类改为RedisSpider;

启动爬虫之后，需要在redis lpush一个JD:start_url作为起始URL(除了爬取手机信息，爬取其他商品的信息可以lpush当前商品的搜索url作为起始url)

