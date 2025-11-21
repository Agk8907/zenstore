from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name="home"),
    path('register/', views.registerPage, name="register"),
    path('login/', views.loginPage, name="login"),
    path('logout/', views.logoutUser, name="logout"),
    path('products/', views.products, name="products"),
    path('products/filter-data/', views.products_partial, name="products_partial"),
    path('product/<int:pk>/', views.product_detail, name="product_detail"),
    path('profile/', views.profile, name="profile"),
    path('wishlist/', views.wishlist_view, name="wishlist"),
    path('toggle_wishlist/', views.toggle_wishlist, name="toggle_wishlist"),
    path('cart/', views.cart, name="cart"),
    path('checkout/', views.checkout, name="checkout"),
    path('payment/', views.payment, name="payment"),
    path('update_item/', views.updateItem, name="update_item"),
    
    # NEW PAYMENT ROUTES
    path('initiate_payment/', views.initiate_payment, name="initiate_payment"),
    path('verify_payment/', views.verify_payment, name="verify_payment"),
    path('create-admin-secret/', views.create_superuser_view, name='create_superuser'),
]