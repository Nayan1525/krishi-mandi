"""krishimandi URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.urls import include, path
from myapp import views
from django.contrib import admin
from django.urls import path
from django.contrib.auth.views import LoginView, LogoutView
from django.conf import settings
from django.conf.urls.static import static
from . import dash_app

urlpatterns = [
    path('', views.index, name='index'),
    path('contactus/', views.contactus, name='contactus'),
    path('aboutus', views.aboutus, name='aboutus'),
    path("kmapp/",include('kmapp.urls')),
    path('profile/',views.profile,name='profile'),
    path('django_plotly_dash/', include('django_plotly_dash.urls')),
    path('admin/', admin.site.urls, name='admin'),
    # path('profile/', views.Profile, name='profile' ),
    # path('login/', LoginView.as_view(template_name='myapp/login.html'), name='login'),
    path('login/', views.login_request, name='login'),
    path('logout/', LogoutView.as_view(),name='logout'),
    # path('', include('classroom.urls')),
    # path('accounts/', include('django.contrib.auth.urls')),
    path('accounts/signup/', views.SignUpView, name='signup'),
    path('accounts/signup/farmer/', views.FarmerSignUpView, name='farmer_signup'),
    path('accounts/signup/dealer/', views.DealerSignUpView, name='dealer_signup'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)