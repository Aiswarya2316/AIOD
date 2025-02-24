from django.urls import path
from .import views
urlpatterns = [
        path('',views.home,name='home'),
        path("registerparent/", views.customer_register, name="customer_register"),
        path("registerstaf/", views.seller_register, name="seller_register"),
        path("registeradmin/", views.admin_register, name="admin_register"),
        path("login/", views.user_login, name="login"),
        path("logout/", views.user_logout, name="logout"),
        path('customerhome',views.customerhome,name='customerhome'),
        path('stafhome',views.stafhome,name='stafhome'),
        path('categories/', views.category_list, name='category_list'),
        path('categoriesadd/', views.add_category, name='add_category'),
        path('causes/', views.cause_list, name='cause_list'),
        path('causesadd/', views.add_cause, name='add_cause'),
        path('donate/', views.donate, name='donate'),
        path('donation-success/', views.donation_success, name='donation_success'),
        path("donation-history/", views.donation_history, name="donation_history"),
        path('donations/', views.donation_list, name='donation_list'),
        path('create-payment/<int:donation_id>/', views.create_payment, name='create_payment'),
        path('verify-payment/', views.verify_payment, name='verify_payment'),
        path('causes/', views.cause_list, name='cause_list'),
        path('causes/category/<int:category_id>/', views.cause_list, name='cause_by_category'),

]







