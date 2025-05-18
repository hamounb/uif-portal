from django.db import models
from django.contrib.auth.models import User

# Create your models here.

def documents_directory_path(instance, filename):
    # file will be uploaded to MEDIA_ROOT/user_<id>/<filename>
    return f"{instance.customer.pk}/{filename}"
    # "{0}/{1}".format(instance.user.id, filename)


class BaseModel(models.Model):
    user_modified = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        related_name='%(class)s_user_modified',
        null=True,
        blank=True,
        verbose_name='کاربر ویرایش'
        )
    user_created = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        related_name='%(class)s_user_created',
        null=True,
        blank=True,
        verbose_name='کاربر ایجاد'
        )
    created_date = models.DateTimeField(verbose_name='تاریخ ایجاد', auto_now_add=True)
    modified_date = models.DateTimeField(verbose_name='تاریخ تغییرات', auto_now=True)

    class Meta:
        abstract = True


class CustomerModel(BaseModel):
    KIND_REAL = 'real'
    KIND_LEGAL = 'legal'
    KIND_CHOICES = (
        (KIND_REAL, 'حقیقی'),
        (KIND_LEGAL, 'حقوقی')
    )
    is_active = models.BooleanField(verbose_name='فعال', default=False)
    sid = models.CharField(verbose_name='کد تفصیلی', max_length=50, null=True, blank=True)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, verbose_name='کاربر')
    kind = models.CharField(verbose_name='نوع مشارکت کننده', max_length=50, choices=KIND_CHOICES, default=KIND_REAL)
    brand = models.CharField(verbose_name='نام تجاری', max_length=100)
    company = models.CharField(verbose_name='نام شرکت', max_length=100, null=True, blank=True)
    ceoname = models.CharField(verbose_name='نام مدیرعامل', max_length=100, null=True, blank=True)
    ncode = models.CharField(verbose_name='شناسه ملی', max_length=11, null=True, blank=True)
    phone = models.CharField(verbose_name='تلفن', max_length=11, null=True, blank=True)
    fax = models.CharField(verbose_name='فکس', max_length=11, null=True, blank=True)
    email = models.EmailField(verbose_name='ایمیل', null=True, blank=True)
    postalcode = models.CharField(verbose_name='کد پستی', max_length=10, null=True, blank=True)
    address = models.TextField(verbose_name='آدرس', null=True, blank=True)

    def __str__(self):
        if self.kind == self.KIND_REAL:
            if self.user:
                return f"{self.brand}({self.user.first_name} {self.user.last_name})"
            else:
                return f"{self.brand}"
        else:
            if self.user:
                return f"{self.brand}-{self.company}({self.user.first_name} {self.user.last_name})"
            else:
                return f"{self.brand}-{self.company}"
    
    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["brand", "user"], name='branduser'),
            models.UniqueConstraint(fields=["sid"], name='specid')
    ]
        verbose_name = 'مشارکت کننده'
        verbose_name_plural = 'مشارکت کنندگان'


class DocumentsModel(BaseModel):
    STATE_WAIT = 'wait'
    STATE_ACCEPT = 'accept'
    STATE_DENY = 'deny'
    STATE_CHOICES = (
        (STATE_WAIT, 'در انتظار بررسی'),
        (STATE_ACCEPT, 'قبول شده'),
        (STATE_DENY, 'رد شده')
    )
    is_active = models.BooleanField(verbose_name='فعال', default=True)
    state = models.CharField(verbose_name='وضعیت', max_length=50, choices=STATE_CHOICES, default=STATE_WAIT)
    customer = models.ForeignKey(CustomerModel, on_delete=models.SET_NULL, null=True, blank=True, verbose_name='کاربر')
    file = models.FileField(verbose_name='مدرک', upload_to=documents_directory_path)
    description = models.TextField(verbose_name="توضیحات", null=True, blank=True)

    def __str__(self):
        if self.customer is not None:
            return f"{self.customer.brand} - {self.file.name}"
        return self.file.name
    
    class Meta:
        verbose_name = 'مدرک'
        verbose_name_plural = 'مدارک'


