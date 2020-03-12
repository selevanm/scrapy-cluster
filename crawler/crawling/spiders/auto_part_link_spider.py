from redis_spider import RedisSpider
from crawling.items import RawResponseItem
from scrapy.http import Request
# from crawling.spiders.lxmlhtml import CustomLxmlLinkExtractor as LinkExtractor


class AutoLinkSpider(RedisSpider):

    '''
    A spider that takes category links fed into Kafka/Rest from autoparts pages and returns the
    actual product page link to be scraped
    '''

    name = "autoprodlinks"

    def __init__(self, *args, **kwargs):
        super(AutoLinkSpider, self).__init__(*args, **kwargs)

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
        base_url = 'https://www.hyundaioemparts.com'

        partlinks = response.xpath('//strong[@class="product-title"]/a/@href').extract()
        self._logger.info("product links: {}".format(partlinks))

        #if we dont get a list of parts this is prob not a parts page but a single part we should process
        if not partlinks:
            link = response.request.url.replace('\n', '')
            self._logger.info("processing single part link: {}".format(link))
            response.meta['spiderid'] = 'products'
            req = Request(link, callback=self.parse, headers={'referer_url': 'None'})
            yield req
        else:
            for link in partlinks:
                self._logger.info("processing link: {}".format(link))
                response.meta['spiderid'] = 'products'
                self._logger.info("setting spiderid in response meta: {}".format(response.meta['spiderid']))
                # attempting to yield the request for another spider to pick it up <spiderid>:<domain>:queue - products:www.hyundaioemparts.com:queue)
                link = link.replace('\n', '').split('?')[0]
                self._logger.info("link after cleanup is: {}".format(link))
                #this should yield the request back to redis and put it in the queue for the products spiders (set above in the meta)
                #the product spider will grab the url and will parse the page for the data.
                req = Request(base_url + link, callback=self.parse, headers={'referer_url': response.request.url})
                # self._logger.info("yielding request: {}".format(req))
                yield req
