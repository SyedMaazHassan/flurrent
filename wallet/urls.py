from django.urls import path
from django.conf import settings
from .views import *
from django.conf.urls.static import static
from django.contrib.auth.decorators import login_required


app_name = 'wallet'

urlpatterns = [
    # path('', index, name='index'),
    # path('wallet',  login_required(WalletList.as_view()), name='index'),
    # path('wallet/topup',  wallet_topup, name='topup'),
    # path('creators/<slug>',  CreatorDetail.as_view(), name='single-creator'),
    # path('creators/<slug>/subscribe',  subscribeCreator, name='subscribe-creator')
    path('wallet/earnings', earnings_view, name="earnings")
] 

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
