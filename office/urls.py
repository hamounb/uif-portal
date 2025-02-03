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
    path('customer/exhibition/edit/<int:id>/', CustomerExhibitionEditView.as_view(), name='customer-exhibition-edit'),
    # path('request/list/', RequestListView.as_view(), name='request-list'),
    # path('request/details/<int:rid>/', RequestDetailsView.as_view(), name='request-details'),
    path('invoice/list/', InvoiceListView.as_view(), name='invoice-list'),
    path('invoice/remove/<int:iid>/', InvoiceRemoveView.as_view(), name='invoice-remove'),
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
    path('exhibition/details/<int:eid>/<int:iid>/', ExhibitionDetailsEditView.as_view(), name='exhibition-details-edit'),
    path('exhibition/status/<int:id>/', ExhibitionStatusView.as_view(), name='exhibition-status'),
    path('payment/list/', PaymentListView.as_view(), name='payment-list'),
    path('payment/add/<int:iid>/', PaymentAddView.as_view(), name='payment-add'),
    path('payment/edit/<int:iid>/<int:pid>/', PaymentEditView.as_view(), name='payment-edit'),
    path('payment/checkout/<int:iid>/', CheckoutView.as_view(), name='checkout'),
    path('payment/deposit/add/', DepositAddView.as_view(), name='deposit-add'),
    ]