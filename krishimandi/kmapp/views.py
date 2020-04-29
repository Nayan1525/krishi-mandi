from django.shortcuts import render,get_object_or_404
import pandas as pd
from .models import State,District,Market,Commodity,Variety,CommodityPrice
import json
from .utils import response_helper
from django.http.response import HttpResponse
from django.core import serializers
from .services.commodity_service import insert_commodity_price_data
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from yahoo_weather.weather import YahooWeather
from yahoo_weather.config.units import Unit
from datetime import datetime, timedelta
from krishimandi import dash_app
from dash.dependencies import Output,Input
from dash.dependencies import State as St
import dash_core_components as dcc
import dash_html_components as html
import dash_table
from django.db.models import Q



#added by kishah
from .filters import PriceFilter
from .forms import testform,weatherform
from django.urls import reverse
from django.shortcuts import redirect
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from myapp.decorators import farmer_required



def load_districts(request):
    state_id = request.GET.get('state')
    districts = District.objects.filter(state_id=state_id).order_by('district_name')
    return render(request, 'kmapp/hr/district_dropdown_list_options.html', {'districts': districts})

def load_markets(request):
    district_id = request.GET.get('district')
    markets = Market.objects.filter(district_id=district_id).order_by('market_name')
    return render(request, 'kmapp/hr/market_dropdown_list_options.html', {'markets': markets})

def load_commodities(request):
    market_id = request.GET.get('market')
    commodities = Commodity.objects.filter(market_id=market_id).order_by('commodity_name')
    return render(request, 'kmapp/hr/commodity_dropdown_list_options.html', {'commodities': commodities})

def load_varieties(request):
    commodity_id = request.GET.get('commodity')
    varieties = Variety.objects.filter(commodity_id=commodity_id).order_by('variety_name')
    return render(request, 'kmapp/hr/variety_dropdown_list_options.html', {'varieties': varieties})

@login_required
def get_graph(request):
    if request.method=='GET':
        state = request.GET.get('state') 
        district = request.GET.get('district')
        market = request.GET.get('market')
        commodity = request.GET.get('commodity')
        variety = request.GET.get('variety')
        if (state is not None) and (district is not None) and (market is not None) and (commodity is not None) and (variety is not None):
            state_name = State.objects.get(id=state)
            district_name = District.objects.get(id=district)
            market_name = Market.objects.get(id=market)
            commodity_name = Commodity.objects.get(id=commodity)
            variety_name = Variety.objects.get(id=variety)
            try:
                market = Market.objects.filter(market_name=market_name)
                commodity = Commodity.objects.filter(commodity_name=commodity_name, market__id__in=market)
                variety = Variety.objects.filter(variety_name=variety_name, commodity__id__in=commodity)
                commodity_price_graph = CommodityPrice.objects.filter(variety__id__in=variety).values()
                commodity_price = CommodityPrice.objects.filter(variety__id__in=variety)

                df = pd.DataFrame([commodity_price_graph for commodity_price_graph in commodity_price_graph])

                list_market_name = []
                list_commodity_name = []
                list_variety_name = []

                for index in range((df['market_id'].shape)[0]):
                    market_obj = Market.objects.get(pk=df['market_id'][index])
                    commodity_obj = Commodity.objects.get(pk=df['commodity_id'][index])
                    variety_obj = Variety.objects.get(pk=df['variety_id'][index])

                    list_market_name.append(str(market_obj.market_name))
                    list_commodity_name.append(str(commodity_obj.commodity_name))
                    list_variety_name.append(str(variety_obj.variety_name))


                df.loc[0:int((df['market_id'].shape)[0]), 'market_id'] = list_market_name
                df.loc[0:int((df['commodity_id'].shape)[0]), 'commodity_id'] = list_commodity_name
                df.loc[0:int((df['variety_id'].shape)[0]), 'variety_id'] = list_variety_name

                df = df.drop(columns=['id','district_id','state_id','timestamp'])
                df = df.rename(
                    columns={'arrival_date': 'Arrival Date', 'variety_id': 'Variety Name', 'commodity_id': 'Commodity Name',
                             'market_id': 'Market Name', 'min_price': 'Min Price', 'max_price': 'Max Price',
                             'modal_price': 'Modal Price'
                             })
                df = df[['Arrival Date', 'Market Name', 'Commodity Name', 'Variety Name', 'Min Price', 'Modal Price', 'Max Price']]


                def serve_layout():
                    return html.Div([
                        dash_table.DataTable(
                            id='table',
                            columns=[{"name": i, "id": i} for i in df.columns],
                            data=df.to_dict('records'),
                        ),
                        dcc.Graph(
                            id="graph-1",
                            figure=dict(
                                data=[
                                    dict(

                                        x=df['Arrival Date'],
                                        y=df['Max Price'],
                                        name='max price',
                                        type='line',
                                        marker=dict(
                                            color='rgb(55, 83, 109)'
                                        )
                                    ),
                                    dict(
                                        x=df['Arrival Date'],
                                        y=df['Min Price'],
                                        name='min price',
                                        type='line',
                                        marker=dict(
                                            color='rgb(255, 150, 100)'
                                        )
                                    ),
                                    dict(
                                        x=df['Arrival Date'],
                                        y=df['Modal Price'],
                                        name='modal price',
                                        type='line',
                                        marker=dict(
                                            color='rgb(120, 50, 25)'
                                        )
                                    )
                                ],
                                layout=dict(
                                    title='arrival date vs price',
                                    xaxis=dict(
                                        title='arrival date',
                                        tickformat='%Y %m %d',
                                        tickmode='linear'
                                    ),
                                    yaxis=dict(
                                        title='prices'
                                    ),
                                )
                            )
                        )
                    ])

                dash_app.app.layout = serve_layout

            except Exception as e:
                print(e)
                return response_helper.server_error_response()

        
    form = testform()  
    if (state is not None) and (district is not None) and (market is not None) and (commodity is not None) and (variety is not None):
        context = {'form':form,'lock':'something'}     
    else:
        context = {'form':form}    
    return render(request,'kmapp/graph.html',context)

