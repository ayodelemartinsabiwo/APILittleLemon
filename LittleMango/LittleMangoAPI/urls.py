from django.urls import path
from . import views

urlpatterns = [
    #path('menu-items/', views.menu_items),
    #path('categorys/', views.category_dtls, name='category-dtls'),
    path('categorys/', views.CategoryView.as_view()),
    path('menu-items/<int:pk>/', views.MenuItemsView.as_view(), name='menu-item-details'),
    path('menu-items/', views.MenuItemsListView.as_view(), name='menu-items-list'),
    path('groups/manager/users', views.manager),
    path('groups/manager/users/<int:pk>', views.manager_single),
    path('groups/delivery-crew/users/', views.DeliveryCrewView.as_view()),
    path('groups/delivery-crew/users/<int:pk>/', views.DeliveryCrewView.as_view()),
    path('cart/menu-items/', views.CartView.as_view()),
    path('orders/', views.OrderListView.as_view(), name= 'order-items-list'),
    path('orders/<int:pk>/', views.OrderDetailView.as_view(), name= 'order-items-details'),


    #path('groups/delivery-crew/users', views.delivery_crews),
]
