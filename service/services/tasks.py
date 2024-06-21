import datetime
import time

from celery import shared_task
from django.db.models import F
from django.db import transaction
from celery_singleton import Singleton
from django.core.cache import cache
from django.conf import settings


'''
 Singleton не ставит в очередь таску, если уже есть таска со схожими 
 но не одинаковыми аргументами. 
'''


'''
 Простое решение для небольших тасок, позволяющее избежать перезаписи
 полей при паралельной работе нескольких воркеров!
 .save(update_fields=['изменяемое поле модели',])
'''

# @shared_task#(base=Singleton) если применять Singleton
# def set_price(subscription_id):
#
#     from services.models import Subscription
#
#     time.sleep(5)
#
#     subscription = Subscription.objects.filter(id=subscription_id).annotate(
#         annotated_price=F('service__full_price') -
#                         F('service__full_price') *
#                         F('plan__discount_percent') / 100.00).first()
#     time.sleep(3)
#
#     subscription.price = subscription.annotated_price
#     subscription.save(update_fields=['price'])
#
#
# @shared_task#(base=Singleton) если применять Singleton
# def set_comment(subscription_id):
#
#     from services.models import Subscription
#
#     subscription = Subscription.objects.get(id=subscription_id)
#
#     time.sleep(10)
#
#     subscription.comment = str(datetime.datetime.now())
#     subscription.save(update_fields=['comment'])


'''
Более сложное решение применимое для больших тасок 
with transaction.atomic(): - атомарная транзакция внутри которой
выполнится либо все либо ничего!
select_for_update() - работает только в transaction.atomic()
блокирует дотуп к обьекту в бд пока не выполнится коммит в бд

В этом варианте воркеры работают не паралельно!
Этот вариант скорее для примера 
'''


@shared_task#(base=Singleton) если применять Singleton (с тестами на 8ми подписках работает криво)
def set_price(subscription_id):

    from services.models import Subscription


    # time.sleep(5)

    with transaction.atomic():

        subscription = Subscription.objects.select_for_update().filter(id=subscription_id).annotate(
            annotated_price=F('service__full_price') -
                            F('service__full_price') *
                            F('plan__discount_percent') / 100.00).first()

        # time.sleep(3)

        subscription.price = subscription.annotated_price
        subscription.save()
    cache.delete(settings.PRICE_CACHE_NAME)

@shared_task#(base=Singleton) если применять Singleton (с тестами на 8ми подписках работает криво)
def set_comment(subscription_id):

    from services.models import Subscription

    with transaction.atomic():

        subscription = Subscription.objects.select_for_update().get(id=subscription_id)

        # time.sleep(10)

        subscription.comment = str(datetime.datetime.now())
        subscription.save()
    cache.delete(settings.PRICE_CACHE_NAME)


