import random
import time

from django.forms import model_to_dict
import requests
import json
import threading
import logging
from django.shortcuts import HttpResponse, render
from pyecharts.globals import ThemeType
import datetime
from Store.models import StoreInfo, GoodsInfo, ConsumptionInfo, StoreHistoricalMonth, GoodsStoreHistoricalMonth
from Empty import Result
from faker import Faker
import numpy as np
import pandas as pd
from pyecharts.charts import Bar, Line, Pie
from pyecharts import options as opts
from bs4 import BeautifulSoup

given_date = datetime.datetime.today().date()
# 用 1 代替日期中的 天
first_day_of_month = given_date.replace(day=1)
# 创建logger对象
print(first_day_of_month)
Flag = True
faker = Faker(locale="zh_CN")
phones = []
for i in range(0, 30):
    phones.append(faker.phone_number())


# 初始化
def Init(request):
    '''print('从服务器更新数据')
    GetData(request)
    print('更新完成')
    print('模拟个人消费')
    SimulationData(request)
    print('完成')
    print('计算营业额')
    TotalTurnover(request)
    print('完成')
    print('模拟其他月份信息')
    HistoricalMonth(request)
    print('完成')
    print('模拟销量')
    GetSalesVolume(request)
    print('完成')
    print('将商品同步到历史表')
    SynchronousStore(request)
    print('完成')'''
    time.sleep(3)
    return render(request, 'index.html',{
        'state':['none','a'],
        'host': Result.Result.host,
    })


# 将商品同步到历史表
def SynchronousStore(request):
    threds = []
    store = StoreInfo.objects.all()
    for i in store:
        threds.append(threading.Thread(target=SynchronousStoreThred, args=(i.Storeid,)))
    for i in threds:
        i.start()
    for i in threds:
        i.join()


# 将商品同步到数据多线程
def SynchronousStoreThred(sid):
    g = GoodsInfo.object.filter(Storeid=sid).all()
    for i in g:
        g = GoodsStoreHistoricalMonth.object.filter(Storeid=i.Storeid, Time=first_day_of_month).all()
        if g.count() == 0:
            GoodsStoreHistoricalMonth.object.create(Storeid=i.Storeid, Goodstitle=i.Goodstitle, Goodsid=i.Goodsid,
                                                    Goodssailed=i.Goodssailed, Goodsrevenue=i.Goodsrevenue,
                                                    Time=first_day_of_month)
        else:
            GoodsStoreHistoricalMonth.object.filter(Storeid=i.Storeid, Time=first_day_of_month, Goodstitle=i.Goodstitle
                                                    , Goodsid=i.Goodsid).update(Goodssailed=i.Goodssailed,
                                                                                Goodsrevenue=i.Goodsrevenue)


# 向数据库添加商品
def getData(sid, url, head, logger):
    params = {
        'i': 11,
        'v': '6.0.5',
        'm': 'we7_wmall',
        'c': 'entry',
        'do': 'mobile',
        'ctrl': 'wmall',
        'ac': 'store',
        'op': 'goods',
        'ta': 'index',
        'lv': 'v6',
        'device': 'wxapp',
        'from': 'wxapp',
        'u': 'wxapp',
        'state': 'we7sid-72f94edc96c8650489a3ede3a06cbf63',
        'useTest': 0,
        'scene': 1001,
        'sid': sid,
        'cid': 0,
        'psize': 1000
    }
    ret = requests.get(url=url, headers=head, params=params)
    data = json.loads(ret.text)
    try:
        storess = data['message']['message']['cate_has_goods']
        for i in storess:
            goods = storess[i]['goods']
            for j in goods:
                g = GoodsInfo.object.filter(Storeid=str(sid), Goodsid=str(goods[j]['cid']),
                                            Goodstitle=str(goods[j]['title']))
                if g.count() == 0:
                    GoodsInfo.object.create(Storeid=str(sid), Goodsid=str(goods[j]['cid']),
                                            Goodstitle=str(goods[j]['title'])
                                            , Goodsprice=str(goods[j]['price']), Goodssailed=str(goods[j]['sailed']),
                                            Goodsrevenue=str(float(goods[j]['sailed']) * float(goods[j]['price'])))
                else:
                    GoodsInfo.object.filter(Storeid=str(sid), Goodsid=str(goods[j]['cid']),
                                            Goodstitle=str(goods[j]['title'])).update(Goodsprice=str(goods[j]['price']),
                                                                                      Goodssailed=str(
                                                                                          goods[j]['sailed']),
                                                                                      Goodsrevenue=str(float(
                                                                                          goods[j]['sailed']) * float(
                                                                                          goods[j]['price'])))
    except KeyError as e:
        goods = data['message']['message']['goods']
        for j in goods:
            g = GoodsInfo.object.filter(Storeid=str(sid), Goodsid=str(goods[j]['cid']),
                                        Goodstitle=str(goods[j]['title']))
            if g.count() == 0:
                GoodsInfo.object.create(Storeid=str(sid), Goodsid=str(goods[j]['cid']),
                                        Goodstitle=str(goods[j]['title'])
                                        , Goodsprice=str(goods[j]['price']), Goodssailed=str(goods[j]['sailed']),
                                        Goodsrevenue=str(float(goods[j]['sailed']) * float(goods[j]['price'])))
            else:
                GoodsInfo.object.filter(Storeid=str(sid), Goodsid=str(goods[j]['cid']),
                                        Goodstitle=str(goods[j]['title'])).update(Goodsprice=str(goods[j]['price']),
                                                                                  Goodssailed=str(
                                                                                      goods[j]['sailed']),
                                                                                  Goodsrevenue=str(float(
                                                                                      goods[j]['sailed']) * float(
                                                                                      goods[j]['price'])))