@login_required
def compare_market(request):
    if request.method=='GET':
        state = request.GET.get('state') 
        district = request.GET.get('district')
        market = request.GET.get('market')
        commodity = request.GET.get('commodity')
        variety = request.GET.get('variety')
        if (state is not None) and (district is not None) and (market is not None) and (commodity is not None) and (variety is not None):
            state_name = State.objects.get(id=state)
            district_name = District.objects.get(id=district)
            market_name = Market.objects.get(id=market)
            commodity_name = Commodity.objects.get(id=commodity)
            variety_name = Variety.objects.get(id=variety)
            
            try:
                market = Market.objects.filter(
                    district__id__in = Market.objects.filter(market_name=market_name).values_list('district',flat=True))
                commodity = Commodity.objects.filter(commodity_name=commodity_name,market__id__in=market)
                variety = Variety.objects.filter(variety_name=variety_name,commodity__id__in=commodity)
                commodity_price_graph = CommodityPrice.objects.filter(variety__id__in=variety).values()
                commodity_price = CommodityPrice.objects.filter(variety__id__in=variety)

                df = pd.DataFrame([commodity_price_graph for commodity_price_graph in commodity_price_graph])

                arrival_date = list(arrival_date.strftime('%Y %m %d') for arrival_date in df['arrival_date'])
                base_date = datetime.today().date().strftime('%Y %m %d')
                date = max(arrival_date for arrival_date in arrival_date if arrival_date <= base_date)
                my_date = datetime.strptime(date,'%Y %m %d').date()

                da = df[(df['arrival_date'] == my_date )]
                da = da.reset_index()

                list_market_name = []
                list_commodity_name = []
                list_variety_name = []

                for index in range((da['market_id'].shape)[0]):
                    market_obj = Market.objects.get(pk=da['market_id'][index])
                    commodity_obj = Commodity.objects.get(pk=da['commodity_id'][index])
                    variety_obj = Variety.objects.get(pk=da['variety_id'][index])

                    list_market_name.append(str(market_obj.market_name))
                    list_commodity_name.append(str(commodity_obj.commodity_name))
                    list_variety_name.append(str(variety_obj.variety_name))


                da.loc[0:int((da['market_id'].shape)[0]),'market_id'] = list_market_name
                da.loc[0:int((da['commodity_id'].shape)[0]),'commodity_id'] = list_commodity_name
                da.loc[0:int((da['variety_id'].shape)[0]), 'variety_id'] = list_variety_name


                da = da.drop(columns=['id','district_id','state_id','timestamp'])

                da = da.rename(columns={'arrival_date':'Arrival Date','variety_id':'Variety Name','commodity_id':'Commodity Name',
                                        'market_id':'Market Name','min_price':'Min Price','max_price':'Max Price','modal_price':'Modal Price'
                                        })
                da = da[['Arrival Date','Market Name','Commodity Name','Variety Name','Min Price','Modal Price','Max Price']]

                def serve_layout():
                    return html.Div([
                        dash_table.DataTable(
                            id='table',
                            columns=[{"name": i, "id": i} for i in da.columns],
                            data=da.to_dict('records'),
                        ),
                        dcc.Graph(
                            id="graph-1",
                            figure=dict(
                                data=[
                                    dict(

                                        x=da['Market Name'],
                                        y=da['Max Price'],
                                        name='max price',
                                        type='bar',
                                        marker=dict(
                                            color='rgb(55, 83, 109)'
                                        )
                                    ),
                                    dict(
                                        x=da['Market Name'],
                                        y=da['Min Price'],
                                        name='min price',
                                        type='bar',
                                        marker=dict(
                                            color='rgb(255, 150, 100)'
                                        )
                                    ),
                                    dict(
                                        x=da['Market Name'],
                                        y=da['Modal Price'],
                                        name='modal price',
                                        type='bar',
                                        marker=dict(
                                            color='rgb(120, 50, 25)'
                                        )
                                    )
                                ],
                                layout=dict(
                                    title='market vs price',
                                    xaxis=dict(
                                        title='market name',
                                    ),
                                    yaxis=dict(
                                        title='prices'
                                    )
                                )
                            )
                        )
                    ])

                dash_app.app.layout = serve_layout

                

            except Exception as e:
                print(e)
                return response_helper.server_error_response()
   
    form = testform()  
    if (state is not None) and (district is not None) and (market is not None) and (commodity is not None) and (variety is not None):
        context = {'form':form,'lock':'something'}     
    else:
        context = {'form':form}    
    return render(request,'kmapp/compare_market.html',context)

