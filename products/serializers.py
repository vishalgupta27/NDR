from ast import arg
from re import search
from xml.dom import ValidationErr
from rest_framework import serializers
from .models import *
import datetime
from login_portal.models import NDR_Taxes
from accounts.serializers import *
from dataclasses import fields
from login_portal.models import *

class ReadWriteSerializerMethodField(serializers.SerializerMethodField):
    def __init__(self, method_name=None, **kwargs):
        self.method_name = method_name
        kwargs['source'] = '*'
        super(serializers.SerializerMethodField, self).__init__(**kwargs)

    def to_internal_value(self, data):
        return {self.field_name: data}


class UnavailabiltyDateSerializer(serializers.ModelSerializer):
    # unavailabilityDate = serializers.CharField(required=False)
    class Meta:
        model = UnavailabilityDate
        fields = ['unavailabilityDate']

class ProductCategorySerialzer(serializers.ModelSerializer):
    class Meta:
        model = ProductCategory
        fields = ['category_id','category']


class ProductViewSerializer(serializers.ModelSerializer):
    DepositRequired = serializers.CharField(required=False)
    ServiceMaintRequired = serializers.CharField(required=False)
    ProductStatusCode = serializers.CharField(required=False)
    ProductYearOfBirth = serializers.CharField(required=False)
    delivery_fee = serializers.CharField(required=False)
    DepositAmount = serializers.CharField(required=False)
    ServiceMaintAmount = serializers.CharField(required=False)
    CategoryName = serializers.CharField(source='Category.category')
    
    Lander_name = serializers.CharField(source='QrCode_Account.Name_First')
    class Meta:
        model = Products
        fields = '__all__'
        # exclude  = ['Category']

    # #### writeable serializers
    # ProductYearOfBirth = ReadWriteSerializerMethodField('handle_ProductYearOfBirth')

    def handle_ProductYearOfBirth(self, obj):

        # https://stackoverflow.com/questions/49414976/django-rest-framework-serializer-with-reverse-relation

        print(obj, type(obj))
        # return Address.objects.get(QrCode_Account=obj.account_id).Address_id
        # if obj.ProductYearOfBirth is None:
        #     return None
        # return obj.ProductYearOfBirth.strftime('%d-%m-%Y')

    #### writeable serializers

    def validate(self,args):

        if len(args) == 0:
            raise serializers.ValidationError("please enter the below fields to update")

        #for each_attr in args.keys():
        #    if each_attr in ('ProductName', 'ProductDescription', 'Category', 'ProductYearOfBirth','OneDay_BasePrice',
        #                     'OneWeek_BasePrice','OneMonth_BasePrice','DepositRequired','DepositAmount','ServiceMaintRequired','ServiceMaintAmount'):
        ProductName = args.get('ProductName', None)
        ProductDescription = args.get('ProductDescription', None)
        # Category = args.get('Category', None)
        ProductYearOfBirth = args.get('ProductYearOfBirth', None)
        OneDay_BasePrice = args.get('OneDay_BasePrice', None)
        OneWeek_BasePrice = args.get('OneWeek_BasePrice', None)
        OneMonth_BasePrice = args.get('OneMonth_BasePrice', None)
        DepositRequired = args.get('DepositRequired', None)
        DepositAmount = args.get('DepositAmount', None)
        ServiceMaintRequired = args.get('ServiceMaintRequired', None)
        ServiceMaintAmount = args.get('ServiceMaintAmount', None)
        # Attach_supporting_document = args.get('Attach_supporting_document', None)
        ProductStatusCode = args.get('ProductStatusCode', None)
        # delivery_fee = args.get('delivery_fee', None)

        if ProductName is  None or len(ProductName.strip())>0:

            pass

        else:
            raise serializers.ValidationError("please Upload Product Name")

        if ProductDescription is  None or len(ProductDescription.strip()) > 0:

            pass

        else:

            raise serializers.ValidationError("please describe the Product")

        # if Category is None or len(Category) > 0:
        #     raise serializers.ValidationError("please enter Category")



        if DepositRequired is not None:
            try:
                if DepositRequired.lower() == 'true':
                    args['DepositRequired'] = True

                elif DepositRequired.lower() == 'false':
                    args['DepositRequired'] = False
                    # set Deposit amount as 0 when Deposit is not Required/True
                    DepositAmount = 0.00
                    args['DepositAmount'] = 0.00

                else:
                    raise serializers.ValidationError("Please provide 'True' or 'false'")

            except Exception as e:
                raise serializers.ValidationError(str(e))

        if ProductYearOfBirth is None:
            # print("ProductYearOfBirth ",ProductYearOfBirth,type(ProductYearOfBirth))
            # ## convert str to date obj
            # try:

            #     print(datetime.datetime.strptime(ProductYearOfBirth, "%d-%m-%Y").strftime("%Y-%m-%d"))

            #     handled_date = datetime.datetime.strptime(ProductYearOfBirth, "%d-%m-%Y").strftime("%Y-%m-%d")

            #     handled_date = datetime.datetime.strptime(handled_date, "%Y-%m-%d")

            #     args['ProductYearOfBirth'] = handled_date.date()
            # except Exception as e:
                raise serializers.ValidationError("please enter birth Year")



         #cast str to bool
        if ServiceMaintRequired is not None:
            try:
                if ServiceMaintRequired.lower() == 'true':
                    args['ServiceMaintRequired'] = True

                elif ServiceMaintRequired.lower() == 'false':
                    args['ServiceMaintRequired'] = False
                    # set Service Maintenance amount as 0 when Service Maintenance is not Required/True
                    ServiceMaintAmount = 0.00
                    args['ServiceMaintAmount'] = 0.00

                else:
                    raise serializers.ValidationError("Please provide 'True' or 'false'")

            except Exception as e:
                raise serializers.ValidationError(str(e))

        if ProductStatusCode is None:
            raise serializers.ValidationError("Enter Product Status Code")
            # if  ProductStatusCode.objects.filter(ProductStatusCode__iexact= Product_Status_Code ).exists() != True:

            #     raise serializers.ValidationError("ProductStatusCode doesnt exists")

            # else:
            #     args['Product_Status_Code_id'] = ProductStatusCode.objects.get(ProductStatusCode__exact=Product_Status_Code).ProductStatusCode_id
            #     args.pop('ProductStatusCode')

        return super().validate(args)


    def update(self, instance, validated_data):
        # https://stackoverflow.com/questions/53779723/django-rest-framework-update-with-kwargs-from-validated-data

        for attr, value in validated_data.items():
            setattr(instance, attr, value)
            print(setattr(instance, attr, value))
        instance.save()
        return instance


class ProductImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product_Images
        fields = ('id',
                  'Product_Image',
                  )


    def validate (self, args):
        Product_Image = args.get('Product_Image',None)
        if Product_Image is None:
            raise serializers.ValidationError("please Upload an Product Image to replace with with current one")

        return super().validate(args)



    def update(self, instance, validated_data):
        # https://stackoverflow.com/questions/53779723/django-rest-framework-update-with-kwargs-from-validated-data

        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance







class ProductRegister_Serializer(serializers.Serializer):
    # UnavailabilityDate = UnavailabiltyDateSerializer()
    Product_Image = serializers.FileField(required=False)
    Product_Image_1 = serializers.ImageField(required=False)
    Product_Image_2 = serializers.ImageField(required=False)
    Product_Image_3 = serializers.ImageField(required=False)
    Product_Image_4 = serializers.ImageField(required=False)
    Product_Image_5 = serializers.ImageField(required=False)
    Attach_supporting_document = serializers.FileField(required=False)
    ProductName = serializers.CharField(required=False)
    ProductDescription = serializers.CharField(required=False)
    ProductYearOfBirth = serializers.CharField(required=False)
    Product_lat = serializers.FloatField(max_value=None, min_value=None,required=False)
    Product_long = serializers.FloatField(max_value=None, min_value=None, required=False)
    make = serializers.CharField(required=False)
    model_number = serializers.CharField(required=False)
    product_address = serializers.CharField(required=False)
    delivery_fee = serializers.CharField(required=False)
    delivery_status = serializers.CharField(required=False)
    hour_basis = serializers.CharField(required=False)
    OneDay_BasePrice = serializers.FloatField(max_value=None, min_value=None,required=False)
    oneDay_status = serializers.CharField(required=False)
    OneWeek_BasePrice = serializers.FloatField(max_value=None, min_value=None,required=False)
    oneWeek_status = serializers.CharField(required=False)
    OneMonth_BasePrice = serializers.FloatField(max_value=None, min_value=None,required=False)
    oneMonth_status = serializers.CharField(required=False)
    DepositRequired = serializers.CharField(required=False)
    DepositAmount = serializers.FloatField(max_value=None, min_value=None,required=False)
    ServiceMaintRequired = serializers.CharField(required=False)
    ServiceMaintAmount = serializers.FloatField(max_value=None, min_value=None,required=False)
    ProductStatusCode = serializers.CharField(required=False)
    extra_fees_status = serializers.CharField(required=False)
    extra_fees = serializers.FloatField(max_value=None, min_value=None,required=False)
    grace_period = serializers.FloatField(required=False)
    maintenance_break = serializers.FloatField(required=False)
    #QrCode_Account_id = serializers.CharField(required=False)

    class Meta:
        model = Products
        fields = '__all__'

    


    def validate (self, args):
        Product_Image = args.get('Product_Image',None)
        Product_Image_2 = args.get('Product_Image_2', None)
        ProductName = args.get('ProductName', None)
        ProductDescription = args.get('ProductDescription', None)
        Product_lat = args.get('Product_lat',None)
        Product_long = args.get('Product_long',None)
        ProductYearOfBirth = args.get('ProductYearOfBirth',None)
        product_address = args.get('product_address', None)
        delivery_fee = args.get('delivery_fee', None)
        delivery_status = args.get('delivery_status', None)
        OneDay_BasePrice = args.get('OneDay_BasePrice',None)
        oneDay_status = args.get('oneDay_status', None)
        OneWeek_BasePrice = args.get('OneWeek_BasePrice',None)
        oneWeek_status = args.get('oneWeek_status', None)
        OneMonth_BasePrice = args.get('OneMonth_BasePrice',None)
        oneMonth_status = args.get('oneMonth_status', None)
        DepositRequired = args.get('DepositRequired',None)
        DepositAmount = args.get('DepositAmount',None)
        ServiceMaintRequired = args.get('ServiceMaintRequired',None)
        ServiceMaintAmount = args.get('ServiceMaintAmount',None)
        ProductStatusCode = args.get('ProductStatusCode', None)
        extra_fees_status = args.get('extra_fees_status', None)
        extra_fees = args.get('extra_fees', None)
        grace_period = args.get('grace_period', None)

        print('args',args)

        if Product_Image is None:
            raise serializers.ValidationError("please Upload Product Image")

        if Product_Image_2 is None:
            raise serializers.ValidationError("please Upload Product Image 2")

        if ProductName is None:
            raise serializers.ValidationError("please Upload Product Name")

        if ProductDescription is None:
            raise serializers.ValidationError("please Upload Product Description")

        # if Category_id is None:
        #     raise serializers.ValidationError("Please Select Category")

        if Product_lat is None:
            raise serializers.ValidationError("please Upload Product Lat")

        if Product_long is None:
            raise serializers.ValidationError("please Upload Product_long")

        # if address_type is None:
        #     raise serializers.ValidationError("please Upload Address Type")
        
        # if product_initial_cost is None:
        #     raise serializers.ValidationError("please Upload Product Initial Cost")
        
        # if availability_date is None:
        #     raise serializers.ValidationError("please Upload Availability Date")

        if ProductYearOfBirth is None:
            raise serializers.ValidationError("please Enter Product's Year Of Birth")

        # if ProductYearOfBirth is not None:
        #     print("ProductYearOfBirth ",ProductYearOfBirth,type(ProductYearOfBirth))
        #     ## convert str to date obj
        #     try:

        #         print(datetime.datetime.strptime(ProductYearOfBirth, "%d-%m-%Y").strftime("%Y-%m-%d"))

        #         handled_date = datetime.datetime.strptime(ProductYearOfBirth, "%d-%m-%Y").strftime("%Y-%m-%d")

        #         handled_date = datetime.datetime.strptime(handled_date, "%Y-%m-%d")

        #         args['ProductYearOfBirth'] = handled_date.date()
        #     except Exception as e:
        #         raise serializers.ValidationError("please enter date in dd-mm-yyyy")


        # if make is None:
        #     raise serializers.ValidationError("Please Enter Make(Brand Name)")

        # if model_number is None:
        #     raise serializers.ValidationError("Please Enter Model Number")

        if product_address is None:
            raise serializers.ValidationError("Please Enter Product Address!")
        
        # if delivery_fee is None:
        #     raise serializers.ValidationError("Please Enter Delivery Fee")

        if OneDay_BasePrice and OneWeek_BasePrice and OneMonth_BasePrice is None:
            raise serializers.ValidationError("Please Enter Anyone One Day, One Week, One Months Base Price")

        if OneDay_BasePrice is None or  not isinstance(OneDay_BasePrice, float):
            if not isinstance(OneDay_BasePrice, float):
                raise serializers.ValidationError("One Day Base Price must be a number")
            raise serializers.ValidationError("please Enter One Day Base Price")

        if OneWeek_BasePrice is None or  not isinstance(OneWeek_BasePrice, float):
            if not isinstance(OneWeek_BasePrice, float):
                raise serializers.ValidationError("One Week Base Price must be a number")
            raise serializers.ValidationError("please Enter One Week Base Price")


        if OneMonth_BasePrice is None or  not isinstance(OneMonth_BasePrice, float):
            if not isinstance(OneMonth_BasePrice, float):
                raise serializers.ValidationError("One Month Base Price must be a number")
            raise serializers.ValidationError("please Enter One Day Month Price")

        if DepositRequired is None:
            raise serializers.ValidationError("please set Deposit Required to True or False")
       
        #cast str to bool
        if DepositRequired is not None:
            try:
                if DepositRequired.lower() == 'true':
                    args['DepositRequired'] = True

                elif DepositRequired.lower() == 'false':
                    args['DepositRequired'] = False
                    # set Deposit amount as 0 when Deposit is not Required/True
                    DepositAmount = 0.00
                    args['DepositAmount'] = 0.00

                else:
                    raise serializers.ValidationError("Please provide 'True' or 'false'")

            except Exception as e:
                raise serializers.ValidationError(str(e))
        #By Anand
        if oneDay_status is not None:
            try:
                if oneDay_status.lower() == 'true':
                    args['oneDay_status'] = True
                elif oneDay_status.lower() == 'false':
                    args['oneDay_status'] =False
                else:
                    raise serializers.ValidationError("Please provide 'True' or 'False'")
            except Exception as e:
                raise serializers.ValidationError(str(e))

        #By Anand
        if oneWeek_status is not None:
            try:
                if oneWeek_status.lower() == 'true':
                    args['oneWeek_status'] = True
                elif oneWeek_status.lower() == 'false':
                    args['oneWeek_status'] =False
                else:
                    raise serializers.ValidationError("Please provide 'True' or 'False'")
            except Exception as e:
                raise serializers.ValidationError(str(e))
                
        #By Anand
        if oneMonth_status is not None:
            try:
                if oneMonth_status.lower() == 'true':
                    args['oneMonth_status'] = True
                elif oneMonth_status.lower() == 'false':
                    args['oneMonth_status'] =False
                else:
                    raise serializers.ValidationError("Please provide 'True' or 'False'")
            except Exception as e:
                raise serializers.ValidationError(str(e))

        if delivery_status is not None:
            try:
                if delivery_status.lower() == 'true':
                    args['delivery_status'] = True
                
                elif delivery_status.lower() == 'false':
                    args['delivery_status'] = False

                else:
                    raise serializers.ValidationError("Please provide 'True' or 'False'")
            except Exception as e:
                raise serializers.ValidationError(str(e))

        if ServiceMaintRequired is None:
            raise serializers.ValidationError("please set Service Maintenance Required to True or False")

        #cast str to bool
        if ServiceMaintRequired is not None:
            try:
                if ServiceMaintRequired.lower() == 'true':
                    args['ServiceMaintRequired'] = True

                elif ServiceMaintRequired.lower() == 'false':
                    args['ServiceMaintRequired'] = False
                    # set Service Maintenance amount as 0 when Service Maintenance is not Required/True
                    ServiceMaintAmount = 0.00
                    args['ServiceMaintAmount'] = 0.00

                else:
                    raise serializers.ValidationError("Please provide 'True' or 'false'")

            except Exception as e:
                raise serializers.ValidationError(str(e))

        if extra_fees_status is not None:
            try:
                if extra_fees_status.lower() == 'true':
                    args['extra_fees_status'] = True

                elif extra_fees_status.lower() == 'false':
                    args['extra_fees_status'] = False
                    # set Service Maintenance amount as 0 when Service Maintenance is not Required/True
                    extra_fees = 0.00
                    args['extra_fees'] = 0.00

                else:
                    raise serializers.ValidationError("Please provide 'True' or 'false'")

            except Exception as e:
                raise serializers.ValidationError(str(e))

        if DepositAmount is None or  not isinstance(DepositAmount, float):
            if not isinstance(DepositAmount, float):
                raise serializers.ValidationError("Deposit Amount must be a number")
            raise serializers.ValidationError("please Enter Deposit Amount")


        if ServiceMaintAmount is None or  not isinstance(ServiceMaintAmount, float):
            if not isinstance(ServiceMaintAmount, float):
                raise serializers.ValidationError("Service Maintenance Amount must be a number")
            raise serializers.ValidationError("please Enter Service Maintenance Amount")

        # if Attach_supporting_document is None:

        #     raise serializers.ValidationError("please provide supporting documents for products")

        if ProductStatusCode is None:

            raise serializers.ValidationError("please ProductStatusCode")


        # if  ProductStatusCode.objects.filter(ProductStatusCode__iexact= Product_Status_Code ).exists() != True:

        #     raise serializers.ValidationError("ProductStatusCode doesnt exists")

        # else:
        #     args['Product_Status_Code_id'] = ProductStatusCode.objects.get(ProductStatusCode__exact=Product_Status_Code).ProductStatusCode_id
        #     args.pop('ProductStatusCode')


        #if QrCode_Account_id is None:
        #    raise serializers.ValidationError("cannot Find USER ID *Foreign key Integrity*")
        #print('QrCode_Account_id',QrCode_Account_id)
        return super().validate(args)


    def create(self, validated_data):

        product = Products.objects.create_products(**validated_data)

        return product



