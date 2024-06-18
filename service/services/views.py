from django.db.models import Prefetch, F, Sum
from rest_framework.viewsets import ReadOnlyModelViewSet

from clients.models import Client
from services.models import Subscription
from services.serializers import SubscriptionSerializer


class SubscriptionView(ReadOnlyModelViewSet):
    ## Простая оптимизация запроса ( 3 запроса к БД + все поля моделей) ##

    # queryset = Subscription.objects.all().prefetch_related('client').prefetch_related('client__user')

    ## Оптимизация ( 2 запроса + только необходимые поля моделей ) ##

    queryset = Subscription.objects.all().prefetch_related(
        'plan',
        ##################################################################################################################
        ## 1й вариант при расчете цены в get_price SubscriptionSerializer  ##
        # 'service',
        ##################################################################################################################
        Prefetch('client',
                 queryset=Client.objects.all().select_related('user').only('company_name', 'user__email'))
    )#.annotate(price=F('service__full_price') -
     #                F('service__full_price') * F('plan__discount_percent') / 100.00)

    serializer_class = SubscriptionSerializer

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        response = super().list(request, *args, **kwargs)


        response_data = {'rezult': response.data}
        response_data['total_amount'] = queryset.aggregate(total=Sum('price')).get('total')
        response.data = response_data
        return response
