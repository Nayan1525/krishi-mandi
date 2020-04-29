from ..models import State,District,Market,Commodity,Variety,CommodityPrice
import json
import requests
import datetime

def insert_commodity_price_data():
    data = requests.get("https://api.data.gov.in/resource/9ef84268-d588-465a-a308-a864a43d0070?api-key=579b464db66ec23bdd0000010fb0d1364fe743d955e4b61089c397b1&limit=10000&offset=0&format=json")

    if data.status_code == 200:
        x = json.loads(data.text)
        records = x['records']
        for record in records:
            stored_state , is_created = State.objects.update_or_create(state_name=record['state'])
            stored_district, is_created=District.objects.update_or_create(district_name=record["district"],state=stored_state)
            stored_market,is_created=Market.objects.update_or_create(market_name=record["market"],district=stored_district)
            stored_commodity, is_created = Commodity.objects.update_or_create(commodity_name=record["commodity"],market=stored_market)
            stored_variety, is_created = Variety.objects.update_or_create(variety_name=record["variety"],commodity=stored_commodity)
            commodity_price_obj,is_created = CommodityPrice.objects.update_or_create(state=stored_state,
                                                                          district=stored_district,
                                                                          market=stored_market,
                                                                          commodity=stored_commodity,
                                                                          variety=stored_variety,
                                                                          arrival_date=datetime.datetime.strptime(record["arrival_date"], "%d/%m/%Y").date().strftime("%Y-%m-%d"))
            commodity_price_obj.max_price = record['max_price']
            commodity_price_obj.min_price = record['min_price']
            commodity_price_obj.modal_price = record['modal_price']
            commodity_price_obj.timestamp = record["timestamp"]
            commodity_price_obj.save()