# By Anand


#By Anand
class WishlistSerializer(serializers.Serializer):
    product_id = serializers.CharField(required=False)
    class Meta:
        model = Wishlist
        fields = '__all__'

    def validate(self, args):
        product_id = args.get('product_id', None)
        if product_id is None:
            raise serializers.ValidationError("Enter Valid Product Id")
        return super().validate(args)

    def create(self, validated_data):
        print("method Colled")
        wishlist = Wishlist.objects.create(**validated_data)
        return wishlist

# By Anand 
class ProductWishlistSerializer(serializers.Serializer):
    product = ProductViewSerializer()
    class Meta:
        model = Wishlist
        fields = '__all__'


# By Anand
class ViewRenterInbox(serializers.ModelSerializer):
    title = serializers.CharField(required=False)
    from_date = serializers.CharField(required=False)
    to_date = serializers.CharField(required=True)
    request_status = serializers.CharField(required=True)
    price = serializers.CharField(required=True)
    lender = UserSerializer(read_only=True)
    product = ProductViewSerializer(read_only=True)
    class Meta:
        model = RequestInbox
        fields = '__all__'

# By Anand
class ViewRequestInbox(serializers.ModelSerializer):
    title = serializers.CharField(required=False)
    from_date = serializers.CharField(required=False)
    to_date = serializers.CharField(required=True)
    request_status = serializers.CharField(required=True)
    price = serializers.CharField(required=True)
    renter = UserSerializer(read_only=True)
    product = ProductViewSerializer(read_only=True)
    class Meta:
        model = RequestInbox
        fields = '__all__'

