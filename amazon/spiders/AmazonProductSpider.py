# -*- coding: utf-8 -*-
from amazon.items import AmazonItem

from selenium import webdriver
from selenium.webdriver.common.proxy import *

from scrapy.http import TextResponse 
from scrapy.xlib.pydispatch import dispatcher
from scrapy import signals
from scrapy.http.request import Request

from sqlalchemy import Table, Column, Integer, String, MetaData, ForeignKey
from sqlalchemy import create_engine
from sqlalchemy.orm import mapper
from sqlalchemy.orm import sessionmaker
from sqlalchemy import update


import uuid
import time
import scrapy
import random



# ChromeOptions option = new ChromeOptions();
# option.addArguments("--proxy-server=http://" + PROXY);
# WebDriver driver = new ChromeDriver(option);

#класс модели базы данных
class Crowl(object):
    def __init__(self, url, stage, complete):
        self.url = url
        self.stage = stage
        self.complete = complete

class AmazonProductSpider(scrapy.Spider):
    name = "AmazonProductSpider"
    # allowed_domains = ['amazonaws.com', 'aws.amazon.com', 'amazon.in']

    #Use working product URL below
    start_urls = [
       'http://www.amazon.in/s/ref=sr_nr_n_1?fst=as%3Aoff&rh=n%3A1350387031%2Cn%3A%211499791031%2Cn%3A%211499793031%2Cn%3A3965457031%2Ck%3Aintelligent+quartz%2Cn%3A2563505031&bbn=3965457031&keywords=intelligent+quartz&ie=UTF8&qid=1490625006&rnid=1350388031'
    ]

    def __init__(self):
        # from selenium.webdriver.chrome.options import Options
        # opts = Options()
        # opts.add_argument("user-agent=whatever you want")
        # driver = webdriver.Chrome(chrome_options=opts)

        # from selenium import webdriver
        # profile = webdriver.FirefoxProfile()
        # profile.set_preference("general.useragent.override", "whatever you want")
        # driver = webdriver.Firefox(profile)

        dispatcher.connect(self.spider_closed, signals.spider_closed)
        #подключение к базе данных
        engine = create_engine('sqlite:///test.db', echo=False)
        #описание таблицы
        metadata = MetaData()
        tb_Crowl = Table('Crowl', metadata,
            Column('id', Integer, primary_key=True),
            Column('url', String),
            Column('stage', Integer),
            Column('complete', Integer)
        )
        #создание таблицы
        metadata.create_all(engine)
        #связь модели и базы данных
        mapper(Crowl, tb_Crowl)
        #создание сессии для общения с базой данных
        Session = sessionmaker(bind=engine)
        self.session = Session()
        f = open('list_proxy.txt', 'r')
        self.listProxy = []
        for line in f:
            self.listProxy.append(line)
        self.baseUrl = 'http://www.amazon.in'

    def spider_closed(self, spider):
        # self.driver.close()
        self.session.commit()

    def getProxy(self):
        numProxy = random.randint(0, len(self.listProxy)-1)
        return self.listProxy[numProxy]
        # for x in self.listProxy: 
        #     print('!!!!!!!!!!!')
        #     print(x.strip())
        #     print('!!!!!!!!!!!')

    # def start_requests(self):
    #     db = self.session.query(Crowl).filter_by(complete=1).order_by(-Crowl.id).first()
    #     try:
    #         url = db.url
    #     except:
    #         url = 'http://www.amazon.in/b/ref=topnav_storetab_top_ap_mega?ie=UTF8&node=6648217031'
    #     proxy = self.getProxy()
    #     request = scrapy.Request(url, callback=self.crawlerCategories)
    #     # request.headers['Proxy-Authorization'] = 'Basic ' + base64.encodestring('johndoe:PaSsw0rd')
    #     yield request

    def parse(self, response):
        '''
        crawler on categories
        '''
        checkThisUrl = self.session.query(Crowl).filter_by(url=response.url).first()
        try:
            if checkThisUrl.url:
                pass
        except:
            print('Create db note')
            checkThisUrl = Crowl(response.url, 1, 0) #add db new processing url
            self.session.add(checkThisUrl)
        if not checkThisUrl.complete:
            print("call parseCategories")
            # yield self.parseCategories(response)
            light = 0
            i_ul = 1
            while response.xpath('//*[@id="a-page"]/div[3]/div/div[2]/div/div[1]/div[1]/ul[{i}]|//*[@id="refinements"]/div[2]/ul[{i}]'.format(i=i_ul)).extract():
                i_li = 1
                while response.xpath('//*[@id="a-page"]/div[3]/div/div[2]/div/div[1]/div[1]/ul[{i}]/li[{j}]|//*[@id="refinements"]/div[2]/ul[{i}]/li[{j}]'.format(i=i_ul,j=i_li)).extract():
                    if response.xpath('//*[@id="a-page"]/div[3]/div/div[2]/div/div[1]/div[1]/ul[{i}]/li[{j}]/a/@href|//*[@id="refinements"]/div[2]/ul[{i}]/li[{j}]/a/@href'.format(i=i_ul,j=i_li)).extract():
                        if not response.xpath('//*[@id="refinements"]/div[2]/ul[{i}]/li[{j}][contains(@class, "shoppingEngineExpand")]'.format(i=i_ul,j=i_li)).extract():
                            light = light + 1
                            cat_next_url = self.baseUrl + ''.join(response.xpath('//*[@id="a-page"]/div[3]/div/div[2]/div/div[1]/div[1]/ul[{i}]/li[{j}]/a/@href|//*[@id="refinements"]/div[2]/ul[{i}]/li[{j}]/a/@href'.format(i=i_ul,j=i_li)).extract())
                            checkUrl = self.session.query(Crowl).filter_by(url=cat_next_url).first()
                            try:
                                if checkUrl.url: #НЕТ рекурсивный вызов функции c полученным url-ом
                                    pass
                            except:
                                checkUrl = Crowl(cat_next_url, 1, 0) #add db new processing url
                                self.session.add(checkUrl)
                            if not checkUrl.complete:
                                print('CallBack!')
                                yield scrapy.Request(cat_next_url, callback=self.parse)
                    print('i_li = {t}'.format(t=i_li))
                    i_li = i_li + 1
                print('i_ul = {t}'.format(t=i_ul))
                i_ul = i_ul + 1
            if light == 0:
                # light_db = checkUrl = Crowl('END!!!' + response.url, 1, 1)
                # self.session.add(light_db)
                yield scrapy.Request(response.url, callback=self.crawlerProductList)
                #yield self.crawlerProductList(response)
            else:
                checkThisUrl.complete = 1
                checkThisUrl.stage = 0
            self.session.commit()
            print('Finish!!!!!')

    def crawlerProductList(self, response):
        '''
        crawler on prodact list
        '''
        # light_db = checkUrl = Crowl('I crawlerProductList!!!!!!!!!!!!!!!!', 1, 1)
        # self.session.add(light_db)
        # self.session.commit()
        print("I'm crawlerProductList!!!!!!!!!!!!!!!!")
        checkThisUrl = self.session.query(Crowl).filter_by(url=response.url).first()
        try:
            if checkThisUrl.url:
                pass
        except: 
            checkThisUrl = Crowl(response.url, 1, 0)
            self.session.add(checkThisUrl)
        if not checkThisUrl.complete:
            print("parserProductList!!!!!!!!!!!!")
            
            try:
                j_li = response.meta['result']
            except:
                j_li = 1

            while response.xpath('//*[@id="result_{i}"]'.format(i=j_li)).extract():
                prod_url = ''.join(response.xpath('//*[@id="result_{i}"]/div/div[1]/div/a/@href'.format(i=j_li)).extract())
                print('111!!!!!!!!!!!!!')
                print(prod_url)
                print('!!!!!!!!!!!!!')                
                checkUrl = self.session.query(Crowl).filter_by(url=prod_url).first()
                try:
                    if checkUrl.url:
                        pass
                except:
                    checkUrl = Crowl(prod_url, 1, 0)
                    self.session.add(checkUrl)
                if not checkUrl.complete: #запрос в базу пройден ли этот url
                    yield scrapy.Request(prod_url, self.scrapperProduct) #НЕТ вызов функции парсинга продукта
                    # checkUrl.complete = 1
                    # checkUrl.stage = 0
                j_li = j_li + 1 #ДА переходим к следующему
            checkThisUrl.complete = 1
            checkThisUrl.stage = 0
            self.session.commit()
        try:
            if ''.join(response.xpath('//*[@id="pagnNextLink"]/@href').extract()):
                prod_next_page_url = self.baseUrl + ''.join(response.xpath('//*[@id="pagnNextLink"]/@href').extract()) #check existing a next page
                # print('222!!!!!!!!!!!!!')
                # print(prod_next_page_url)
                # print('!!!!!!!!!!!!!')
                request = scrapy.Request(prod_next_page_url, callback=self.crawlerProductList)
                request.meta['result'] = j_li
                yield request
        except:
            return True

    def scrapperProduct(self, response):
        """
        parse product
        """
        print("I'm parser!!!!!!!!!!!!!!!!!")

        self.driver = webdriver.Chrome('/Users/user/Documents/ShopifyCSV/amazon/amazon/spiders/chromedriver')

        # numProxy = random.randint(0, len(self.listProxy)-1)
        # myProxy = self.listProxy[numProxy].strip()
        # print('!!!!!!!!!!!!')
        # print(myProxy)
        # print('!!!!!!!!!!!!')
        # chrome_option = webdriver.ChromeOptions()
        # chrome_option.add_argument("--proxy-server={proxy}".format(proxy=myProxy))
        # self.driver = webdriver.Chrome(executable_path='/Users/user/Documents/ShopifyCSV/amazon/amazon/spiders/chromedriver', chrome_options=chrome_option)
        
        self.driver.get(response.url)
        time.sleep(5)
        i = 1
        try:
            element = self.driver.find_element_by_xpath('//*[@id="size-chart-url"]')
            element.click()
        except:
            pass
        k=2
        while True:
            try:
                element = self.driver.find_element_by_xpath('//*[@id="altImages"]/ul/li[{k}]/span/span/span/input'.format(k=k))
                element.click()
                k = k+1
            except:
                break
        time.sleep(3)
        response = TextResponse(url=response.url, body=self.driver.page_source, encoding='utf-8')
        availability = response.xpath('//div[@id="availability"]//text()').extract()
        f = open('index.html', 'w')
        f.write(self.driver.page_source)
        f.close()
        self.driver.close()

        while ((response.xpath('//*[@id="native_size_name_{i}"]'.format(i=i)).extract()) or (response.xpath('//*[@id="altImages"]/ul/li[{i}]/span/span/span/input'.format(i=(i+1))).extract())):
            items = AmazonItem()
            handle = response.xpath('//*[@id="productTitle"]/text()').extract() #OK!
            size = response.xpath('//*[@id="native_size_name_{i}"]/text()'.format(i=i)).extract() 
            altImage = response.xpath('//*[@id="altImages"]/ul/li[{i}]/span/span/span/span/img/@src'.format(i=i)).extract()
            sale_price = ''
            price = ''
            description = ''
            title = ''
            size_chart = ''
            label_color = ''
            label_size = ''
            label_description = ''
            sku = ''
            product_url = ''
            if i == 1:
                product_url = response.url
                sku = str(uuid.uuid4())
                label_color = 'color'
                label_size = 'size'
                label_description = 'description'
                title = response.xpath('//*[@id="productTitle"]/text()').extract() #OK!
                imglist = response.xpath('//*[@id="main-image-container"]/ul/li[{i}]/span/span/div/img/@src'.format(i=i)).extract()
                sale_price = response.xpath('//span[contains(@id,"ourprice") or contains(@id,"saleprice")]/text()').extract() #full prices
                _tr = 1
                while response.xpath('//*[@id="size-chart-table-1"]/tbody/tr[{tr}]'.format(tr=_tr)).extract():
                    _td = 1
                    while response.xpath('//*[@id="size-chart-table-1"]/tbody/tr[{tr}]/*[{td}]'.format(tr=_tr,td=_td)).extract(): #//*[@id="size-chart-table-1"]/tbody/tr[1]/th[1]
                        # print("tr:{_tr}_td:{_td}".format(_tr=_tr, _td=_td))
                        if _tr == 1:
                            size_chart += ''.join(response.xpath('//*[@id="size-chart-table-1"]/tbody/tr[{tr}]/*[{td}]/text()'.format(tr=_tr,td=_td)).extract()).strip() 
                        else:
                            size_chart += ''.join(response.xpath('//*[@id="size-chart-table-1"]/tbody/tr[{tr}]/*[{td}]/span/text()'.format(tr=_tr,td=_td)).extract()).strip()
                        size_chart += ' '
                        _td = _td + 1
                    _tr = _tr + 1
                try:
                    if sale_price[1].strip():
                        price = sale_price[1].strip()
                    else:
                        price = ''.join(sale_price).strip()
                except:
                    price = ''
                j = 1
                description = ''
                while response.xpath('//*[@id="feature-bullets"]/ul/li[{j}]/span'.format(j=j)).extract():
                  description += ''.join(response.xpath('//*[@id="feature-bullets"]/ul/li[{j}]/span/text()'.format(j=j)).extract()).strip()
                  j= j + 1
            else:
                ig = i + 5
                imglist = response.xpath('//*[@id="main-image-container"]/ul/li[{i}]/span/span/div/img/@src'.format(i=ig)).extract()

            items['handle'] = ''.join(handle).strip()
            items['title'] = ''.join(title).strip()
            items['body'] = ''
            items['vendor_'] = ''
            items['type_'] = ''
            items['tags'] = ''
            items['published'] = ''
            items['option_1_name'] = label_color
            items['option_1_value'] = ''
            items['option_2_name'] = label_size
            items['option_2_value'] = ''.join(size).strip()
            items['option_3_name'] = label_description
            items['option_3_value'] = description
            items['variant_sku'] = sku
            items['variant_grams'] = ''
            items['variant_inventory_tracker'] = ''
            items['variant_inventory_quantity'] = ''
            items['variant_inventory_policy'] = ''
            items['variant_fulfillment_service'] = ''
            items['variant_price'] = ''.join(sale_price).strip()
            items['price'] = price
            items['variant_compare_at_price'] = ''
            items['variant_requires_shipping'] = ''
            items['variant_taxable'] = ''
            items['variant_barcode'] = ''
            items['image_src'] = ''.join(imglist).strip()
            items['image_position'] = i
            items['image_alt_text'] = ''
            items['gift_card'] = ''
            items['variant_image'] = ''.join(altImage).strip()
            items['variant_weight_unit'] = ''
            items['variant_tax_code'] = ''
            items['prodact_url'] = product_url
            items['availability'] = ''.join(availability).strip()
            items['size_chart'] = size_chart
            i = i + 1

            rows = self.session.query(Crowl).filter_by(url = response.url).update({'complete': 1})
            self.session.commit()

            # stmt = update(Crowl).where(Crowl.url==response.url).values(complete = 1, stage = 0)
            yield items
