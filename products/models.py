from contextlib import nullcontext
from distutils.command.upload import upload
from django.db import models
from accounts.models import User
# Create your models here.
import uuid
import random

class ProductStatusCode(models.Model):
    ProductStatusCode_id = models.AutoField(primary_key=True, editable=False)
    ProductStatusCode = models.CharField(max_length=100, unique=False)
    Status_Public = models.CharField(max_length=100, unique=False)
    Description = models.TextField()

    class Meta:
        db_table = "tbl_ProductStatusCode"

    def __str__(self):
        return self.ProductStatusCode

# by Anand
class ProductCategory(models.Model):
    category_id = models.UUIDField(primary_key=True, editable=False, default=uuid.uuid4)
    category = models.CharField(max_length=200, null=True, blank=True)
    created_at = models.DateField(auto_now_add=True, null=True)

    def __str__(self):
        return self.category

    @property
    def get_products(self):
        return Products.objects.filter(Category__category=self.category)


class ProductManager(models.Manager):
    def create_products(self, **fields):
        # QrCode_Account_id = fields.get('QrCode_Account_id', None)
        fields.pop('Product_Image')
        products = self.create(**fields)
        # products.QrCode_Account = QrCode_Account_id
        # products.save

        return products


class Products(models.Model):
    Products_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    QrCode_Product =  models.FileField(upload_to='user/Products_Qr',  null=True, blank=True)
    Attach_supporting_document = models.FileField(upload_to='user/Product_docs', null=True, blank=True)
    QrCode_Account = models.ForeignKey(User, null=True,on_delete = models.DO_NOTHING,related_name='my_products')
    ProductStatusCode = models.CharField(max_length=100, null=True)
    ProductName = models.CharField(max_length=100, unique=False)
    ProductDescription = models.TextField()
    ProductYearOfBirth = models.CharField(max_length=100,null=True)
    Category = models.ForeignKey(ProductCategory, on_delete=models.DO_NOTHING, null=True)
    Product_lat = models.DecimalField(max_digits=16, decimal_places=10, null=True, blank=True)
    Product_long = models.DecimalField(max_digits=16, decimal_places=10, null=True, blank=True)
    distance = models.DecimalField(max_digits=16, decimal_places=10, null=True, blank=True)
    Product_Image_1 = models.ImageField(upload_to="user/Products_IMG", null=True, blank=True)
    Product_Image_2 = models.ImageField(upload_to="user/Products_IMG", null=True, blank=True)
    Product_Image_3 = models.ImageField(upload_to="user/Products_IMG", null=True, blank=True)
    Product_Image_4 = models.ImageField(upload_to="user/Products_IMG", null=True, blank=True)
    Product_Image_5 = models.ImageField(upload_to="user/Products_IMG", null=True, blank=True)
    make = models.CharField(max_length=100, null=True, blank=True)
    model_number = models.CharField(max_length=50, null=True, blank=True)
    product_address = models.CharField(max_length=200, null=True, blank=True)
    hour_basis = models.CharField(max_length=20, null=True, blank=True)
    delivery_fee = models.FloatField(null=True, blank=True)
    delivery_status = models.BooleanField(default=False)
    OneDay_BasePrice = models.FloatField(null=True, blank=True)
    oneDay_status = models.BooleanField(default=False)
    OneWeek_BasePrice = models.FloatField(null=True, blank=True)
    oneWeek_status = models.BooleanField(default=False)
    OneMonth_BasePrice = models.FloatField(null=True, blank=True)
    oneMonth_status = models.BooleanField(default=False)
    DepositRequired = models.BooleanField(default=False)
    DepositAmount = models.FloatField(default=0.00,null=True, blank=True)
    ServiceMaintRequired = models.BooleanField(default=False)
    ServiceMaintAmount = models.FloatField(default=0.00,null=True, blank=True)
    extra_fees_status = models.BooleanField(default=False)
    extra_fees = models.FloatField(default=0.00,null=True, blank=True)
    grace_period = models.CharField(max_length=100, null=True, blank=True)
    maintenance_break = models.CharField(max_length=100, null=True, blank=True)
    is_wishlist = models.BooleanField(default=False)
    created_at = models.DateField(auto_now_add=True, null=True)
    is_verified = models.BooleanField(default=False)
    objects = ProductManager()

    class Meta:
        db_table = "tbl_ProductRegistration"
        
    def __str__(self):
        return f'{self.ProductName} - {self.QrCode_Account.email}'
    
