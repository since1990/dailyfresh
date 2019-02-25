from django.contrib import admin
from goods.models import GoodsType, IndexGoodsBanner, IndexTypeGoodsBanner
from goods.models import GoodsSKU, Goods, IndexPromotionBanner, GoodsImage
from django.core.cache import cache


class BaseModelAdmin(admin.ModelAdmin):
    def save_model(self, request, obj, form, change):
        '''新增或更新表中的数据时调用'''
        super().save_model(request, obj, form, change)

        # 发出任务，让celery worker重新生成首页静态页
        from celery_tasks.tasks import generate_static_index_html
        generate_static_index_html.delay()

        # 清除首页的缓存数据
        cache.delete('index_page_data')

    def delete_model(self, request, obj):
        '''删除表中的数据时调用'''
        super().delete_model(request, obj)
        # 发出任务，让celery worker重新生成首页静态页
        from celery_tasks.tasks import generate_static_index_html
        generate_static_index_html.delay()

        # 清除首页的缓存数据
        cache.delete('index_page_data')


# Register your models here.
admin.site.register(GoodsImage, BaseModelAdmin)
admin.site.register(Goods, BaseModelAdmin)
admin.site.register(GoodsType, BaseModelAdmin)
admin.site.register(GoodsSKU, BaseModelAdmin)
admin.site.register(IndexGoodsBanner, BaseModelAdmin)
admin.site.register(IndexTypeGoodsBanner, BaseModelAdmin)
admin.site.register(IndexPromotionBanner, BaseModelAdmin)