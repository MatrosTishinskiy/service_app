from django.core.validators import MaxValueValidator
from django.db import models, transaction
from django.db.models import F

from clients.models import Client
from services.tasks import set_price





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
                lambda: [set_price.delay(subscription.id)
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
                lambda: [set_price.delay(subscription.id)
                         for subscription in self.subscriptions.all()])






class Subscription(models.Model):
    client = models.ForeignKey(to=Client, related_name='subscriptions', on_delete=models.PROTECT)
    service = models.ForeignKey(to=Service, related_name='subscriptions', on_delete=models.PROTECT)
    plan = models.ForeignKey(to=Plan, related_name='subscriptions', on_delete=models.PROTECT)
    price = models.PositiveIntegerField(default=0)


    def save(self, *args, **kwargs):
        if not self.pk:
            start_price = (self.service.full_price -
                           self.service.full_price *
                           self.plan.discount_percent / 100)

            self.price = start_price
        super().save(*args, **kwargs)