# By Anand
class UnavailabilityDate(models.Model):
    product = models.ForeignKey(Products, on_delete=models.CASCADE, null=True, related_name='product_availability_date')
    unavailabilityDate = models.CharField(max_length=100, null=True)

    def __str__(self):
        return f'{self.product.ProductName}'

class Product_Images(models.Model):
    product_id = models.ForeignKey(Products, related_name='product_id',null=True,on_delete = models.CASCADE)
    Product_Image = models.FileField(upload_to='user/Product_images', null=True, blank=True)
    QrCode_Product = models.ForeignKey(Products, related_name='qrcode_product',null=True,on_delete = models.CASCADE)

    class Meta:

        db_table = "tbl_ProductPhotos"



# By Anand 
class Wishlist(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    product = models.ForeignKey(Products, on_delete=models.CASCADE, null=True)
    added_date = models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return self.user.Name_First

# By Anand
class Reward(models.Model):
    reward_id = models.UUIDField(primary_key=True, editable=False, default=uuid.uuid4)
    user = models.ForeignKey(User, on_delete=models.DO_NOTHING, null=True, blank=True)
    product = models.ForeignKey(Products, on_delete=models.DO_NOTHING, null=True)
    points = models.FloatField(default=00.00, null=True)
    referral = models.CharField(max_length=200, null=True, blank=True)
    description = models.TextField(null=True, blank=True)
    dateTime = models.DateTimeField(auto_now_add=True, null=True)

    def __str__(self):
        return self.user.Name_First

# By Anand
class RequestInbox(models.Model):
    title = models.CharField(max_length=250, null=True)
    product = models.ForeignKey(Products, on_delete=models.DO_NOTHING, null=True, blank=True)
    renter = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    lender = models.ForeignKey(User, on_delete=models.CASCADE, related_name="lender", null=True, blank=True)
    from_date = models.CharField(max_length=100, null=True, blank=True)
    to_date = models.CharField(max_length=50, null=True, blank=True)
    price = models.CharField(max_length=100, null=True, blank=True)
    reward_points = models.CharField(max_length=100,null=True, blank=True, default=0.0)
    STATUS_CHOICES = (
        ('Requested', 'Requested'),
        ('Accepted', 'Accepted'),
        ('Rejected', 'Rejected'),
    )
    request_status = models.CharField(max_length=200, choices=STATUS_CHOICES, null=True, blank=True)
    
    PAYMENT_STATUS_CHOICES = (
        ('Paid','Paid'),
        ('Failed','Failed'),
        ('Pending','Pending'),
    )
    payment_status = models.CharField(max_length=50, null=True, choices=PAYMENT_STATUS_CHOICES, default='Pending')
    isRead = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True, null=True)

    def __str__(self):
        return self.title
    #Order By
    class Meta:
        ordering = ('-created_at',)

# By Anand
class Referral(models.Model):
    referrer = models.OneToOneField(User, on_delete=models.DO_NOTHING, null=True)
    referrered = models.ForeignKey(User, on_delete=models.DO_NOTHING, null=True, related_name="referred_by")
    points = models.CharField(max_length=1000, null=True, blank=True)

    class Meta:
        unique_together = (('referrer', 'referrered'))

    def save(self, *args, **kwargs):
        pass



# https://stackoverflow.com/questions/58115738/realizing-rating-in-django


# By Anand
class ReportIncident(models.Model):
    user = models.ForeignKey(User, on_delete=models.DO_NOTHING, null=True)
    about = models.CharField(max_length=100, null=True)
    transaction_id = models.CharField(max_length=100, null=True)
    description = models.TextField(null=True)
    photo = models.FileField(upload_to='user/report_incident/img', null=True)
    document = models.FileField(upload_to='user/report_incident', null=True)
    device_id = models.CharField(max_length=1000, null=True, blank=True)
    reply = models.CharField(max_length=500, null=True, blank=True)
    securityDeposit = models.CharField(max_length=100, null=True, blank=True)
    lateFees = models.CharField(max_length=100, null=True, blank=True)
    created = models.DateTimeField(auto_now_add = True, null=True)
    status = models.BooleanField(default=False)
    close_date = models.DateTimeField(auto_now=True)
    def __str__(self):
        return self.about


