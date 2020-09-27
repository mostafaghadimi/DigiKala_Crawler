import scrapy
import pandas as pd

class CommentSpider(scrapy.Spider):
    name = "comment"

    def __init__(self):
        self.crawled = set()
        self.base_url = "https://www.digikala.com/ajax/product/comments/{}/?mode=newest_comment&page={}"
        self.title = "//h2[@class='c-comments__headline']/span/span/text()"
        self.container = "//div[@id='product-comment-list']/ul[@class='c-comments__list']/li/section/div[@class='article']"
        self.header = ".header div::text"
        self.comment_text = "p::text"
        self.positive = ".c-comments__evaluation-positive ul li::text"
        self.negative = ".c-comments__evaluation-negative ul li::text"
        self.pages = "//div[@class='c-pager']"
        self.all_pages = self.pages + "/ul/li/a/@href"
        self.product_no = 3440000
        self.all_urls = set(self.base_url.format(i, 1) for i in range(2, self.product_no))
        

    def url_parser(self, url):
        product_id = url.split("/")[6]
        current_page = int(url.split("=")[-1])
        return product_id, current_page

    def start_requests(self):
        for url in self.all_urls:
            product_id, current_page = self.url_parser(url)
            self.crawled.add((product_id, current_page))
            yield scrapy.Request(url=url, callback=self.parse)

    def parse(self, response):
        url = response.url
        product_id = url.split("/")[6]
        if response.status == 200:
            title = response.xpath(self.title).get()
            if title:
                comments = response.xpath(self.container)
                for i, comment in enumerate(comments):
                    # print("index", i)
                    # print("product_id", product_id)
                    # print("comment", comment)
                    header = comment.css(self.header).get() #done
                    comment_text = comment.css(self.comment_text).get() #done
                    positive = comment.css(self.positive).getall() 
                    negative = comment.css(self.negative).getall()

                    yield {
                        'product_id': product_id,
                        'title': title,
                        'header': header,
                        'title': title,
                        'comment': comment_text,
                        'positive': positive,
                        'negative': negative,
                    }
                
                all_pages = response.xpath(self.all_pages).getall()
                if all_pages:
                    last_page = int(all_pages[-1].split("=")[-1])
                    if (product_id, last_page) not in self.crawled:
                        for current_page in range(2, last_page + 1):
                            self.crawled.add((product_id, current_page))
                            to_crawl = self.base_url.format(product_id, current_page)
                            yield scrapy.Request(to_crawl, self.parse)
                    
            else:
                return
        else:
            return