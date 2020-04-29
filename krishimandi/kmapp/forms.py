from django import forms
from .models import CommodityPrice,District,Market
from django.db import models
class testform(forms.ModelForm):
	class Meta:
		model = CommodityPrice
		fields = ('state','district','market','commodity','variety')
	def __init__(self,*args,**kwargs):
		super().__init__(*args,**kwargs)
		self.fields['district'].queryset = District.objects.none()
		self.fields['market'].queryset = Market.objects.none()
		self.fields['commodity'].queryset = District.objects.none()
		self.fields['variety'].queryset = District.objects.none()

class weatherform(forms.ModelForm):
	class Meta:
		model = CommodityPrice
		fields = ('state','district','market',)
	def __init__(self,*args,**kwargs):
		super().__init__(*args,**kwargs)
		self.fields['district'].queryset = District.objects.none()
		self.fields['market'].queryset = Market.objects.none()


	


