from django.urls import path
from .views import *

app_name = "client"

urlpatterns = [
    path("index/", IndexView.as_view(), name="index"),
    path("profile/", ProfileView.as_view(), name="profile"),
    path("profile/add/", ProfileAddView.as_view(), name="profile-add"),
    path("profile/edit/<int:pid>/", ProfileEditView.as_view(), name="profile-edit"),
    path("exhibition/", ExhibitionView.as_view(), name="exhibition"),
    path("document/add/<int:cid>/", DocumentAddView.as_view(), name="document-add"),
    path("request//add/", RequestAddView.as_view(), name="request-add"),
    path("request/document/add/<int:rid>/", RequestDocumentAddView.as_view(), name="request-document-add"),
    path("invoice/", InvoiceView.as_view(), name="invoice"),
    path("invoice/details/<int:iid>/", InvoiceDetailsView.as_view(), name="invoice-details"),
    path("invoice/done/<int:iid>/", InvoiceDoneView.as_view(), name="invoice-done"),
    path("payment/create/<int:iid>/<str:pay>/", PaymentCreateView.as_view(), name="payment-create"),
    path("payment/<int:iid>/done/", PaymentDoneView.as_view(), name="payment-done"),
    ]