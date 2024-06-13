from django.core.validators import MaxValueValidator
from django.db import models

from clients.models import Client


class Service(models.Model):
    name = models.CharField(max_length=50)
    full_price = models.PositiveSmallIntegerField()




class Plan(models.Model):
    PLAN_TYPES = (
        ('full', 'Full'),
        ('student', 'Student'),
        ('discount', 'Discount'),
    )

    plan_type = models.CharField(choices=PLAN_TYPES, max_length=10)
    discount_percent = models.PositiveSmallIntegerField(default=0,
                                                        validators=[
                                                            MaxValueValidator(100)
                                                        ])


class Subscription(models.Model):
    client = models.ForeignKey(to=Client, related_name='subscriptions', on_delete=models.PROTECT)
    service = models.ForeignKey(to=Service, related_name='subscriptions', on_delete=models.PROTECT)
    plan = models.ForeignKey(to=Plan, related_name='subscriptions', on_delete=models.PROTECT)


