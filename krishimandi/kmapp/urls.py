from django.urls import path
from . import views

urlpatterns = [
    path('state/',views.retrieve_state,name="states"),
    path('state/district/<int:state_id>',views.retrieve_district,name="district"),
    path('state/district/market/<int:district_id>',views.retrieve_market,name="market"),
    path('state/district/market/commodity/<int:market_id>',views.retrieve_commodity, name="commodity"),
    path('state/district/market/commodity/variety/<int:commodity_id>',views.retrieve_variety,name="variety"),
    path('state/district/market/commodity/variety/commodity_price/<int:variety_id>',views.retrieve_commodity_price, name="commodity_price"),
    path('create/commodity_price',views.create_commodity_price,name="commodity_price"),
    path('state/district/market/weather/<int:market_id>', views.retrieve_weather,
         name="weather"),
    path('seed_dealers/',views.seed_dealers,name="seed_dealers"),
    path('compare_by_markets/<market_name>/<commodity_name>/<variety_name>', views.compare_by_market, name="compare"),
    path('compare_by_dates/<market_name>/<commodity_name>/<variety_name>', views.compare_by_dates, name="compare1"),

    #by kishan
    path('price',views.get_prize,name='price'),
    path('graph',views.get_graph,name='graph'),
    path('compare_market',views.compare_market,name='compare_market'),
    path('weather',views.show_weather,name='show_weather'),
    path('ajax/load-districts/', views.load_districts, name='ajax_load_districts'),
    path('ajax/load-markets/', views.load_markets, name='ajax_load_markets'),
    path('ajax/load-commodities/', views.load_commodities, name='ajax_load_commodities'),
    path('ajax/load-varieties/', views.load_varieties, name='ajax_load_varieties'),
]
