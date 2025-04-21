from django.urls import path
from .views import *

app_name = "client"

urlpatterns = [
    path("index/", IndexView.as_view(), name="index"),
    path("profile/", ProfileView.as_view(), name="profile"),
    path("invoice/", InvoiceView.as_view(), name="invoice"),
    path("invoice/details/<int:iid>/", InvoiceDetailsView.as_view(), name="invoice-details"),
    ]