# 向数据库添加店铺
def GetData(request):
    if request.method == 'GET':

        logger = logging.getLogger('test_logger')

        # 设置日志等级
        logger.setLevel(logging.DEBUG)

        # 创建控制台
        KZT = logging.StreamHandler()

        # 设置控制台日志等级
        KZT.setLevel(logging.DEBUG)

        # 设置控制台输出的日志格式
        formatter = logging.Formatter('%(message)s')
        KZT.setFormatter(formatter)

        # 加载控制台实例到logger对象中
        logger.addHandler(KZT)

        url = 'https://admin.jiweike.cn/app/wxapp.php'
        pam = {
            'i': '11', 'm': 'we7_wmall',
            'c': 'entry',
            'do': 'mobile',
            'ctrl': 'wmall',
            'ac': 'home',
            'op': 'search',
            'ta': 'index',
            'lv': 'y6',
            'device': 'wxapp',
            'from': 'wxapp',
            'u': 'wxapp',
            'state': 'we7sid-72f94edc96c8650489a3ede3a06cbf63',
            'useTest': '0',
            'scene': '1001',
            'theme': 'blue',
            'ipreload': '1',
            'lat': '39.8918',
            'lng': '118.89294',
            'page': 1,
            'psize': 100,
            'child_id': '0'
        }
        head = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/53.0.2785.143 Safari/537.36 MicroMessenger/7.0.9.501 NetType/WIFI MiniProgramEnv/Windows WindowsWechat'
        }
        threads = []
        ret = requests.get(url=url, params=pam, headers=head)
        jsons = json.loads(ret.text)
        stores = jsons['message']['message']['stores']['stores']
        for v in stores:
            g = StoreInfo.objects.filter(Storeid=str(v['id']))
            if g.count() == 0:
                StoreInfo.objects.create(Storeid=str(v['id']), Storetitle=str(v['title']),
                                         Storeaddress=str(v['address']),
                                         Storesailed=v['sailed'])
                StoreHistoricalMonth.objects.create(Storeid=str(v['id']), Storetitle=str(v['title']),
                                                    Storesailed=v['sailed'],
                                                    Sturerevenue=0, Time=first_day_of_month)
                thread = threading.Thread(target=getData, args=(v['id'], url, head, logger))
                threads.append(thread)
            else:
                StoreInfo.objects.filter(Storeid=str(v['id'])).update(Storesailed=v['sailed'])
                thread = threading.Thread(target=getData, args=(v['id'], url, head, logger))
                threads.append(thread)

        for i in threads:
            i.start()
        for i in threads:
            i.join()
        return render(request, 'test.html')
    else:
        return HttpResponse(request.method)


def GetStoreListAll(request):
    head = {
        'accept': 'application/json'
    }
    if request.method == 'GET':
        jsonList = StoreInfo.objects.all()
        data = []
        for i in jsonList:
            data.append(model_to_dict(i))
        return HttpResponse(json.dumps(Result.Result.succ(data).toString()), headers=head)
    else:
        return HttpResponse(json.dumps(Result.Result.succ(1).toString()))


