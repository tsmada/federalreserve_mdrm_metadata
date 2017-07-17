# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class ACQ1(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()

    reportnum = scrapy.Field()
    reportname = scrapy.Field()
    itemnum = scrapy.Field()
    itemname = scrapy.Field()
    sourceurl = scrapy.Field()
    pass

class ACQ2(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()

    mdrmnum = scrapy.Field()
    itemname = scrapy.Field()
    itemdesc = scrapy.Field()
    startdate = scrapy.Field()
    enddate = scrapy.Field()
    confidential = scrapy.Field()
    itemtype = scrapy.Field()
    reportnum = scrapy.Field()
    reportname = scrapy.Field()
    sourceurl = scrapy.Field()
    pass

class ACQ3(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()

    mdrmnum = scrapy.Field()
    startdate = scrapy.Field()
    enddate = scrapy.Field()
    confidential = scrapy.Field()
    itemname = scrapy.Field()
    itemtype = scrapy.Field()
    reportnum = scrapy.Field()
    sourceurl = scrapy.Field()
    pass


class ACQ4(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()

    mainseries = scrapy.Field()
    subseries = scrapy.Field()
    segment = scrapy.Field()
    seriesname = scrapy.Field()
    reportforms = scrapy.Field()
    sourceurl = scrapy.Field()
    mainseriesurl = scrapy.Field()
    subseriesurl = scrapy.Field()
    segurl = scrapy.Field()
    pass

class AUD(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()

    download_exception_count = scrapy.Field()
    download_exception_type_count = scrapy.Field()
    download_request_bytes = scrapy.Field()
    download_request_count = scrapy.Field()
    download_request_method_post_count = scrapy.Field()
    download_request_method_get_count = scrapy.Field()
    download_response_bytes = scrapy.Field()
    download_response_count = scrapy.Field()
    download_response_status_200_count = scrapy.Field()
    download_response_status_404_count = scrapy.Field()
    duplicate_filtered = scrapy.Field()
    finish_reason = scrapy.Field()
    finish_time = scrapy.Field()
    log_count_debug = scrapy.Field()
    log_count_error = scrapy.Field()
    log_count_info = scrapy.Field()
    request_max_depth = scrapy.Field()
    response_received_count = scrapy.Field()
    scheduler_dequeued = scrapy.Field()
    scheduler_dequeued_memory = scrapy.Field()
    scheduler_enqueued = scrapy.Field()
    scheduler_enqueued_memory = scrapy.Field()
    spider_exception_encoding_error = scrapy.Field()
    start_time = scrapy.Field()
    pass