def show_weather(request):
    if request.method=='GET':
        state = request.GET.get('state') 
        district = request.GET.get('district')
        market = request.GET.get('market')
        if (state is not None) and (district is not None) and (market is not None):
            state_name = State.objects.get(id=state)
            district_name = District.objects.get(id=district)
            market_name = Market.objects.get(id=market)
            
            try:
                # market = get_object_or_404(Market, pk=market_id)
                # market_name = market.market_name
                data = YahooWeather(APP_ID="xg9emu6o",
                                    api_key="dj0yJmk9R0EwRVIxMFVoV25KJmQ9WVdrOWVHYzVaVzExTm04bWNHbzlNQS0tJnM9Y29uc3VtZXJzZWNyZXQmc3Y9MCZ4PWI2",
                                    api_secret="35b08b1e830b532f2d497d06b7074eda066cae4d")
                data.get_yahoo_weather_by_city(market_name, Unit.celsius)
                text = data.condition.text
                tempreture = data.condition.temperature
                sunrise = data.astronomy.sunrise
                sunset = data.astronomy.sunset
                humadity = data.atmosphere.humidity
                pressure = data.atmosphere.pressure
                visibility = data.atmosphere.visibility
                speed = data.wind.speed
                direction = data.wind.direction
                lat = data.location.lat
                log = data.location.long

                
            except Exception as e:
                print(e)
                return response_helper.server_error_response()

   
    form = weatherform()  
    if (state is not None) and (district is not None) and (market is not None):
        context = {'form':form,'lock':'something',"market": market,'text': text,
                                                      'tempreture': tempreture, 'sunrise': sunrise, 'sunset': sunset,
                                                      'humadity': humadity, 'pressure': pressure, 'visibility': visibility,
                                                      'speed': speed, 'direction': direction,'lat':lat,'log':log}     
    else:
        context = {'form':form}    
    return render(request,'kmapp/show_weather.html',context)