# By Anand
import datetime
class OrderDetails(models.Model):
    request_inbox = models.ForeignKey(RequestInbox, on_delete=models.DO_NOTHING, null=True, blank=True)
    lender = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    renter = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True, related_name="renter_id")
    product = models.ForeignKey(Products, on_delete=models.DO_NOTHING, null=True, blank=True)
    payment_id = models.CharField(max_length=100, null=True, blank=True)
    amount = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True)
    delivery_fee = models.FloatField(default=0.00,null=True, blank=True)
    reward_points = models.CharField(max_length=100,null=True, blank=True, default=0.0)
    STATUS_CHOICES = (
        ('Paid','Paid'),
        ('Failed','Failed'),
        ('Pending','Pending'),
        ('Refund','Refund'),
    )
    payment_status = models.CharField(max_length=50, null=True, choices=STATUS_CHOICES, default='Pending')
    date_of_payment = models.DateTimeField(auto_now_add=True)
    renter_pickup_status = models.BooleanField(default=False)
    renter_return_status = models.BooleanField(default=False)
    lender_pickup_status = models.BooleanField(default=False)
    lender_return_status = models.BooleanField(default=False)
    final_pickup_status = models.BooleanField(default=False)
    final_return_status = models.BooleanField(default=False)
    today = datetime.datetime.now()
    month = today.strftime('%B')
    year = today.strftime("%Y")
    sales_month = models.CharField(max_length=100,default=month)
    sales_year = models.CharField(max_length=100, default=year)
    update_at = models.DateField(auto_now_add=True)

    def __str__(self):
        return f'Order ID {self.id} - Sales Month {self.sales_month} - Sales Year {self.sales_year}'

    class Meta:
        ordering = ['-date_of_payment']

# By Anand
class ProductPickUpReturn(models.Model):
    pickUp_id = models.UUIDField(primary_key=True, unique=True, default=uuid.uuid4, editable=False)
    order = models.ForeignKey(OrderDetails, on_delete=models.CASCADE, null=True)
    product = models.ForeignKey(Products, on_delete=models.DO_NOTHING, null=True, blank=True)
    lender = models.ForeignKey(User, on_delete=models.DO_NOTHING, null=True, blank=True)
    renter = models.ForeignKey(User, on_delete=models.DO_NOTHING, related_name='renter_name', null=True, blank=True)
    renter_pickup_img = models.ImageField(upload_to="user/renter/ProductPickupImage", null=True, blank=True)
    renter_return_img = models.ImageField(upload_to="user/renter/ProductReturnImage", null=True, blank=True)
    lender_pickup_img = models.ImageField(upload_to="user/lender/ProductReturnImage", null=True, blank=True)
    lender_return_img = models.ImageField(upload_to="user/lender/ProductPickupImage", null=True, blank=True)
    total_amount = models.FloatField(null=True)
    renter_pickup_location = models.CharField(max_length=250, null=True, blank=True)
    renter_return_location = models.CharField(max_length=250, null=True, blank=True)
    PAYMENT_STATUS = (
        ('Recieved','Recieved'),
        ('Not Recieved','Not Recieved'),
    )
    status_of_payment = models.CharField(max_length = 100, choices=PAYMENT_STATUS, null=True, blank=True)
    renter_return_status = models.BooleanField(default=False)
    renter_pickup_status = models.BooleanField(default=False)
    lender_pickup_status = models.BooleanField(default=False)
    lender_return_status = models.BooleanField(default=False)
    final_pickup_status = models.BooleanField(default=False)
    final_return_status = models.BooleanField(default=False)
    renter_pickUp_date = models.DateTimeField(null=True, blank=True)
    renter_return_date = models.DateTimeField(null=True, blank=True)
    lender_pickUp_date = models.DateTimeField(null=True, blank=True)
    lender_return_date = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f'Pickup ID {self.pickUp_id} - Product Name {self.product.ProductName}'
    
#By Anand
class LenderReviews(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name = 'user', null=True)
    lender = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    rating = models.IntegerField(null=True)
    about_lender = models.TextField(null=True)
    def __str__(self):
        return f'Rating as a lender {self.lender.Name_First}'

class RenterReviews(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    renter = models.ForeignKey(User, on_delete=models.CASCADE, related_name="myReview", null=True, blank=True)
    renterRating = models.IntegerField(null=True)
    about_renter = models.TextField(null=True)
    def __str__(self):
        return f'My rating as a renter {self.renter.Name_First}'

#By Anand
class ProductReviews(models.Model):
    product = models.ForeignKey(Products, on_delete=models.CASCADE, null=True)
    renter = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    rating = models.IntegerField(null=True)
    about_product = models.TextField(null=True)
    def __str__(self):
        return self.product.ProductName

