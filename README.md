
京东手机信息爬虫
====
## JD爬虫

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