def get_prize(request):
    prices = CommodityPrice.objects.order_by('-arrival_date').order_by('-variety')
    priceFilter = PriceFilter(request.GET,queryset=prices)
    prices = priceFilter.qs
    price_paginator = Paginator(prices,20)
    price_page_number = request.GET.get('page')
    prices = price_paginator.get_page(price_page_number)
    context = {'prices':prices,'priceFilter':priceFilter}
    return render(request,'kmapp/mandi_prize.html',context)

# old once added by nayan
def retrieve_state(request):
    try:
        state = State.objects.filter().values("id","state_name")
        # state_obj = State.objects.filter().values("id","state_name")
            # state_paginator = Paginator(state_obj,10)
            # state_page_number = request.GET.get('page')
            # state = state_paginator.get_page(state_page_number)
        return render(request,"state.html",{"state":state})
    except Exception as e:
        print(e)
        return response_helper.server_error_response()

def retrieve_district(request,state_id):
    try:
        state = get_object_or_404(State,pk=state_id)
        district = District.objects.filter(state_id=state_id)
        # district_paginator = Paginator(district_obj,10)
        # district_page_number = request.GET.get('page')
        # district = district_paginator.get_page(district_page_number)
        return render(request,"district.html",{'state':state,'district':district})
    except Exception as e:
        print(e)
        return response_helper.server_error_response()

def retrieve_market(request,district_id):
    try:
        district = get_object_or_404(District,pk=district_id)
        market = Market.objects.filter(district_id=district_id)
        # market_paginator = Paginator(market_obj, 10)
        # market_page_number = request.GET.get('page')
        # market = market_paginator.get_page(market_page_number)
        return render(request,"market.html",{"district":district,'market':market})
    except Exception as e:
        print(e)
        return response_helper.server_error_response()

def retrieve_commodity(request,market_id):
    try:
        market = get_object_or_404(Market,pk=market_id)
        commodity = Commodity.objects.filter(market_id=market_id)
        # commodity_paginator = Paginator(commodity_obj, 10)
        # commodity_page_number = request.GET.get('page')
        # commodity = commodity_paginator.get_page(commodity_page_number)
        return render(request,"commodity.html",{"market":market,'commodity':commodity})
    except Exception as e:
        print(e)
        return response_helper.server_error_response()

def retrieve_variety(request,commodity_id):
    try:
        commodity = get_object_or_404(Commodity,pk=commodity_id)
        variety = Variety.objects.filter(commodity_id=commodity_id)
        # variety_paginator = Paginator(variety_obj, 10)
        # variety_page_number = request.GET.get('page')
        # variety = variety_paginator.get_page(variety_page_number)
        return render(request,"variety.html",{"commodity":commodity,'variety':variety})
    except Exception as e:
        print(e)
        return response_helper.server_error_response()

def retrieve_commodity_price(request,variety_id):
    try:
        variety = get_object_or_404(Variety,pk=variety_id)
        commodity_price = CommodityPrice.objects.filter(variety_id=variety_id)
        # commodity_price_paginator = Paginator(commodity_price_obj, 10)
        # commodity_price_page_number = request.GET.get('page')
        # commodity_price = commodity_price_paginator.get_page(commodity_price_page_number)
        return render(request,"commodity_price.html",{'variety':variety,"commodity_price":commodity_price})
    except Exception as e:
        print(e)
        return response_helper.server_error_response()

def create_commodity_price(request):
    if request.method == "POST":
        return HttpResponse(json.dumps({"message": "method is not allowed"}), status=405)
    try:
        m = insert_commodity_price_data()
        commodity_price_data = serializers.serialize('json', CommodityPrice.objects.all())
        return response_helper.create_success_response("okay", commodity_price_data)
    except Exception as e:
        print(e)
        return response_helper.server_error_response()