class ExhibitionModel(BaseModel):
    is_active = models.BooleanField(verbose_name='فعال', default=True)
    sid = models.CharField(verbose_name='کد معین', max_length=50, null=True, blank=True)
    title = models.CharField(verbose_name='عنوان نمایشگاه', max_length=200)
    price = models.CharField(verbose_name='قیمت', max_length=20)
    value_added = models.CharField(verbose_name='ارزش افزوده', max_length=10)
    min_area = models.CharField(verbose_name='حداقل متراژ(مترمربع)', max_length=100)
    date = models.DateField(verbose_name='تاریخ برگزاری', null=True, blank=True)

    def __str__(self):
        return f"{self.title} - {self.date.year}"
    
    class Meta:
        verbose_name = 'نمایشگاه'
        verbose_name_plural = 'نمایشگاه‌ها'

class WalletModel(BaseModel):
    user = models.OneToOneField(User, on_delete=models.PROTECT, verbose_name="کاربر")
    cash = models.CharField(verbose_name="موجودی(ریال)", max_length=15, default="0")

    def __str__(self):
        return f"{self.user.username} ({self.user.first_name} {self.user.last_name})"
    
    class Meta:
        verbose_name = "کیف پول"
        verbose_name_plural = "کیف‌های پول"


class InvoiceModel(BaseModel):
    STATE_PAID = "paid"
    STATE_UNPAID = "unpaid"
    STATE_CHOICES = (
        (STATE_PAID, "پرداخت شده"),
        (STATE_UNPAID, "پرداخت نشده")
    )
    is_active = models.BooleanField(verbose_name="فعال", default=True)
    state = models.CharField(verbose_name="وضعیت", max_length=50, choices=STATE_CHOICES, default=STATE_UNPAID)
    wallet = models.ForeignKey(WalletModel, on_delete=models.SET_NULL, verbose_name="کیف پول", null=True, blank=True)
    customer = models.ForeignKey(CustomerModel, on_delete=models.SET_NULL, verbose_name="مشارکت کننده", null=True, blank=True)
    exhibition = models.ForeignKey(ExhibitionModel, on_delete=models.SET_NULL, verbose_name="نمایشگاه", null=True, blank=True)
    booth_number = models.CharField(verbose_name="شماره غرفه", max_length=100, null=True, blank=True)
    price = models.CharField(verbose_name="مبلغ", max_length=20, default="0")
    area = models.CharField(verbose_name="متراژ(مترمربع)", max_length=9, default="0")
    value_added = models.CharField(verbose_name="ارزش افزوده(درصد)", max_length=10, default="0")
    discount = models.CharField(verbose_name="تخفیف(درصد)", max_length=3, default="0")
    amount = models.CharField(verbose_name="مبلغ نهایی", max_length=20, default="0")

    def __str__(self):
        return f"ش: {self.pk}-{self.customer.brand} ({self.exhibition.title})"
    
    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["customer", "exhibition", "booth_number"], name='customer_exhibition_booth')
    ]
        verbose_name = "فاکتور"
        verbose_name_plural = "فاکتورها"

        
class BankModel(BaseModel):
    KIND_CURRENT = 'current'
    KIND_SHORT = 'short'
    KIND_LOAN = 'loan'
    KIND_CHOICES = (
        (KIND_CURRENT, "حساب جاری"),
        (KIND_SHORT, "حساب کوتاه مدت"),
        (KIND_LOAN, "حساب قرض‌الحسنه")
    )
    name = models.CharField(verbose_name="نام", max_length=100)
    account_number = models.CharField(verbose_name="شماره حساب", max_length=100)
    kind = models.CharField(verbose_name="نوع حساب", max_length=100, choices=KIND_CHOICES, default=KIND_CURRENT)

    def __str__(self):
        return f"{self.name}-{self.account_number}"
    
    class Meta:
        verbose_name = "حساب بانک"
        verbose_name_plural = "حساب بانک‌ها"


