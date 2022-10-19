"""DataAnalysis URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.1/topics/http/urls/
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
from django.contrib import admin
from django.urls import path
from Store.views import index, GetData, GetStoreListAll, SimulationData, MonthlySalesRank, MonthlyTurnoverRank, \
    MostPopularStore, TotalTurnoverAll,CommodityRank,GoodsMonthlyTurnoverRank,GoodsMonthlyTurnover,PersonalAnalysis,Init

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', index),
    path('Init/', Init),
    path('GetStoreListAll/', GetStoreListAll),
    path('SimulationData/', SimulationData),

    # 店铺数据
    path('MonthlySalesRank', MonthlySalesRank),
    path('MonthlyTurnoverRank', MonthlyTurnoverRank),
    path('MostPopularStore', MostPopularStore),
    path('TotalTurnoverAll', TotalTurnoverAll),

    # 商品数据
    path('CommodityRank',CommodityRank),
    path('GoodsMonthlyTurnoverRank',GoodsMonthlyTurnoverRank),
    path('GoodsMonthlyTurnover',GoodsMonthlyTurnover),

    #个人
    path('PersonalAnalysis',PersonalAnalysis)
]