def retrieve_weather(request,market_id):
    try:
        market = get_object_or_404(Market, pk=market_id)
        market_name = market.market_name
        data = YahooWeather(APP_ID="xg9emu6o",
                            api_key="dj0yJmk9R0EwRVIxMFVoV25KJmQ9WVdrOWVHYzVaVzExTm04bWNHbzlNQS0tJnM9Y29uc3VtZXJzZWNyZXQmc3Y9MCZ4PWI2",
                            api_secret="35b08b1e830b532f2d497d06b7074eda066cae4d")
        data.get_yahoo_weather_by_city(market_name, Unit.celsius)
        text = data.condition.text
        tempreture = data.condition.temperature
        sunrise = data.astronomy.sunrise
        sunset = data.astronomy.sunset
        humadity = data.atmosphere.humidity
        pressure = data.atmosphere.pressure
        visibility = data.atmosphere.visibility
        speed = data.wind.speed
        direction = data.wind.direction
        lat = data.location.lat
        log = data.location.long

        return render(request, "weather.html", {"market": market,'text': text,
                                              'tempreture': tempreture, 'sunrise': sunrise, 'sunset': sunset,
                                              'humadity': humadity, 'pressure': pressure, 'visibility': visibility,
                                              'speed': speed, 'direction': direction,'lat':lat,'log':log})
    except Exception as e:
        print(e)
        return response_helper.server_error_response()

def delete_old():
    seven_days_ago = datetime.now() - timedelta(days=7)
    CommodityPrice.objects.filter(arrival_date__lt=seven_days_ago)

def seed_dealers(request):
    return render(request,"seed_dealers.html")


def compare_by_market(request,variety_name,market_name,commodity_name):
    try:
        market = Market.objects.filter(
            district__id__in = Market.objects.filter(market_name=market_name).values_list('district',flat=True))
        commodity = Commodity.objects.filter(commodity_name=commodity_name,market__id__in=market)
        variety = Variety.objects.filter(variety_name=variety_name,commodity__id__in=commodity)
        commodity_price_graph = CommodityPrice.objects.filter(variety__id__in=variety).values()
        commodity_price = CommodityPrice.objects.filter(variety__id__in=variety)

        df = pd.DataFrame([commodity_price_graph for commodity_price_graph in commodity_price_graph])

        arrival_date = list(arrival_date.strftime('%Y %m %d') for arrival_date in df['arrival_date'])
        base_date = datetime.today().date().strftime('%Y %m %d')
        date = max(arrival_date for arrival_date in arrival_date if arrival_date <= base_date)
        my_date = datetime.strptime(date,'%Y %m %d').date()

        da = df[(df['arrival_date'] == my_date )]
        da = da.reset_index()

        list_market_name = []
        list_commodity_name = []
        list_variety_name = []

        for index in range((da['market_id'].shape)[0]):
            market_obj = Market.objects.get(pk=da['market_id'][index])
            commodity_obj = Commodity.objects.get(pk=da['commodity_id'][index])
            variety_obj = Variety.objects.get(pk=da['variety_id'][index])

            list_market_name.append(str(market_obj.market_name))
            list_commodity_name.append(str(commodity_obj.commodity_name))
            list_variety_name.append(str(variety_obj.variety_name))


        da.loc[0:int((da['market_id'].shape)[0]),'market_id'] = list_market_name
        da.loc[0:int((da['commodity_id'].shape)[0]),'commodity_id'] = list_commodity_name
        da.loc[0:int((da['variety_id'].shape)[0]), 'variety_id'] = list_variety_name


        da = da.drop(columns=['id','district_id','state_id','timestamp'])

        da = da.rename(columns={'arrival_date':'Arrival Date','variety_id':'Variety Name','commodity_id':'Commodity Name',
                                'market_id':'Market Name','min_price':'Min Price','max_price':'Max Price','modal_price':'Modal Price'
                                })
        da = da[['Arrival Date','Market Name','Commodity Name','Variety Name','Min Price','Modal Price','Max Price']]

        def serve_layout():
            return html.Div([
                dash_table.DataTable(
                    id='table',
                    columns=[{"name": i, "id": i} for i in da.columns],
                    data=da.to_dict('records'),
                ),
                dcc.Graph(
                    id="graph-1",
                    figure=dict(
                        data=[
                            dict(

                                x=da['Market Name'],
                                y=da['Max Price'],
                                name='max price',
                                type='bar',
                                marker=dict(
                                    color='rgb(55, 83, 109)'
                                )
                            ),
                            dict(
                                x=da['Market Name'],
                                y=da['Min Price'],
                                name='min price',
                                type='bar',
                                marker=dict(
                                    color='rgb(255, 150, 100)'
                                )
                            ),
                            dict(
                                x=da['Market Name'],
                                y=da['Modal Price'],
                                name='modal price',
                                type='bar',
                                marker=dict(
                                    color='rgb(120, 50, 25)'
                                )
                            )
                        ],
                        layout=dict(
                            title='market vs price',
                            xaxis=dict(
                                title='market name',
                            ),
                            yaxis=dict(
                                title='prices'
                            )
                        )
                    )
                )
            ])

        dash_app.app.layout = serve_layout

        return render(request,"compare_other.html",{'commodity_price':commodity_price})

    except Exception as e:
        print(e)
        return response_helper.server_error_response()


