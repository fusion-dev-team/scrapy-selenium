# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html


# from scrapy.exporter import XmlItemExporter

# class ProductXmlExporter(XmlItemExporter):

#     def serialize_field(self, field, name, value):
#         if field == 'price':
#             return '$ %s' % str(value)
#         return super(Product, self).serialize_field(field, name, value)

import csv

class AmazonPipeline(object):

    # def __init__(self):
    #     self.csvwriter = csv.writer(open('items.csv', 'a'))

    def process_item(self, item, AmazonProductSpider):
        # build your row to export, then export the row
        # row = []
        # for key in item:
        #     row.append(item[key])
        # # self.csvwriter.writerow(item)
        # self.csvwriter.writerow(row)
        return item