def index(request):

    return render(request, 'index.html', {
        'panel': 'none',
        'state': ['a', 'none'],
        'host': Result.Result.host,
    })


# 计算商店当前月份总营业额
def TotalTurnover(request):
    goods = StoreInfo.objects.all()
    threads = []
    for i in goods:
        threads.append(threading.Thread(target=TotalTurnoverTread, args=(i.Storeid,)))
    for i in threads:
        i.start()
    for i in threads:
        i.join()


# 计算商店当前月份总营业额
def TotalTurnoverTread(sid):
    ls = ConsumptionInfo.object.filter(Storeid=sid).values_list()
    df_obj = pd.DataFrame(ls)
    StoreInfo.objects.filter(Storeid=sid).update(Sturerevenue=format((df_obj[6] * df_obj[4]).sum(), '.3f'))
    StoreHistoricalMonth.objects.filter(Storeid=sid, Time=first_day_of_month).update(
        Sturerevenue=format((df_obj[6] * df_obj[4]).sum(), '.3f'))


# 模拟数据个人消费
def SimulationTread(sid, count):
    Goods = GoodsInfo.object.all().filter(Storeid=sid).values_list()
    flage = ConsumptionInfo.object.filter(Storeid=sid).all()
    if flage.count() == 0:
        sum = 0
    else:
        num = ConsumptionInfo.object.filter(Storeid=sid).values_list()
        df = pd.DataFrame(num)
        sum = df[4].sum()
    for i in range(int(sum), int(count) + 1):
        j = random.randint(1, 30)
        if int(i) + int(j) > int(count):
            i = i
        else:
            i = int(i) + int(j)
        s = random.sample(list(Goods), 1)[0]
        ConsumptionInfo.object.create(Goodsid=s[1], Storeid=sid,
                                      Guest=random.sample(list(phones), 6)[random.randint(0, 5)],
                                      Quantity=j,
                                      Goodsprice=s[4],
                                      Time=faker.date_time_this_month(before_now=True, after_now=False, tzinfo=None))


# 模拟数据个人消费
def SimulationData(request):
    Store = StoreInfo.objects.all()
    threadings = []
    for id in Store:
        threadings.append(threading.Thread(target=SimulationTread, args=(id.Storeid, id.Storesailed,)))
    for i in threadings:
        i.start()
    for i in threadings:
        i.join()
    return HttpResponse(request)


# 模拟其他月份信息
def HistoricalMonth(requrst):
    dist = ['2022-4-1', '2022-5-1', '2022-6-1', '2022-7-1', '2022-8-1', '2022-9-1']
    store = StoreInfo.objects.all()
    threads = []
    for item in dist:
        for i in store:
            threads.append(threading.Thread(target=HistoricalMonthThredGoods, args=(i, item,)))
    for i in threads:
        i.start()
    for i in threads:
        i.join()


# 模拟其他月份信息
def HistoricalMonthThredGoods(i, item):
    goods = GoodsInfo.object.filter(Storeid=i.Storeid).all()
    if StoreHistoricalMonth.objects.filter(Storeid=i.Storeid, Time=item).all().count() == 0:
        StoreHistoricalMonth.objects.create(Storeid=i.Storeid, Storetitle=i.Storetitle, Storesailed=i.Storesailed,
                                            Sturerevenue=i.Sturerevenue, Time=item)
    for v in goods:
        num = random.randint(0, 3000)
        if GoodsStoreHistoricalMonth.object.filter(Storeid=v.Storeid, Goodstitle=v.Goodstitle,
                                                   Time=item).all().count() == 0:
            GoodsStoreHistoricalMonth.object.create(Storeid=v.Storeid, Goodstitle=v.Goodstitle, Goodsid=v.Goodsid,
                                                    Goodssailed=num, Goodsrevenue=int(num) * v.Goodsprice,
                                                    Time=item)
    goods = GoodsStoreHistoricalMonth.object.filter(Time=item).values_list()


# 模拟其他月份信息
# 获取销量
def GetSalesVolume(request):
    store = StoreInfo.objects.all()
    dist = ['2022-4-1', '2022-5-1', '2022-6-1', '2022-7-1', '2022-8-1', '2022-9-1']
    for i in store:
        for j in dist:
            stores = GoodsStoreHistoricalMonth.object.filter(Storeid=i.Storeid, Time=j).values_list()
            df = pd.DataFrame(stores)
            StoreHistoricalMonth.objects.filter(Storeid=i.Storeid, Time=j).update(Storesailed=df[4].sum(),
                                                                                  Sturerevenue=df[5].sum())


