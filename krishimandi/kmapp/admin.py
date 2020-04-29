from django.contrib import admin
from . models import State,District,Market,Commodity,Variety,CommodityPrice
# Register your models here.
admin.site.register(State)
admin.site.register(District)
admin.site.register(Market)
admin.site.register(Commodity)
admin.site.register(Variety)
admin.site.register(CommodityPrice)
