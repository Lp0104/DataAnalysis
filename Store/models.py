from django.db import models


# Create your models here.
class StoreInfo(models.Model):
    objects = models.Manager()
    Storeid = models.CharField(max_length=20, primary_key=True)
    Storetitle = models.CharField(max_length=100)
    Storeaddress = models.CharField(max_length=100)
    Storesailed = models.IntegerField()
    Sturerevenue = models.DecimalField(max_digits=11, decimal_places=3, blank=True, null=True)

    class Meta:
        managed = True
        db_table = 'Store'


class GoodsInfo(models.Model):
    object = models.Manager()
    Goodsid = models.CharField(max_length=20)
    Storeid = models.CharField(max_length=20)
    Goodstitle = models.CharField(max_length=100)
    Goodsprice = models.FloatField()
    Goodssailed = models.IntegerField()
    Goodsrevenue = models.DecimalField(max_digits=11, decimal_places=3)

    class Meta:
        managed = True
        db_table = 'Goods'


class ConsumptionInfo(models.Model):
    object = models.Manager()
    Goodsid = models.CharField(max_length=20)
    Storeid = models.CharField(max_length=20)
    Guest = models.CharField(max_length=20)
    Quantity = models.IntegerField()
    Time = models.DateField()
    Goodsprice = models.FloatField(blank=True, null=True)

    class Meta:
        managed = True
        db_table = 'Consumption'


class StoreHistoricalMonth(models.Model):
    objects = models.Manager()
    Storeid = models.CharField(max_length=20)
    Storetitle = models.CharField(max_length=100)
    Storesailed = models.IntegerField()
    Sturerevenue = models.DecimalField(max_digits=11, decimal_places=3, blank=True, null=True)
    Time = models.DateField()

    class Meta:
        managed = True
        db_table = 'StoreHistoricalMonth'


class GoodsStoreHistoricalMonth(models.Model):
    object = models.Manager()
    Goodsid = models.CharField(max_length=20)
    Storeid = models.CharField(max_length=20)
    Goodstitle = models.CharField(max_length=100)
    Goodssailed = models.IntegerField()
    Goodsrevenue = models.DecimalField(max_digits=11, decimal_places=3)
    Time = models.DateField()

    class Meta:
        managed = True
        db_table = 'GoodsStoreHistoricalMonth'
