from .views import *
from django.urls import path

# router = DefaultRouter()

# router.register(r'tables', TableViewSet)
urlpatterns = [
    path('',OrderView.as_view()),
    path('tableView/',FetchTables.as_view()),
    path('table/',TableOrderView.as_view()),
    path('delivery/',DeliveryOrder.as_view()),
    path('cooked/',MarkOrderCooked.as_view()),
    # path('t/', include(router.urls)),
]