# By Anand
class RequestInboxSerializer(serializers.ModelSerializer):
    title = serializers.CharField(required=False)
    renter = serializers.CharField(required=False)
    price = serializers.CharField(required=False)
    lender_id = serializers.CharField(required=False)
    from_date = serializers.CharField(required=False)
    to_date = serializers.CharField(required=False)
    product_id = serializers.CharField(required=False)
    request_status = serializers.CharField(required=False)

    class Meta:
        model = RequestInbox
        fields = ['title', 'product_id','price', 'renter','lender_id','from_date','to_date','request_status']
    
        
# By Anand 
class ReportIncidentSerializer(serializers.ModelSerializer):
    about = serializers.CharField(required=False)
    description = serializers.CharField(required=False)
    transaction_id = serializers.CharField(required=False)
    photo = serializers.FileField(required=False)
    document = serializers.FileField(required=False)
    securityDeposit = serializers.CharField(required=False)
    lateFees = serializers.CharField(required=False)
    device_id = serializers.CharField(required=False)
    class Meta:
        model = ReportIncident
        fields = '__all__'
    
    def validate(self, attrs):
        # user = attrs.get('user', None)
        about = attrs.get('about', None)
        description = attrs.get('description', None)
        transaction_id = attrs.get('transaction_id', None)
        # device_id = attrs.get('device_id', None)
        
        if about is None:
            raise serializers.ValidationError("About is Required")
        
        if description is None:
            raise serializers.ValidationError("description is Required")
        
        if transaction_id is None:
            raise serializers.ValidationError("Transaction ID is Required")
        
        # if device_id is None:
        #     raise serializers.ValidationError("Device ID is Required")
        
        
        return super().validate(attrs)



