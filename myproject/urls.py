
from django.contrib import admin
from django.urls import path,include
from django.conf.urls.static import static
from django.conf import settings
from user import urls as user_urls
from order import urls as order_urls
from payment import urls as payment_urls

from products import urls as product_urls
urlpatterns = [
    path('admin/', admin.site.urls),
    path('user/',include(user_urls)),
    path('order/',include(order_urls)),
    path('payment/',include(payment_urls)),
    path('product/',include(product_urls))


]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