class PaymentModel(BaseModel):
    STATE_CHECK = 'check'
    STATE_CASH = 'cash'
    STATE_POS = 'pos'
    STATE_IPG = 'ipg'
    STATE_CHOICES = (
        (STATE_CHECK, 'چک بانکی'),
        (STATE_CASH, 'نقدی'),
        (STATE_POS, 'پوز بانکی'),
        (STATE_IPG, 'درگاه اینترنتی'),
    )
    state = models.CharField(verbose_name="وضعیت", max_length=50, choices=STATE_CHOICES, default=STATE_POS)
    wallet = models.ForeignKey(WalletModel, on_delete=models.PROTECT, verbose_name="کیف پول")
    invoice = models.ForeignKey(InvoiceModel, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="فاکتور")
    bank = models.ForeignKey(BankModel, on_delete=models.SET_NULL, verbose_name="حساب بانکی", null=True, blank=True)
    amount = models.IntegerField(verbose_name="مبلغ", default=1000)
    cardnumber = models.CharField(verbose_name="شماره کارت/چک", max_length=32, null=True, blank=True)
    issuerbank = models.CharField(verbose_name="بانک صادرکننده", max_length=150, null=True, blank=True)
    name = models.CharField(verbose_name="مشخصات صاحب چک", max_length=150, null=True, blank=True)
    rrn = models.CharField(verbose_name="شماره سند بانکی", max_length=150, null=True, blank=True)
    tracenumber = models.CharField(verbose_name="شماره پیگیری", max_length=150, null=True, blank=True)
    digitalreceipt = models.CharField(verbose_name="رسید دیجیتال", max_length=150, null=True, blank=True)
    respcode = models.IntegerField(verbose_name="کد نتیجه تراکنش", default=0, null=True, blank=True)
    respmsg = models.CharField(verbose_name="متن نتیجه تراکنش", max_length=150, null=True, blank=True)
    payload = models.CharField(verbose_name="توضیحات", max_length=150, null=True, blank=True)
    datepaid = models.CharField(verbose_name="تاریخ و زمان تراکنش", max_length=50, null=True, blank=True)

    def __str__(self):
        if self.state == self.STATE_POS:
            return f"{self.wallet.user.username} - شماره پیگیری: {self.tracenumber}"
        return f"{self.state}-{self.invoice.customer.brand} - مبلغ: {self.amount}"
    
    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["digitalreceipt"], name='specdr')
    ]
        verbose_name = 'پرداخت'
        verbose_name_plural = 'پرداخت‌ها'


class RequestModel(BaseModel):
    STATE_ACCEPT = 'accept'
    STATE_DENY = 'deny'
    STATE_WAIT = 'wait'
    STATE_CHOICES = (
        (STATE_ACCEPT, 'قبول شده'),
        (STATE_DENY, 'رد شده'),
        (STATE_WAIT, 'انتظار'),
    )
    state = models.CharField(verbose_name="وضعیت", max_length=50, choices=STATE_CHOICES, default=STATE_WAIT)
    exhibition = models.ForeignKey(ExhibitionModel, on_delete=models.CASCADE, verbose_name="عنوان نمایشگاه")
    customer = models.ForeignKey(CustomerModel, on_delete=models.CASCADE, verbose_name="مشارکت کننده")
    description = models.TextField(verbose_name="توضیحات و محصولات")
    message = models.TextField(verbose_name="پیام")

    def __str__(self):
        return f"{self.customer.brand}-{self.exhibition.title}"
    
    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["exhibition", "customer"], name='exhcus')
    ]
        verbose_name = 'درخواست'
        verbose_name_plural = 'درخواست‌ها'


class RequestDocumentsModel(BaseModel):
    request = models.ForeignKey(RequestModel, on_delete=models.CASCADE, verbose_name="درخواست")
    file = models.FileField(verbose_name="مدارک", upload_to=documents_directory_path)

    def __str__(self):
        return f"{self.request.customer.brand}-{self.request.exhibition.title}"
    
    class Meta:
        verbose_name = 'مدرک درخواست'
        verbose_name_plural = 'مدارک درخواست‌ها'


