from django.urls import path
from . import views

urlpatterns = [
    path('categories', views.CategoryListCreate.as_view()),
    path('categories/<int:pk>', views.CategorySingle.as_view()),
    path('menu-items', views.MenuItemsList.as_view()),
    path('menu-items/<int:pk>', views.MenuItemSingle.as_view()),
    path('groups/manager/users', views.manager_list_add),
    path('groups/manager/users/<int:pk>', views.manager_execlude),
    path('groups/delivery-crew/users', views.delivery_crew_list_add),
    path('groups/delivery-crew/users/<int:pk>', views.delivery_execlude),
    path('cart/menu-items', views.cart_end_point),
    path('orders', views.orders_endpoint),
    path('orders/<int:order_id>', views.order_endpoint),
]