import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'krishimandi.settings')
from django.conf import settings
from dash.dependencies import Output,Input,State
import dash_core_components as dcc
import dash_html_components as html
from django_plotly_dash import DjangoDash
import pandas as pd
from datetime import datetime as dt

app = DjangoDash('krishimandi',suppress_callback_exceptions=True)

