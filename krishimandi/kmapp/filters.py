import django_filters
from django_filters import DateFilter, CharFilter
from .models import Variety
from .models import *

class PriceFilter(django_filters.FilterSet):
	from_date = DateFilter(field_name='arrival_date',lookup_expr='gte') 
	to_date = DateFilter(field_name='arrival_date',lookup_expr='lte')
	class Meta:
		model = CommodityPrice
		fields = '__all__'
		exclude = ['variety','arrival_date','min_price','modal_price','max_price','timestamp']