# 店铺数据
# 店铺月销量排行
def MonthlySalesRank(request):
    # 常见DataFrame对象，指定列索引
    ls = StoreInfo.objects.all().order_by('-Storesailed')[:10].values_list()
    df_obj = pd.DataFrame(ls)
    # 通过列索引的方式获取一列数据
    bar = (
        Bar(init_opts=opts.InitOpts(width="1700px",
                                    height="750px",theme=ThemeType.LIGHT))
        .add_xaxis(df_obj[1].tolist())
        .add_yaxis("商品月销量（份）", df_obj[3].tolist())
        .set_global_opts(title_opts=opts.TitleOpts(title="店铺月销量排行", subtitle="仅采用本月销量仅展示前十名"))
    )
    html_embed = bar.render_embed()
    soup = BeautifulSoup(html_embed, 'lxml')
    my_pic = "\n".join([str(i).strip() for i in soup.body.contents])  # soup.body.contents是一个列表，把列表转为字符串
    print(df_obj[1].tolist())
    return render(request, 'test.html', {
        "my_pic": my_pic,
        'panel': 'none',
        'search': 'none',
        'state': ['mdui-collapse-item-open','',''],
        'host': Result.Result.host,
    })


# 店铺月营业额排行
def MonthlyTurnoverRank(request):
    ls = StoreInfo.objects.all().order_by('-Sturerevenue')[:10].values_list()
    df_obj = pd.DataFrame(ls)
    # 通过列索引的方式获取一列数据
    bar = (
        Bar(init_opts=opts.InitOpts(width="1700px",
                                    height="750px",theme=ThemeType.LIGHT))
        .add_xaxis(df_obj[1].tolist())
        .add_yaxis("店铺月营业额（元）", df_obj[4].tolist())
        .set_global_opts(title_opts=opts.TitleOpts(title="店铺月营业额排行", subtitle="仅采用本月营业额仅展示前十名"))
    )
    html_embed = bar.render_embed()
    soup = BeautifulSoup(html_embed, 'lxml')
    my_pic = "\n".join([str(i).strip() for i in soup.body.contents])  # soup.body.contents是一个列表，把列表转为字符串
    print(df_obj[1].tolist())
    return render(request, 'test.html', {
        "my_pic": my_pic,
        'panel': 'none',
        'search': 'none',
        'state': ['mdui-collapse-item-open', '', ''],
        'host': Result.Result.host,
    })


# 最受欢迎店铺
def MostPopularStore(request):
    num = []
    s = StoreInfo.objects.all()
    for i in s:
        ls = StoreHistoricalMonth.objects.filter(Storeid=i.Storeid).values_list()
        df_obj = pd.DataFrame(ls)
        num.append([df_obj[2][0], df_obj[3].sum()])
    df = pd.DataFrame(list(num))
    df = df.sort_values(by=1, ascending=False)[:10]
    print(df)
    # 通过列索引的方式获取一列数据
    bar = (
        Bar(init_opts=opts.InitOpts(width="1700px",
                                    height="750px",theme=ThemeType.LIGHT))
        .add_xaxis(df[0].tolist())
        .add_yaxis("最受欢迎店铺（份）", df[1].tolist())
        .set_global_opts(title_opts=opts.TitleOpts(title="最受欢迎店铺", subtitle="仅采用总销量排名仅展示前十名"))
    )
    html_embed = bar.render_embed()
    soup = BeautifulSoup(html_embed, 'lxml')
    my_pic = "\n".join([str(i).strip() for i in soup.body.contents])  # soup.body.contents是一个列表，把列表转为字符串
    print(df_obj[1].tolist())
    return render(request, 'test.html', {
        "my_pic": my_pic,
        'panel': 'none',
        'search': 'none',
        'state': ['mdui-collapse-item-open', '', ''],
        'host': Result.Result.host,
    })


