from django.urls import path

from . import views

app_name = "self-service-kiosk"
urlpatterns = [
    path("", views.all_products_view, name="index"),
    path("login/", views.user_login, name="login"),
    path('cart/', views.cart, name='cart'),
    path('confirm_order/', views.confirm_order, name='confirm_order'),
    path('account_details/', views.account_details, name='account_details'),
    path('logout/', views.user_logout, name='logout'),
    path('update_quantity/<int:item_id>/<int:quantity>/', views.update_quantity, name='update_quantity'),
    path('all_products/', views.all_products_view, name='all_products'),
    path('register/', views.register, name='register'),
    path('set_password/<uuid:token>/', views.set_password, name='set_password'),
    path('payment_problem/', views.payment_problem, name='payment_problem'),
    path('guest_login/', views.guest_login, name='guest_login'),
    path('order_success/<int:case>/', views.order_success, name='order_success'),
    path('forgot_password/', views.forgot_password, name='forgot_password'),
    path('qr/', views.qr_code_view, name='qr_code'),
    path('login/token/<uuid:token>/', views.login_with_token, name='login_with_token'),
    path('process_payment/', views.process_payment, name='process_payment'),
    path('invoices/<str:file_path>/', views.invoice_view, name='invoice_view'),
    path('order/<int:order_id>/', views.order_detail, name='order_detail'),
    path('help_page/', views.help_page, name='help_page'),
    path('send_feedback/', views.send_feedback, name='send_feedback'),
]
