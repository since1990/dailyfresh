from django.contrib import admin
from goods.models import GoodsType, IndexGoodsBanner, IndexTypeGoodsBanner, GoodsSKU, Goods, IndexPromotionBanner


# Register your models here.
admin.site.register(Goods)
admin.site.register(GoodsType)
admin.site.register(GoodsSKU)
admin.site.register(IndexGoodsBanner)
admin.site.register(IndexTypeGoodsBanner)
admin.site.register(IndexPromotionBanner)