# 店铺总营业额排行
def TotalTurnoverAll(request):
    num = []
    s = StoreInfo.objects.all()
    for i in s:
        if i.Storetitle != '测试店铺（请勿下单）':
            ls = StoreHistoricalMonth.objects.filter(Storeid=i.Storeid).values_list()
            df_obj = pd.DataFrame(ls)
            num.append([df_obj[2][0], df_obj[4].sum()])
    df = pd.DataFrame(list(num))
    df = df.sort_values(by=1, ascending=False)[:10]
    print(df)
    # 通过列索引的方式获取一列数据
    bar = (
        Bar(init_opts=opts.InitOpts(width="1700px",
                                    height="750px",theme=ThemeType.LIGHT))
        .add_xaxis(df[0].tolist())
        .add_yaxis("店铺总营业额排行（元）", df[1].tolist())
        .set_global_opts(title_opts=opts.TitleOpts(title="店铺总营业额排行", subtitle="仅采用总营业额排名仅展示前十名"))
    )
    html_embed = bar.render_embed()
    soup = BeautifulSoup(html_embed, 'lxml')
    my_pic = "\n".join([str(i).strip() for i in soup.body.contents])  # soup.body.contents是一个列表
    print(df_obj[1].tolist())
    return render(request, 'test.html', {
        "my_pic": my_pic,
        'panel': 'none',
        'search': 'none',
        'state': ['mdui-collapse-item-open', '', ''],
        'host': Result.Result.host,
    })


# 商品数据
# 商品月销量排行
def CommodityRank(request):
    ls = GoodsInfo.object.all().order_by('-Goodssailed')[:10].values_list()
    df_obj = pd.DataFrame(ls)
    print(df_obj)
    # 通过列索引的方式获取一列数据
    bar = (
        Bar(init_opts=opts.InitOpts(width="1700px",
                                    height="750px",theme=ThemeType.LIGHT))
        .add_xaxis(df_obj[3].tolist())
        .add_yaxis("商品月销量排行（份）", df_obj[5].tolist())
        .set_global_opts(title_opts=opts.TitleOpts(title="商品月销量排行", subtitle="仅采用本月销售量仅展示前十名"))
    )
    html_embed = bar.render_embed()
    soup = BeautifulSoup(html_embed, 'lxml')
    my_pic = "\n".join([str(i).strip() for i in soup.body.contents])  # soup.body.contents是一个列表，把列表转为字符串
    print(df_obj[1].tolist())
    return render(request, 'test.html', {
        "my_pic": my_pic,
        'panel': 'none',
        'search': 'none',
        'state': ['', 'mdui-collapse-item-open', ''],
        'host': Result.Result.host,
    })


# 月营业额排行
def GoodsMonthlyTurnoverRank(request):
    ls = GoodsInfo.object.all().order_by('-Goodsrevenue')[:10].values_list()
    df_obj = pd.DataFrame(ls)
    print(df_obj)
    # 通过列索引的方式获取一列数据
    bar = (
        Bar(init_opts=opts.InitOpts(width="1700px",
                                    height="750px",theme=ThemeType.LIGHT))
        .add_xaxis(df_obj[3].tolist())
        .add_yaxis("商品月销量排行（份）", df_obj[6].tolist())
        .set_global_opts(title_opts=opts.TitleOpts(title="商品月销量排行", subtitle="仅采用本月销售量仅展示前十名"))
    )
    html_embed = bar.render_embed()
    soup = BeautifulSoup(html_embed, 'lxml')
    my_pic = "\n".join([str(i).strip() for i in soup.body.contents])  # soup.body.contents是一个列表，把列表转为字符串
    print(df_obj[1].tolist())
    return render(request, 'test.html', {
        'Storenames': [my_pic],
        'my_pic': my_pic,
        'panel': 'none',
        'search': 'none',
        'state': ['', 'mdui-collapse-item-open', ''],
        'host': Result.Result.host,
    })


