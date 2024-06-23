from django.core.validators import MaxValueValidator
from django.db import models, transaction
from django.core.cache import cache
from django.conf import settings
from django.db.models.signals import post_delete

import datetime


from clients.models import Client
from services.tasks import set_price, set_comment
from services.receivers import delete_cache_total_amount

class Service(models.Model):
    name = models.CharField(max_length=50)
    full_price = models.PositiveSmallIntegerField()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.old_full_price = self.full_price


    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        if self.old_full_price != self.full_price:
            transaction.on_commit(
                lambda: [(set_price.delay(subscription.id), set_comment.delay(subscription.id))
                         for subscription in self.subscriptions.all()])


class Plan(models.Model):
    PLAN_TYPES = (
        ('full', 'Full'),
        ('student', 'Student'),
        ('discount', 'Discount'),
    )

    plan_type = models.CharField(choices=PLAN_TYPES, max_length=10)
    discount_percent = models.PositiveIntegerField(default=0,
                                                   validators=[
                                                       MaxValueValidator(100)
                                                   ])

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.old_discount_percent = self.discount_percent


    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        if self.old_discount_percent != self.discount_percent:
            transaction.on_commit(
                lambda: [(set_price.delay(subscription.id), set_comment.delay(subscription.id))
                         for subscription in self.subscriptions.all()])


class Subscription(models.Model):
    client = models.ForeignKey(to=Client, related_name='subscriptions', on_delete=models.PROTECT)
    service = models.ForeignKey(to=Service, related_name='subscriptions', on_delete=models.PROTECT)
    plan = models.ForeignKey(to=Plan, related_name='subscriptions', on_delete=models.PROTECT)
    price = models.PositiveIntegerField(default=0)
    comment = models.CharField(max_length=50, default='')



    def save(self, *args, **kwargs):
        # create = not bool(self.id)
        # super().save(*args, **kwargs)
        #
        # if create:
        #     set_price.delay(self.id)


        if not self.pk:  ###Самопальный вариант. Не делает 2х лишних запросов в БД###
            start_price = (self.service.full_price -
                           self.service.full_price *
                           self.plan.discount_percent / 100)

            self.price = start_price
            self.comment = str(datetime.datetime.now())
            cache.delete(settings.PRICE_CACHE_NAME)
        super().save(*args, **kwargs)


post_delete.connect(delete_cache_total_amount, sender=Subscription)
