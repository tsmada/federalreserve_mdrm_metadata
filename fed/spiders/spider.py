from scrapy.selector import Selector
from scrapy.utils.project import get_project_settings
from scrapy.item import Item
from scrapy.http import Request, FormRequest, TextResponse
from fed.items import AUD
from scrapy.spiders import CrawlSpider, BaseSpider
from scrapy.linkextractors.sgml import SgmlLinkExtractor
import sys, os, csv, time, uuid, re, string
import datetime
from time import sleep
import time


class Fed(CrawlSpider):
  name = "fed" ## Scrapy crawls this e.g., scrapy crawl fed
  allowed_domains = ['federalreserve.gov'] ## allowable URLs to crawl
  start_urls = ['https://www.federalreserve.gov/apps/reportforms/default.aspx', 'https://www.federalreserve.gov/apps/mdrm/data-dictionary'] ## Start URL endpoints

  def __init__(self, *args, **kwargs):
    self.requests_list = [] ## List to hold requests for generator method
    ### Download Forms
    # link = 'https://www.federalreserve.gov/apps/reportforms/default.aspx'
    # request = Request(link, callback=self.return_schedules)
    # self.requests_list.append(request)
    ### Extracts
    link = 'https://www.federalreserve.gov/apps/mdrm/data-dictionary'
    request = Request(link, callback=self.return_mdrm, dont_filter=True)
    self.requests_list.append(request)
    link = 'https://www.federalreserve.gov/apps/mdrm/series'
    request = Request(link, callback=self.return_mdrm_series, dont_filter=True)
    self.requests_list.append(request)

  def __del__(self):
    """Deleted."""
    print 'deleted'

  def parse(self, response):
    for r in self.requests_list:
        yield r

  def return_mdrm_series(self, response):
    hxs = Selector(response)
    table = hxs.xpath('//*[@id="tabledata"]//tr')
    i=0
    with open('data_dict_mdrm_hierarchy.csv', 'a+') as f:
      f.write('Main Series, Sub Series, Segmented Mnemonic, Title, Reporting Forms, Source, MainSeriesLink, SubSeriesLink, SegmentLink' + '\n')
      for xp in table:
        currentmain = str(None)
        mainserieslink = str(None)
        subserieslink = str(None)
        segmentlink = str(None)
        try:
          mainseries = xp.xpath('./td[1]/span/a/b/text()').extract()[0].strip()
          mainserieslink = 'https://www.federalreserve.gov/apps/mdrm/' + xp.xpath('./td[1]/span/a/@href').extract()[0].strip()
          currentmain = mainseries
        except:
          try:
            mainseries = xp.xpath('./td[1]/span/b/text()').extract()[0].strip()
            mainserieslink = str(None)
            currentmain = mainseries
          except:
            mainseries = currentmain
          mainseries = currentmain
        title = xp.xpath('./td[4]/text()').extract()[0].strip().replace('"',"'")
        try:
          reportform = xp.xpath('./td[5]//text()').extract()[1].strip().replace('"',"'")
        except:
          reportform = str(None)
        try:
          subseries = xp.xpath('./td[2]/span/a/b/text()').extract()[0].strip()
          subserieslink = 'https://www.federalreserve.gov/apps/mdrm/' + xp.xpath('./td[2]/span/a/@href').extract()[0].strip()
        except:
          subserieslink = str(None)
          try:
            subseries = xp.xpath('./td[2]/span/b/text()').extract()[0].strip()
          except:
            subseries = str(None)
        try:
          segment = xp.xpath('./td[3]/span/a/b/text()').extract()[0].strip()
          segmentlink = 'https://www.federalreserve.gov/apps/mdrm/' + xp.xpath('./td[3]/span/a/@href').extract()[0].strip()
        except:
          try:
            segment = xp.xpath('./td[3]/span/b/text()').extract()[0].strip()
            segmentlink = str(None)
          except:
            segment = str(None)
        #print mainseries, subseries, segment, mainserieslink, subserieslink, segmentlink
        f.write('"' + mainseries + '","' +subseries+ '","' +segment+ '","' + title+ '","' + reportform+'","' + response.url +'","' + mainserieslink +'","' + subserieslink +'","' + segmentlink +'"\n')
        i+=1




  def return_mdrm(self, response): ## Touch source books and write headers
    with open('data_dict_report_form.csv','a+') as f:
      f.write('Report Number, Report Name, Item Number, Description and Series, Source' + '\n')
    with open('data_dict_item_number.csv', 'a+') as f:
      f.write('Series, Start Date, End Date, Confidential, Item Type, Reporting Forms, Source, Description, Name' + '\n')
    with open('data_dict_series.csv', 'a+') as f:
      f.write('MDRM Item, Start Date, End Date, Item Name, Item Type, Reporting Forms, Source' + '\n')
    hxs = Selector(response)
    #print response.headers
    schedules = hxs.xpath('//*[@id="SelectedReportForm"]/option/text()').extract()
    reportkeys = hxs.xpath('//*[@id="SelectedReportForm"]/option/@value').extract()
    #print reportkeys
    link = 'https://www.federalreserve.gov/apps/mdrm/data-dictionary'
    i=1
    for report in schedules[1:]: ## For reports in dropdown search list -- Queue request with parse_mdrm callback
      #print report
      reportkey = reportkeys[i]
      #print reportkey
      now = datetime.datetime.now()
      request = FormRequest(link, formdata={
'Keyword':'',
'SelectedSeries.Key':'',
'search_by':'Report',
'SelectedReportForm.Key': reportkey,
'SelectedItemType.Key':'-1',
'DisplayItemShortTitle':'false',
'DisplayConfidentialItemsOnly':'false',
'SelectedCatalogItemReportingStatus.Key':'All',
'SelectedCatalogItemState.Key':'Opened',
'SelectedCatalogItemTimePeriod.Key':'Before',
'SelectedCatalogItemMonthRange.Key':str(now.month),
'SelectedCatalogItemDayRange.Key':str(now.day),
'SelectedCatalogItemYearRange.Key':str(now.year),
'SelectedCatalogItemMonthCeilingRange.Key':str(now.month),
'SelectedCatalogItemDayCeilingRange.Key':str(now.day),
'SelectedCatalogItemYearCeilingRange.Key':str(now.year),
'subchoice':'Search'
        },callback=lambda r, report=report:self.parse_mdrm(r, report), dont_filter=True)
      yield request
      i+=1

  def parse_mdrm(self, response, report): ## Data Dictionary Parsing Method
    hxs = Selector(response)
    table = hxs.xpath('/html/body/table//tr/td[@width="500"]')
    try:
      reportname = hxs.xpath('/html/body/div[3]/text()').extract()[0].strip().replace(',','~').replace('\r\n',' ').replace('\n',' ').encode('ascii','ignore')
      print reportname
      if "and Loan Holding Companies" in reportname:
        print reportname
        time.sleep(5)
      for xp in table:
        desc = xp.xpath('./text()').extract()[0].strip().replace('"',"'").strip().replace(',','~').replace('\r\n','').replace('\n','').encode('ascii','ignore')
        #print desc
        frb = xp.xpath('.//preceding-sibling::td[@scope="row"]/a/text()').extract()[0].strip().replace('"',"'").encode('ascii','ignore')
        link = 'https://www.federalreserve.gov' + str(xp.xpath('.//preceding-sibling::td[@scope="row"]/a/@href').extract()[0].strip())
        with open('data_dict_report_form.csv','a+') as f:
          f.write('"' + report + '","' + reportname + '","' + frb + '","' + desc +'","' + response.url +   '"\n') ## Write report_form.csv
        request = Request(link, callback=lambda r, frb=frb:self.item_parser(r, frb))
        #yield request
    except IndexError as e:
      reportname = ''

  def item_parser(self, response, itemnumber):
    hxs = Selector(response)
    table = hxs.xpath('/html/body/table//tr')
    filename = 'data_dict_item_number.csv'
    try:
      itemnumbername = hxs.xpath('/html/body/div[3]/text()').extract()[0].strip()
    except IndexError as e:
      itemnumbername = ''
    for xp in table:
      fulld = ''
      try:
        if len(xp.xpath('./td/a/@href').extract()) != 0:
          serieslink = 'https://www.federalreserve.gov' + xp.xpath('./td/a/@href').extract()[0].strip()
        if len(xp.xpath('./td/a/text()').extract()) != 0:
          series = xp.xpath('./td/a/text()').extract()[0].strip().replace('"',"'").encode('ascii','ignore')
        startdate = xp.xpath('./td[2]/text()').extract()[0].strip().encode('ascii','ignore')
        enddate = xp.xpath('./td[3]/text()').extract()[0].strip().encode('ascii','ignore')
        confidential = xp.xpath('./td[4]/text()').extract()[0].strip().replace('"',"'").encode('ascii','ignore')
        try:
          description = hxs.xpath('/html/body//p/text()').extract()[4:-1]
        except:
          print 'description indexing broke'
          time.sleep(1)
          description = hxs.xpath('/html/body//p/text()').extract()
        if series == 'IBFS2906':
          print description, len(description)
          time.sleep(2)
        for k, paragraph in enumerate(description):
          fulld = fulld + paragraph.encode('ascii','ignore').strip().replace('\r\n','').replace('"',"'") + ' '
            #print paragraph
        # print fulld
        # if len(description) == 1:
        #   #print description[0]
        #   description = description[0].replace(u'"',"'").strip()
        # else:
        #   if len(description[0]) < 4:
        #     description = description[1].replace(u'"',"'").strip()
        name = hxs.xpath('/html/body/div[3]/text()')[0].extract().encode('ascii','ignore')
        itemtype = xp.xpath('./td[5]/text()').extract()[0].strip().encode('ascii','ignore')
        reportingforms = xp.xpath('./td[6]/text()').extract()[0].strip().replace('"',"'").encode('ascii','ignore')
        if len(reportingforms) == 0 and len(series) != 0:
          multiplelink =  'https://www.federalreserve.gov' + xp.xpath('./td[6]/a/@href').extract()[0].strip()
          request = Request(multiplelink, callback=lambda r, filename=filename:self.multiple_forms(r, filename))
          yield request
        else:
          with open(filename, 'a+') as f:
            f.write('"' + series+ '","' + startdate+ '","' + enddate+ '","' + confidential+ '","' + itemtype+ '","' + reportingforms+'","' + response.url+'","' + str(fulld) +'","' + name + '"\n')
          request = Request(serieslink, callback=lambda r, series=series:self.series_parser(r, series))
          yield request
      except IndexError as e:
        print 'something broke on the description or name in item_number.csv', e
        pass

  def series_parser(self, response, series):
    hxs = Selector(response)
    table = hxs.xpath('/html/body/table[1]//tr')
    filename = 'data_dict_series.csv'
    for xp in table:
      try:
        mdrmlink = 'https://www.federalreserve.gov' + xp.xpath('./td/a/@href').extract()[0].strip()
        series = xp.xpath('./td/a/text()').extract()[0].strip().replace('"',"'")
        startdate = xp.xpath('./td[2]/text()').extract()[0].strip()
        enddate = xp.xpath('./td[3]/text()').extract()[0].strip()
        confidential = xp.xpath('./td[4]/text()').extract()[0].strip().replace('"',"'")
        itemtype = xp.xpath('./td[5]/text()').extract()[0].strip()
        reportingforms = xp.xpath('./td[6]/text()').extract()[0].strip().replace('"',"'")
        #print '+++', hxs.xpath('/html/body/p[4]/text()').extract()
        with open(filename, 'a+') as f:
          f.write('"' + series+ '","' + startdate+ '","' + enddate+ '","' + confidential+ '","' + itemtype+ '","' + reportingforms +'","' + response.url + '"\n')
        if len(reportingforms) == 0 and len(series) != 0:
          multiplelink =  'https://www.federalreserve.gov' + xp.xpath('./td[6]/a/@href').extract()[0].strip()
          request = Request(multiplelink, callback=lambda r, filename=filename:self.multiple_forms(r, filename))
          yield request
        # request = Request(mdrmlink, callback=lambda r:self.mdrm_parser(r, series))
        # yield request
      except:
        pass

  def multiple_forms(self, response, *args, **kwargs):
    filename = args[0]
    hxs = Selector(response)
    table = hxs.xpath('/html/body/table//tr')
    for xp in table:
      try:
        one = xp.xpath('./td/text()').extract()
        two = xp.xpath('./td[2]/text()').extract().replace('"',"'")
        three = xp.xpath('./td[3]/text()').extract().replace('"',"'")
        four = xp.xpath('./td[4]/text()').extract().replace('"',"'")
        five = xp.xpath('./td[5]/text()').extract().replace('"',"'")
        six = xp.xpath('./td[6]/text()').extract()
        with open(filename, 'a+') as f:
          f.write('"' + one + '","' + two + '","' + three + '","' + four + '","' + five + '","' + six +'","' + response.url + '"\n')
      except:
        pass



  # def mdrm_parser(self, response, series):
  #   hxs = Selector(response)
  #   table = hxs.xpath('/html/body/table[1]//tr')
  #   with open('data_dict_mdrm.csv', 'a+') as f:
  #     for xp in table:
  #       try:
  #         mdrmlink = 'https://www.federalreserve.gov' + xp.xpath('./td/a/@href').extract()[0].strip()
  #         mdrm = xp.xpath('./td/text()').extract()[0].strip()
  #         startdate = xp.xpath('./td[2]/text()').extract()[0].strip()
  #         enddate = xp.xpath('./td[3]/text()').extract()[0].strip()
  #         itemname = xp.xpath('./td[4]/text()').extract()[0].strip()
  #         itemtype = xp.xpath('./td[5]/text()').extract()[0].strip()
  #         reportingforms = xp.xpath('./td[5]/text()').extract()[0].strip()
  #         f.write(mdrm+ ',' + startdate+ ',' + enddate+ ',' + itemname+ ',' + itemtype+ ',' + reportingforms + '\n')
  #       except:
  #         pass



  def return_schedules(self, response):
    hxs = Selector(response)
    print response.headers
    schedules = hxs.xpath('//*[@id="MainContent_ddl_ReportForms"]/option/@value').extract()
    print "Parsing report"
    link = 'https://www.federalreserve.gov/apps/reportforms/default.aspx'
    for schedule in schedules[1:]:
      print schedule
      request = FormRequest(link, formdata={'__EVENTVALIDATION': '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',
        '__VIEWSTATE': '/wEPDwULLTE0NDE3ODY4NTUPZBYCZg9kFgQCAw9kFgYCAw8WAh4LXyFJdGVtQ291bnQCCRYSZg9kFgICAQ9kFgICAQ8PFgQeBFRleHQFFEZpbmFuY2lhbCBzdGF0ZW1lbnRzHgtOYXZpZ2F0ZVVybAUfY2F0ZWdvcnlpbmRleC5hc3B4P3hUZFRhK0ZhU2xJPWRkAgEPZBYCAgEPZBYCAgEPDxYEHwEFHUFwcGxpY2F0aW9ucy9zdHJ1Y3R1cmUgY2hhbmdlHwIFH2NhdGVnb3J5aW5kZXguYXNweD8rUGhrSndpQmpiQT1kZAICD2QWAgIBD2QWAgIBDw8WBB8BBQVGRklFQx8CBR9jYXRlZ29yeWluZGV4LmFzcHg/MS9SSVhPL1VkdUk9ZGQCAw9kFgICAQ9kFgICAQ8PFgQfAQUPTW9uZXRhcnkgcG9saWN5HwIFH2NhdGVnb3J5aW5kZXguYXNweD9MS1pSY1ZlOGdzWT1kZAIED2QWAgIBD2QWAgIBDw8WBB8BBQhSZXNlYXJjaB8CBR9jYXRlZ29yeWluZGV4LmFzcHg/ZEVhcHEyMmVCSTg9ZGQCBQ9kFgICAQ9kFgICAQ8PFgQfAQUYQnVzaW5lc3MvY29uc3VtZXIgY3JlZGl0HwIFH2NhdGVnb3J5aW5kZXguYXNweD8wWjVTMXBKYlNHZz1kZAIGD2QWAgIBD2QWAgIBDw8WBB8BBR9TZWN1cml0aWVzIEV4Y2hhbmdlIEFjdCBvZiAxOTM0HwIFH2NhdGVnb3J5aW5kZXguYXNweD9taTQxTHZvcGI5bz1kZAIHD2QWAgIBD2QWAgIBDw8WBB8BBSNNdW5pY2lwYWwgYW5kIGdvdmVybm1lbnQgc2VjdXJpdGllcx8CBR9jYXRlZ29yeWluZGV4LmFzcHg/TDg3N1Z3RWo5U3M9ZGQCCA9kFgICAQ9kFgICAQ8PFgQfAQUVQWN0aXZpdGllcyBtb25pdG9yaW5nHwIFH2NhdGVnb3J5aW5kZXguYXNweD9LWjlNcFA4bUVRWT1kZAIFD2QWAgIBDw8WAh8CBQ1+L3Jldmlldy5hc3B4ZGQCDQ9kFgICAQ8QDxYGHg1EYXRhVGV4dEZpZWxkBQpPcHRpb25OYW1lHg5EYXRhVmFsdWVGaWVsZAUIT3B0aW9uSWQeC18hRGF0YUJvdW5kZ2QQFYABElNlbGVjdCBmb3JtIG51bWJlcglGRklFQyAwMDEJRkZJRUMgMDAyCkZGSUVDIDAwMnMJRkZJRUMgMDA0CUZGSUVDIDAwNhRGRklFQyAwMDkvRkZJRUMgMDA5YQlGRklFQyAwMTkURkZJRUMgMDMwL0ZGSUVDIDAzMFMJRkZJRUMgMDMxCUZGSUVDIDA0MQlGRklFQyAxMDEJRkZJRUMgMTAyCEZvcm0gMTNGBkZvcm0gMwZGb3JtIDQGRm9ybSA1B0ZSIDEzNzkHRlIgMjAwNAdGUiAyMDA1B0ZSIDIwMDYMRlIgMjAwOWEvYi9jB0ZSIDIwMTIKRlIgMjAyOGEvcwpGUiAyMDI4Yi9zB0ZSIDIwMzAIRlIgMjAzMGEHRlIgMjA0NgdGUiAyMDUwCEZSIDIwNTFhCEZSIDIwNTJhCEZSIDIwNTJiB0ZSIDIwNTYHRlIgMjA1OAdGUiAyMDY0B0ZSIDIwNjkHRlIgMjA3MAhGUiAyMDgxYQhGUiAyMDgxYghGUiAyMDgxYwdGUiAyMDgyDUZSIDIwODMvQS9CL0MHRlIgMjA4NAdGUiAyMDg2CEZSIDIwODZhB0ZSIDIwODcHRlIgMjIyNQdGUiAyMjMwB0ZSIDIyNDgQRlIgMjMxNC9GUiAyMzE0UwxGUiAyMzE0YS9iL2MHRlIgMjMyMAdGUiAyNDE1B0ZSIDI0MTYHRlIgMjQyMAdGUiAyNDM2CEZSIDI1MDJxB0ZSIDI1MTIHRlIgMjU3MgdGUiAyNjQ0B0ZSIDI4MzUIRlIgMjgzNWEIRlIgMjg4NmIfRlIgMjkwMCAoQnJhbmNoZXMgYW5kIEFnZW5jaWVzKRpGUiAyOTAwIChDb21tZXJjaWFsIEJhbmtzKRdGUiAyOTAwIChDcmVkaXQgVW5pb25zKRtGUiAyOTAwIChTYXZpbmdzIGFuZCBMb2FucykIRlIgMjkxMGEHRlIgMjkxNQdGUiAyOTMwCEZSIDI5MzBhGkZSIDI5NTAgKENvbW1lcmNpYWwgQmFua3MpF0ZSIDI5NTAgKENyZWRpdCBVbmlvbnMpG0ZSIDI5NTAgKFNhdmluZ3MgYW5kIExvYW5zKQdGUiAyOTUxCkZSIDMwMzNwL3MHRlIgMzAzNghGUiBHLUZJTglGUiBHLUZJTlcGRlIgRy0xBkZSIEctMgZGUiBHLTMGRlIgRy00CkZSIEgtKGIpMTELRlIgSE1EQS1MQVIGRlIgSC02BkZSIEstMQZGUiBLLTIIRlIgTVNELTQIRlIgTVNELTUHRlIgVEEtMQZGUiBULTQGRlIgVS0xB0ZSIFhYLTEHRlIgWS0xZgZGUiBZLTMHRlIgWS0zRgdGUiBZLTNOBkZSIFktNAZGUiBZLTYHRlIgWS02QQZGUiBZLTcHRlIgWS03QRBGUiBZLTdOL0ZSIFktN05TB0ZSIFktN1EGRlIgWS04B0ZSIFktOUMIRlIgWS05Q1MIRlIgWS05RVMIRlIgWS05TFAIRlIgWS05U1AHRlIgWS0xMAhGUiBZLTEwRghGUiBZLTEwUxBGUiBZLTExL0ZSIFktMTFTCEZSIFktMTFJCEZSIFktMTFRB0ZSIFktMTIIRlIgWS0xMkEIRlIgWS0xNEEIRlIgWS0xNE0IRlIgWS0xNFEHRlIgWS0xNQdGUiBZLTE2B0ZSIFktMjADTVNEBE1TRFcGUmVnIEgyFYABATAJRkZJRUNfMDAxCUZGSUVDXzAwMgpGRklFQ18wMDJzCUZGSUVDXzAwNAlGRklFQ18wMDYURkZJRUNfMDA5L0ZGSUVDXzAwOWEJRkZJRUNfMDE5FEZGSUVDXzAzMC9GRklFQ18wMzBTCUZGSUVDXzAzMQlGRklFQ18wNDEJRkZJRUNfMTAxCUZGSUVDXzEwMghGb3JtXzEzRgZGb3JtXzMGRm9ybV80BkZvcm1fNQdGUl8xMzc5B0ZSXzIwMDQHRlJfMjAwNQdGUl8yMDA2DEZSXzIwMDlhL2IvYwdGUl8yMDEyCkZSXzIwMjhhL3MKRlJfMjAyOGIvcwdGUl8yMDMwCEZSXzIwMzBhB0ZSXzIwNDYHRlJfMjA1MAhGUl8yMDUxYQhGUl8yMDUyYQhGUl8yMDUyYgdGUl8yMDU2B0ZSXzIwNTgHRlJfMjA2NAdGUl8yMDY5B0ZSXzIwNzAIRlJfMjA4MWEIRlJfMjA4MWIIRlJfMjA4MWMHRlJfMjA4Mg1GUl8yMDgzL0EvQi9DB0ZSXzIwODQHRlJfMjA4NghGUl8yMDg2YQdGUl8yMDg3B0ZSXzIyMjUHRlJfMjIzMAdGUl8yMjQ4EEZSXzIzMTQvRlJfMjMxNFMMRlJfMjMxNGEvYi9jB0ZSXzIzMjAHRlJfMjQxNQdGUl8yNDE2B0ZSXzI0MjAHRlJfMjQzNghGUl8yNTAycQdGUl8yNTEyB0ZSXzI1NzIHRlJfMjY0NAdGUl8yODM1CEZSXzI4MzVhCEZSXzI4ODZiCUZSXzI5MDBiYQlGUl8yOTAwY2IJRlJfMjkwMGN1CUZSXzI5MDBzbAhGUl8yOTEwYQdGUl8yOTE1B0ZSXzI5MzAIRlJfMjkzMGEJRlJfMjk1MGNiCUZSXzI5NTBDVQlGUl8yOTUwc2wHRlJfMjk1MQpGUl8zMDMzcC9zB0ZSXzMwMzYIRlJfRy1GSU4JRlJfRy1GSU5XBkZSX0ctMQZGUl9HLTIGRlJfRy0zBkZSX0ctNApGUl9ILShiKTExC0ZSX0hNREEtTEFSBkZSX0gtNgZGUl9LLTEGRlJfSy0yCEZSX01TRC00CEZSX01TRC01B0ZSX1RBLTEGRlJfVC00BkZSX1UtMQdGUl9YWC0xB0ZSX1ktMWYGRlJfWS0zB0ZSX1ktM0YHRlJfWS0zTgZGUl9ZLTQGRlJfWS02B0ZSX1ktNkEGRlJfWS03B0ZSX1ktN0EQRlJfWS03Ti9GUl9ZLTdOUwdGUl9ZLTdRBkZSX1ktOAdGUl9ZLTlDCEZSX1ktOUNTCEZSX1ktOUVTCEZSX1ktOUxQCEZSX1ktOVNQB0ZSX1ktMTAIRlJfWS0xMEYIRlJfWS0xMFMQRlJfWS0xMS9GUl9ZLTExUwhGUl9ZLTExSQhGUl9ZLTExUQdGUl9ZLTEyCEZSX1ktMTJBCEZSX1ktMTRBCEZSX1ktMTRNCEZSX1ktMTRRB0ZSX1ktMTUHRlJfWS0xNgdGUl9ZLTIwA01TRARNU0RXBlJlZ19IMhQrA4ABZ2dnZ2dnZ2dnZ2dnZ2dnZ2dnZ2dnZ2dnZ2dnZ2dnZ2dnZ2dnZ2dnZ2dnZ2dnZ2dnZ2dnZ2dnZ2dnZ2dnZ2dnZ2dnZ2dnZ2dnZ2dnZ2dnZ2dnZ2dnZ2dnZ2dnZ2dnZ2dnZ2dnZ2dnZ2dnZ2dnZ2dnZ2dnZ2dnZ2dnZ2dnZ2dnZ2dkZAIFDxYCHwEF7QQ8ZGl2IGNsYXNzPSJzZWNvbmRhcnlGb290ZXJMaW5rc0xlZnQiPgogICAgICAgICAgICAgICA8YSBocmVmPSIvYWNjZXNzaWJpbGl0eS5odG0iPkFjY2Vzc2liaWxpdHk8L2E+CiAgICAgICAgICAgICAgIDxhIGhyZWY9Ii9hYm91dHRoZWZlZC9jb250YWN0LXVzLXRvcGljcy5odG0iPkNvbnRhY3QgdXM8L2E+CiAgICAgICAgICAgICAgIDxhIGhyZWY9Ii9kaXNjbGFpbWVyLmh0bSI+RGlzY2xhaW1lcjwvYT4KICAgICAgICAgICAgICAgPGEgaHJlZj0iL3BvbGljaWVzLmh0bSI+V2Vic2l0ZSBwb2xpY2llczwvYT4KICAgICAgICAgICAgICAgPGEgaHJlZj0iL2ZvaWEvYWJvdXRfZm9pYS5odG0iPkZPSUE8L2E+CjwvZGl2Pgo8ZGl2IGNsYXNzPSJzZWNvbmRhcnlGb290ZXJMaW5rc1JpZ2h0Ij4KICAgICAgICAgICAgICAgPGEgaHJlZj0iaHR0cDovL3d3dy5hZG9iZS5jb20vcHJvZHVjdHMvYWNyb2JhdC9yZWFkc3RlcDIuaHRtbCI+UERGIFJlYWRlcjwvYT48aW1nIHNyYz0nL0dJRkpQRy9leGl0SWNvbi5naWYnIGFsdD0iTGVhdmluZyB0aGUgQm9hcmQiIGJvcmRlcj0iMCIgY2xhc3M9ImV4aXRJY29uIiAvPgogICAgICAgICAgICAgICA8ZGl2IGNsYXNzPSJjbGVhciI+PC9kaXY+CjwvZGl2PgpkZKM1wCsz+B3fLY3wfUB1qGxaN1blWWLBO/GsFiuVzqll',
        '__VIEWSTATEGENERATOR':'664BC42A','ctl00$MainContent$ddl_ReportForms': schedule, 'ctl00$MainContent$h_FormId':'', 'ctl00$MainContent$btn_GetForm':'Submit Query'}, headers={'Accept':'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8', 'Content-Type':'application/x-www-form-urlencoded'},callback=lambda r:self.parse_report(r), dont_filter=True)
      yield request

  def parse_report(self, response):
    hxs = Selector(response)
    link = None
    links = []
    if 'http://www.ffiec.gov/ffiec_report_forms.htm' not in response.body:
      #links.append('https://www.federalreserve.gov' + hxs.xpath('//*[@id="printThis"]//*/a[@href]/@href')[0].extract())
      for path in hxs.xpath('//*[@id="formLinks"]//*/a[@href]/@href').extract()[0:2]:
        links.append('https://www.federalreserve.gov' + path)
    else:
      links.append(hxs.xpath('//*[@id="printThis"]//*/a[@href]/@href')[0].extract())
    for link in links:
      if link is not None and '.pdf' in link:
        reportname = link.split('/')[-1]
        request = Request(link, callback=lambda r:self.download_pdf(r, reportname))
        yield request


  def download_pdf(self, response, report):
    with open(report, 'wb+') as f:
      f.write(response.body)