# 商品月销量
def GoodsMonthlyTurnover(request):
    my_pic = Line(init_opts=opts.InitOpts(width="1700px",
                                          height="750px",theme=ThemeType.LIGHT))
    Goods = []
    name = request.GET.get('name')
    Storenames = StoreInfo.objects.all()
    if name == None:
        return render(request, 'test.html', {
            'Storenames': [Storenames],
            'state': ['', 'mdui-collapse-item-open', ''],
            'search': 'none',
            'host': Result.Result.host,
        })
    else:
        i = StoreInfo.objects.filter(Storetitle=name).all()
        id = i[0].Storeid
        gid = GoodsInfo.object.filter(Storeid=id).all()
        for i in gid:
            goods = GoodsStoreHistoricalMonth.object.filter(Storeid=id, Goodstitle=i.Goodstitle).order_by('-Goodstitle',
                                                                                                          'Time').values_list()
            Goods.append(pd.DataFrame(goods))

        print(Goods[0])
        my_pic.add_xaxis(Goods[0][6].tolist())
        for v in Goods:
            my_pic.add_yaxis(series_name=v[3][0], y_axis=v[4].tolist(), is_selected=False)
        my_pic.set_global_opts(title_opts=opts.TitleOpts(title="Line-多折线重叠"))
        html_embed = my_pic.render_embed()
        soup = BeautifulSoup(html_embed, 'lxml')
        my_pic = "\n".join([str(i).strip() for i in soup.body.contents])  # soup.body.contents是一个列表，把列表转为字符串
        return render(request, 'test.html', {
            'Storenames': [Storenames],
            'my_pic': my_pic,
            'panel': 'True',
            'search': 'none',
            'state': ['', 'mdui-collapse-item-open', ''],
            'host': Result.Result.host,
        })


# 个人消费分析
def PersonalAnalysis(request):
    my_pic = Line(init_opts=opts.InitOpts(width="1700px",
                                          height="750px",theme=ThemeType.LIGHT))
    Goods = []
    phone = request.GET.get('phone')
    print(phone)
    Storenames = StoreInfo.objects.all()
    if phone == None:
        return render(request, 'test.html', {
            'Storenames': [Storenames],
            'panel': 'none',
            'state': ['', '', 'mdui-collapse-item-open'],
            'host': Result.Result.host,
        })
    else:
        i = ConsumptionInfo.object.filter(Guest=phone).all().values_list()
        if i.count()==0:
            return render(request, 'test.html', {
                'Storenames': [Storenames],
                'panel': 'none',
                'state': ['', '', 'mdui-collapse-item-open'],
                'host': Result.Result.host,
            })
        df = pd.DataFrame(i)
        df5 = df.sort_values(by=5, ascending=True)
        time = first_day_of_month
        da5_times = []
        for i in range(1, 99):
            df5_time = df5[(df5[5] == time)]
            da5_times.append([df5_time[4].sum(), str(time)])
            time = time + datetime.timedelta(days=i)
            if time > datetime.date.today():
                break
        df_obj = pd.DataFrame(da5_times)
        bar = (
            Bar(init_opts=opts.InitOpts(width="600px",
                                        height="450px",theme=ThemeType.LIGHT))
            .add_xaxis(df_obj[1].tolist())
            .add_yaxis("外卖消费情况（份）", df_obj[0].tolist())
            .set_global_opts(title_opts=opts.TitleOpts(title="外卖消费情况", subtitle="仅采用本月数据"))
        )
        html_embed = bar.render_embed()
        soup = BeautifulSoup(html_embed, 'lxml')
        StoreId = df[2].tolist()
        StoreId = list(set(StoreId))
        df4_Stores = []
        StoreTitles = []
        for i in StoreId:
            df4_Store = df[(df[2] == i)]
            df4_Stores.append([df4_Store[4].sum(), i])
        df_store = pd.DataFrame(df4_Stores).sort_values(by=0, ascending=False)[:6]
        print(df_store)
        for i in df_store[1].tolist():
            s = StoreInfo.objects.filter(Storeid=i).all()
            StoreTitles.append(s[0].Storetitle)
        print(StoreTitles)
        my_pic = "\n".join([str(i).strip() for i in soup.body.contents])  # soup.body.contents是一个列表，把列表转为字符串
        c = (
            Pie()
            .add("", [list(z) for z in zip(StoreTitles, df_store[0].tolist())])
            # 这里设定颜色，当然了，看你有多少种。
            .set_colors(["blue", "green", "yellow", "red", "pink", "orange", "purple"])
            .set_global_opts(title_opts=opts.TitleOpts(title="店铺偏好"))
            .set_series_opts(label_opts=opts.LabelOpts(formatter="{b}: {c}"))
        )
        html_embed = c.render_embed()
        soup = BeautifulSoup(html_embed, 'lxml')
        my_pic2 = "\n".join([str(i).strip() for i in soup.body.contents])  # soup.body.contents是一个列表，把列表转为字符串
        return render(request, 'test.html', {
            'Storenames': [my_pic],
            'my_pic': my_pic,
            'my_pic2': my_pic2,
            'panel': 'none',
            'search': 'aaa',
            'state':['','','mdui-collapse-item-open'],
            'host':Result.Result.host,
        })