class NDRTaxSerializer(serializers.ModelSerializer):
    class Meta:
        model = NDR_Taxes
        fields = '__all__'

class CreateOrderSerializer(serializers.ModelSerializer):
    request_inbox_id = serializers.CharField(required=False)
    lender_id = serializers.CharField(required=False)
    product_id = serializers.CharField(required=False)
    amount = serializers.CharField(required=False)
    payment_status = serializers.CharField(required=False)
    payment_id = serializers.CharField(required=False)
    class Meta:
        model = OrderDetails
        fields = ['request_inbox_id','lender_id','product_id','amount','payment_status','payment_id']



class ViewRenterOrderSerializer(serializers.ModelSerializer):
    lender = UserSerializer(read_only = True)
    product = ProductViewSerializer(read_only=True)
    amount = serializers.CharField(required=False)
    payment_status = serializers.CharField(required=False)
    payment_id = serializers.CharField(required=False)
    date_of_payment = serializers.CharField(required=False)
    pickup_status = serializers.CharField(required=False)
    return_status = serializers.CharField(required=False)
    from_date = serializers.CharField(source='request_inbox.from_date')
    to_date = serializers.CharField(source='request_inbox.to_date')
    class Meta:
        model = OrderDetails
        fields = '__all__'
        
class ViewTransactionSerializer(serializers.ModelSerializer):
    renter = UserSerializer(read_only = True)
    product = ProductViewSerializer(read_only=True)
    amount = serializers.CharField(required=False)
    payment_status = serializers.CharField(required=False)
    payment_id = serializers.CharField(required=False)
    date_of_payment = serializers.CharField(required=False)
    class Meta:
        model = OrderDetails
        fields = '__all__'



