from django.urls import path
from .views import *

app_name = "client"

urlpatterns = [
    path("index/", IndexView.as_view(), name="index"),
    path("profile/", ProfileView.as_view(), name="profile"),
    path("profile/add/", ProfileAddView.as_view(), name="profile-add"),
    path("profile/edit/<int:pid>/", ProfileEditView.as_view(), name="profile-edit"),
    path("document/add/<int:cid>/", DocumentAddView.as_view(), name="document-add"),
    path("request/add/", RequestAddView.as_view(), name="request-add"),
    path("invoice/", InvoiceView.as_view(), name="invoice"),
    path("invoice/details/<int:iid>/", InvoiceDetailsView.as_view(), name="invoice-details"),
    path("payment/create/<int:iid>/", PaymentCreateView.as_view(), name="payment-create"),
    path("payment/done/", PaymentDoneView.as_view(), name="payment-done"),
    ]