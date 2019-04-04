#_-*-_coding:_utf-8_-*-

#_Define_here_the_models_for_your_scraped_items
#
#_See_documentation_in:
#_http://doc.scrapy.org/en/latest/topics/items.html

import scrapy

class AmazonItem(scrapy.Item):
#_define_the_fields_for_your_item_here_like:

    handle = scrapy.Field()
    title = scrapy.Field()
    body = scrapy.Field()
    vendor_ = scrapy.Field()
    type_ = scrapy.Field()
    tags = scrapy.Field()
    published = scrapy.Field()
    option_1_name = scrapy.Field()
    option_1_value = scrapy.Field()
    option_2_name = scrapy.Field()
    option_2_value = scrapy.Field()
    option_3_name = scrapy.Field()
    option_3_value = scrapy.Field()
    variant_sku = scrapy.Field()
    variant_grams = scrapy.Field()
    variant_inventory_tracker = scrapy.Field()
    variant_inventory_quantity = scrapy.Field()
    variant_inventory_policy = scrapy.Field()
    variant_fulfillment_service = scrapy.Field()
    variant_price = scrapy.Field()
    price = scrapy.Field()
    variant_compare_at_price = scrapy.Field()
    variant_requires_shipping = scrapy.Field()
    variant_taxable = scrapy.Field()
    variant_barcode = scrapy.Field()
    image_src = scrapy.Field()
    image_position = scrapy.Field()
    image_alt_text = scrapy.Field()
    gift_card = scrapy.Field()
    variant_image = scrapy.Field()
    variant_weight_unit = scrapy.Field()
    variant_tax_code = scrapy.Field()
    prodact_url = scrapy.Field()
    availability = scrapy.Field()
    size_chart = scrapy.Field()