def compare_by_dates(request,variety_name,market_name,commodity_name):
    try:
        market = Market.objects.filter(market_name=market_name)
        commodity = Commodity.objects.filter(commodity_name=commodity_name, market__id__in=market)
        variety = Variety.objects.filter(variety_name=variety_name, commodity__id__in=commodity)
        commodity_price_graph = CommodityPrice.objects.filter(variety__id__in=variety).values()
        commodity_price = CommodityPrice.objects.filter(variety__id__in=variety)

        df = pd.DataFrame([commodity_price_graph for commodity_price_graph in commodity_price_graph])

        list_market_name = []
        list_commodity_name = []
        list_variety_name = []

        for index in range((df['market_id'].shape)[0]):
            market_obj = Market.objects.get(pk=df['market_id'][index])
            commodity_obj = Commodity.objects.get(pk=df['commodity_id'][index])
            variety_obj = Variety.objects.get(pk=df['variety_id'][index])

            list_market_name.append(str(market_obj.market_name))
            list_commodity_name.append(str(commodity_obj.commodity_name))
            list_variety_name.append(str(variety_obj.variety_name))


        df.loc[0:int((df['market_id'].shape)[0]), 'market_id'] = list_market_name
        df.loc[0:int((df['commodity_id'].shape)[0]), 'commodity_id'] = list_commodity_name
        df.loc[0:int((df['variety_id'].shape)[0]), 'variety_id'] = list_variety_name

        df = df.drop(columns=['id','district_id','state_id','timestamp'])
        df = df.rename(
            columns={'arrival_date': 'Arrival Date', 'variety_id': 'Variety Name', 'commodity_id': 'Commodity Name',
                     'market_id': 'Market Name', 'min_price': 'Min Price', 'max_price': 'Max Price',
                     'modal_price': 'Modal Price'
                     })
        df = df[['Arrival Date', 'Market Name', 'Commodity Name', 'Variety Name', 'Min Price', 'Modal Price', 'Max Price']]


        def serve_layout():
            return html.Div([
                dash_table.DataTable(
                    id='table',
                    columns=[{"name": i, "id": i} for i in df.columns],
                    data=df.to_dict('records'),
                ),
                dcc.Graph(
                    id="graph-1",
                    figure=dict(
                        data=[
                            dict(

                                x=df['Arrival Date'],
                                y=df['Max Price'],
                                name='max price',
                                type='line',
                                marker=dict(
                                    color='rgb(55, 83, 109)'
                                )
                            ),
                            dict(
                                x=df['Arrival Date'],
                                y=df['Min Price'],
                                name='min price',
                                type='line',
                                marker=dict(
                                    color='rgb(255, 150, 100)'
                                )
                            ),
                            dict(
                                x=df['Arrival Date'],
                                y=df['Modal Price'],
                                name='modal price',
                                type='line',
                                marker=dict(
                                    color='rgb(120, 50, 25)'
                                )
                            )
                        ],
                        layout=dict(
                            title='arrival date vs price',
                            xaxis=dict(
                                title='arrival date',
                                tickformat='%Y %m %d',
                                tickmode='linear'
                            ),
                            yaxis=dict(
                                title='prices'
                            ),
                        )
                    )
                )
            ])

        dash_app.app.layout = serve_layout
        return render(request,"kmapp/compare.html",{'commodity_price':commodity_price})

    except Exception as e:
        print(e)
        return response_helper.server_error_response()
