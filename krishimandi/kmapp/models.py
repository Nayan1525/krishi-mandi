from django.db import models
from datetime import datetime, timedelta


class State(models.Model):
    state_name = models.CharField(max_length=30, default=None)

    def __str__(self):
        return self.state_name

    class Meta:
        db_table = "state_info"
        ordering = ['id']


class District(models.Model):
    state = models.ForeignKey(State, on_delete=models.CASCADE)
    district_name = models.CharField(max_length=30, default=None)

    def __str__(self):
        return self.district_name
    class Meta:
        db_table = "district_info"
        ordering = ['id']


class Market(models.Model):
    district = models.ForeignKey(District, on_delete=models.CASCADE)
    market_name = models.CharField(max_length=30, default=None)

    def __str__(self):
        return self.market_name
    class Meta:
        db_table = "market_info"
        ordering = ['id']


class Commodity(models.Model):
    market = models.ForeignKey(Market, on_delete=models.CASCADE)
    commodity_name = models.CharField(max_length=30, default=None)

    def __str__(self):
        return self.commodity_name

    class Meta:
        db_table = "commodity_info"
        ordering = ['id']


class Variety(models.Model):
    commodity = models.ForeignKey(Commodity, on_delete=models.CASCADE)
    variety_name = models.CharField(max_length=30, default=None)

    def __str__(self):
        return self.variety_name

    class Meta:
        db_table = "variety_info"
        ordering = ['id']

#from date , to date, variety, commodity, market, district,state, min_price ,max_price 
class CommodityPrice(models.Model):
    arrival_date = models.DateField(null=True, blank=True)
    variety = models.ForeignKey(Variety, on_delete=models.CASCADE)
    commodity = models.ForeignKey(Commodity, on_delete=models.CASCADE)
    market = models.ForeignKey(Market, on_delete=models.CASCADE)
    district = models.ForeignKey(District, on_delete=models.CASCADE)
    state = models.ForeignKey(State, on_delete=models.CASCADE)
    min_price = models.FloatField(null=True, blank=True)
    modal_price = models.FloatField(max_length=50,null=True, blank=True)
    max_price = models.FloatField(null=True, blank=True)
    timestamp = models.IntegerField(null=True, blank=True)


    class Meta:
        db_table = "commodity_price_info"
        ordering = ['arrival_date']