from products.utils import Util
class ReferralSerializer(serializers.ModelSerializer):
    referrar = serializers.EmailField() # email of referal

    class Meta:
        model = Referral
        fields = ['referrar', 'referrered']

    def validate(self, attrs):
        reffered_by = self.context.get('referrered')
        print('reffered_by ', reffered_by)
        referal_code = self.context.get('referal_code')
        print('referal_code ', referal_code)
        refered_to = attrs.get('referrar')
        print('refered_to ', refered_to)
        if User.objects.filter(email=str(refered_to)).exists():
            raise serializers.ValidationError('Already Registered User')
        else:
            # Send EMail
            download_link = "___app_download_link____________"

            body = 'Click below link to download our app:'+'\n'+download_link+'\n'+'referral code: '+referal_code

            # data = {'email_body': body, 'to_email': str(refered_to), 'from_email':str(reffered_by),
            #         'email_subject': 'Referral Code.'}

            data = {
               'subject':'Referral Code.',
               'body':body,
               'to_email':str(refered_to)
            } 

            Util.send_email(data)

            return attrs


# By Anand
class PickupSerailizer(serializers.ModelSerializer):
    order_id = serializers.CharField(required=False)
    product_id = serializers.CharField(required=False)
    lender_id = serializers.CharField(required=False)
    total_amount = serializers.CharField(required=False)
    status_of_payment = serializers.CharField(required=False)
    renter_pickup_img = serializers.FileField(required=False)
    class Meta:
        model = ProductPickUpReturn
        fields = ['order_id','product_id','total_amount','status_of_payment','lender_id','renter_pickup_img']

class ReturnSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductPickUpReturn
        fields = ['product_img']

# By Anand 
class LenderReviewsSerializer(serializers.ModelSerializer):
    lender = serializers.CharField(required=False)
    renter = serializers.CharField(required=False)
    rating = serializers.CharField(required=False)
    review = serializers.CharField(required=False)
    lender = UserSerializer(read_only=True)
    user = UserSerializer(read_only=True)
    class Meta:
        model = LenderReviews
        fields = '__all__'


    def validate(self, attrs):
        lender = attrs.get('lender', None)
        renter = attrs.get('renter', None)
        rating = attrs.get('rating', None)
        about_lender = attrs.get('about_lender', None)
        if lender is None:
            raise serializers.ValidationError("Lender is Required")
        
        if renter is None:
            raise serializers.ValidationError("Renter is Required")
        
        # if product is None:
        #     raise serializers.ValidationError("Product is Required")

        if rating is None:
            raise serializers.ValidationError("Rating is Required")

        if about_lender is None:
            raise serializers.ValidationError("Write Something About the Lender")
        
        return super().validate(attrs)

    def create(self, validated_data):
        lender_review = LenderReviews.objects.create(**validated_data)
        return lender_review
    
class RenterSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only = True)
    renter = UserSerializer(read_only = True)
    class Meta:
        model = RenterReviews
        fields = '__all__'

# By Anand 
class ProductReviewsSerializer(serializers.ModelSerializer):
    product = serializers.CharField(required=False)
    renter = serializers.CharField(required=False)
    rating = serializers.CharField(required=False)
    about_product = serializers.CharField(required=False)
    renter = UserSerializer(read_only=True)

    class Meta:
        model = ProductReviews
        fields = '__all__'

    def validate(self, attrs):
        product = attrs.get('product', None)
        renter = attrs.get('renter', None)
        rating = attrs.get('rating', None)
        about_product = attrs.get('about_product', None)
        
        if renter is None:
            raise serializers.ValidationError("Renter is Required")
        
        if product is None:
            raise serializers.ValidationError("Product is Required")

        if rating is None:
            raise serializers.ValidationError("Rating is Required")

        if about_product is None:
            raise serializers.ValidationError("Write Something about the Product")
        
        return super().validate(attrs)

    def create(self, validated_data):
        product_review = ProductReviews.objects.create(**validated_data)
        return product_review
        
# By Anand
class ViewPickupReturnSerializer(serializers.ModelSerializer):
    order = ViewRenterOrderSerializer(read_only=True)
    renter =UserSerializer()

    class Meta:
        model = ProductPickUpReturn()
        fields = '__all__'

class SubscriptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = subscription()
        fields = '__all__'
    
class FAQsSerializer(serializers.ModelSerializer):
    class Meta:
        model = NDR_FAQs
        fields = '__all__'