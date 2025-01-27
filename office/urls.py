from django.urls import path
from .views import *

app_name = "office"

urlpatterns = [
    path('', Test.as_view(), name='test'),
    path('home/', HomeView.as_view(), name='home'),
    path('customer/list/', CustomerListView.as_view(), name='customer-list'),
    path('customer/add/', CustomerAddView.as_view(), name='customer-add'),
    path('customer/change/<int:cid>/', CustomerChangeView.as_view(), name='customer-change'),
    path('customer/exhibition/<int:id>/', CustomerExhibitionView.as_view(), name='customer-exhibition'),
    # path('request/list/', RequestListView.as_view(), name='request-list'),
    # path('request/details/<int:rid>/', RequestDetailsView.as_view(), name='request-details'),
    path('invoice/add/', InvoiceAddView.as_view(), name='invoice-add'),
    path('invoice/list/', InvoiceListView.as_view(), name='invoice-list'),
    path('invoice/unpaid/', InvoiceUnpaidView.as_view(), name='invoice-unpaid'),
    path('invoice/details/<int:iid>/', InvoiceDetailsView.as_view(), name='invoice-details'),
    path('invoice/edit/<int:iid>/', InvoiceEditView.as_view(), name='invoice-edit'),
    path('document/list/', DocumentsListView.as_view(), name='documents-list'),
    path('document/add/<int:id>/', DocumentsAddView.as_view(), name='documents-add'),
    path('document/del/<int:fid>/', DocumentsDelView.as_view(), name='documents-del'),
    path('document/accept/<int:fid>/', DocumentsAcceptView.as_view(), name='documents-accept'),
    path('document/deny/<int:fid>/', DocumentsDenyView.as_view(), name='documents-deny'),
    # path('message/list/', MessagesListView.as_view(), name='message-list'),
    # path('message/add/', MessageAddView.as_view(), name='message-add'),
    # path('message/change/<int:mid>/', MessageChangeView.as_view(), name='message-change'),
    path('exhibition/add/', ExhibitionAddView.as_view(), name='exhibition-add'),
    path('exhibition/list/', ExhibitionListView.as_view(), name='exhibition-list'),
    path('exhibition/details/<int:eid>/', ExhibitionDetailsView.as_view(), name='exhibition-details'),
    path('exhibition/status/<int:id>/', ExhibitionStatusView.as_view(), name='exhibition-status'),
    path('payment/list/', PaymentListView.as_view(), name='payment-list'),
    path('payment/add/<int:id>/', PaymentAddView.as_view(), name='payment-add'),
    path('payment/edit/<int:id>/', PaymentEditView.as_view(), name='payment-edit'),
    ]