from redis_spider import RedisSpider
from crawling.items import RawResponseItem
from crawling.models import Part, Fitment
from scrapy.http import Request
# from crawling.spiders.lxmlhtml import CustomLxmlLinkExtractor as LinkExtractor


class PartHOEMSpider(RedisSpider):

    '''
    Based on hyundaioemparts.com product pages
    A spider that grabs 'products' from the redis queue and process them into the database
    '''

    name = "products"

    custom_settings = {
        'ITEM_PIPELINES': {
            'crawling.pipelines.DataPipeline': 400
        }
    }

    def __init__(self, *args, **kwargs):
        super(PartHOEMSpider, self).__init__(*args, **kwargs)

    def parse(self, response):
        self._logger.info("crawled url {}".format(response.request.url))
        # capture raw response
        item = RawResponseItem()
        # populated from response.meta
        item['appid'] = response.meta['appid']
        item['crawlid'] = response.meta['crawlid']
        item['attrs'] = response.meta['attrs']
        # populated from raw HTTP response
        item["url"] = response.request.url
        item["response_url"] = response.url
        item["status_code"] = response.status
        item["status_msg"] = "OK"
        item["response_headers"] = self.reconstruct_headers(response)
        item["request_headers"] = response.request.headers
        item["body"] = response.body
        item["encoding"] = response.encoding
        item["links"] = []

        part = Part()
        part.url = str(response.request).lstrip('<Request GET ').rstrip('>')
        self._logger.info("part url: {}".format(part.url))
        part.parent_url = response.request.headers.get('referer_url')
        self._logger.info("parent url: {}".format(part.parent_url))
        part.name = response.xpath('//div[@class="product-title-module"]/h1/text()').extract_first()
        self._logger.info("part name: {}".format(part.name))
        list_price = response.xpath('//span[@id="product_price2"]/text()').extract_first()
        if list_price is not None:
            part.list_price = list_price.replace('$', '').replace(',', '')
            # list_price_str = list_price.strip('$')
            # part.list_price = list_price_str.strip(',')
        self._logger.info("part list_price: {}".format(part.list_price))
        sale_price = response.xpath('//span[@id="product_price"]/text()').extract_first()
        if sale_price is not None:
            part.sale_price = sale_price.replace('$', '').replace(',', '')
            # sale_price_str = sale_price.strip('$')
            # part.sale_price = sale_price_str.strip(',')
        self._logger.info("part sale_price: {}".format(part.sale_price))
        part.sku = response.xpath('//span[contains(@class,"sku-display")]/text()').extract_first()
        self._logger.info("part sku: {}".format(part.sku))
        part.positions = response.xpath('//li[@class="positions"]/span[@class="list-value"]/text()').extract_first()
        self._logger.info("part positions: {}".format(part.positions))
        part.other_names = response.xpath('//li[@class="also_known_as"]/span[@class="list-value"]/text()').extract_first()
        self._logger.info("part other_names: {}".format(part.other_names))
        part.description = response.xpath('//li[@itemprop="description"]/span/p/text()').extract_first()
        self._logger.info("part description: {}".format(part.description))
        fitments = response.xpath('//table[@class="fitment-table"]//tr')

        for f in fitments[1:]:  # ignore table header row
            fitment = Fitment()
            fitment.make = f.xpath('td[1]//text()').extract_first()
            self._logger.info("fitment.make: {}".format(fitment.make))
            fitment.body_trim = f.xpath('td[2]//text()').extract_first()
            self._logger.info("fitment.body_trim: {}".format(fitment.body_trim))
            fitment.eng_tran = f.xpath('td[3]//text()').extract_first()
            self._logger.info("fitment.eng_tran: {}".format(fitment.eng_tran))
            part.fitments.append(fitment)

        yield {'part': part}
