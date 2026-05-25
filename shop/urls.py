from django.urls import path
from . import views

app_name = 'shop'

urlpatterns = [
    path('', views.HomeView.as_view(), name='home'),
    path('about/', views.AboutView.as_view(), name='about'),
    path('search/', views.SearchView.as_view(), name='search'),
    path('cart/', views.CartView.as_view(), name='cart'),
    path('cart/add/<int:product_id>/', views.add_to_cart, name='add_to_cart'),
    path('cart/remove/<int:item_id>/', views.remove_from_cart, name='remove_from_cart'),
    path('category/<slug:slug>/', views.CategoryView.as_view(), name='category'),
    path('product/<slug:slug>/', views.ProductDetailView.as_view(), name='product_detail'),
    path('product/<int:product_id>/review/', views.add_review, name='add_review'),
]