# class DepositModel(BaseModel):
#     STATE_DEPOSIT = "deposit"
#     STATE_RETURN = "return"
#     STATE_PAYMENT = "payment"
#     STATE_CHOICES = (
#         (STATE_DEPOSIT, "بیعانه"),
#         (STATE_RETURN, "عودت"),
#         (STATE_PAYMENT, "اضافه به حساب")
#     )
#     state = models.CharField(verbose_name='وضعیت', max_length=50, choices=STATE_CHOICES, default=STATE_DEPOSIT)
#     wallet = models.ForeignKey(WalletModel, on_delete=models.PROTECT, verbose_name="کیف پول")
#     invoice_number = models.CharField(verbose_name="شماره سند", max_length=100, unique=True)
#     description = models.TextField(verbose_name="توضیحات", null=True, blank=True)

#     def __str__(self):
#         return f"{self.wallet.customer.brand}({self.wallet.customer.first_name} {self.wallet.customer.last_name}) - شماره سند: {self.invoice_number}"
    
#     class Meta:
#         verbose_name = "بیعانه"
#         verbose_name_plural = "بیعانه‌ها"


# class DepositPaymentModel(BaseModel):
#     deposit = models.ForeignKey(DepositModel, on_delete=models.PROTECT, max_length="بیعانه")
#     date = models.CharField(verbose_name="تاریخ رسید", max_length=10)
#     tracenumber = models.CharField(verbose_name="شماره پیگیری", max_length=150, null=True, blank=True)
#     amount = models.CharField(verbose_name="مبلغ", max_length=12, default="0")

#     def __str__(self):
#         return f"{self.tracenumber} - شماره سند: {self.deposit.invoice_number}"
    
#     class Meta:
#         verbose_name = "رسید بیعانه"
#         verbose_name_plural = "رسید بیعانه‌ها"


# class RequestModel(BaseModel):
#     STATE_WAIT = 'wait'
#     STATE_ACCEPT = 'accept'
#     STATE_DENY = 'deny'
#     STATE_CHOICES = (
#         (STATE_WAIT, 'در انتظار بررسی'),
#         (STATE_ACCEPT, 'قبول شده'),
#         (STATE_DENY, 'رد شده')
#     )
#     state = models.CharField(verbose_name='وضعیت', max_length=50, choices=STATE_CHOICES, default=STATE_WAIT)
#     user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, verbose_name='کاربر')
#     customer = models.ForeignKey(CustomerModel, on_delete=models.CASCADE, verbose_name='مشارکت کننده')
#     exhibition = models.ForeignKey(ExhibitionModel, on_delete=models.CASCADE, verbose_name='نمایشگاه')
#     area = models.IntegerField(verbose_name='متراژ', default=0)
#     rules = models.BooleanField(verbose_name='قوانین')
#     is_active = models.BooleanField(verbose_name='فعال', default=True)

#     def __str__(self):
#         return f"{self.customer.company} - {self.exhibition.title}"
    
#     class Meta:
#         verbose_name = 'درخواست'
#         verbose_name_plural = 'درخواست‌ها'


# class MessagesModel(BaseModel):
#     is_active = models.BooleanField(verbose_name='فعال', default=True)
#     customer = models.ForeignKey(CustomerModel, on_delete=models.CASCADE, verbose_name='مشارکت کننده')
#     text = models.TextField(verbose_name='متن پیام')

#     def __str__(self):
#         return f"{self.pk}.{self.customer.company} - ({self.customer.firstname} {self.customer.lastname})"
    
#     class Meta:
#         verbose_name = 'پیغام'
#         verbose_name_plural = 'پیغام‌ها'


# class MessageChangeModel(models.Model):
#     message = models.ForeignKey(MessagesModel, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="پیغام اصلی")
#     text = models.TextField(verbose_name='متن پیام')
#     user_modified = models.ForeignKey(
#         User,
#         on_delete=models.SET_NULL,
#         related_name='%(class)s_user_modified',
#         null=True,
#         blank=True,
#         verbose_name='کاربر ویرایش'
#         )
#     modified_date = models.DateTimeField(verbose_name='تاریخ تغییرات')

#     def __str__(self):
#         if self.message is not None:
#             return f"{self.message.pk}.{self.message.customer.company} - ({self.message.customer.firstname} {self.message.customer.lastname})"
#         return self.text
    
#     class Meta:
#         verbose_name = 'پیغام ویرایش شده'
#         verbose_name_plural = 'پیغام‌های ویرایشی'

