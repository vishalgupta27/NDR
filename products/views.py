from rest_framework.permissions import IsAuthenticated, AllowAny
from next_door_backend.settings import FCM_DJANGO_SETTINGS  
from django.core.mail import EmailMultiAlternatives
from rest_framework import generics, permissions
from math import sin, cos, sqrt, atan2, radians
from django.core.files.base import ContentFile
from rest_framework.response import Response
from .models import Products, Product_Images
from rest_framework.views import APIView
from django.db.models import Count, Avg
from rest_framework import serializers
from accounts.utils import generate_qr
from django.core.mail import send_mail
from django.http import JsonResponse 
from rest_framework.parsers import *
from django.shortcuts import render
from accounts.serializers import *
from login_portal.models import *
from pyfcm import FCMNotification
from rest_framework import status
from django.conf import settings
from django.db.models import Q
from .serializers import *
import geopy.distance
from .helpers import *
import stripe
# Create your views here.

class AddProductView(generics.GenericAPIView):
    serializer_class = ProductRegister_Serializer
    permission_classes = [IsAuthenticated, ]
    parser_classes = (MultiPartParser, FormParser)
    def post(self, request):
        #request.data.update({"QrCode_Account_id": request})
        category = request.data['Category']
        cattst, created = ProductCategory.objects.get_or_create(category = category)
        serializer = self.get_serializer(data=request.data)
        if (serializer.is_valid()):
            product = serializer.save()
            product.Category_id = cattst.category_id
            # product.QrCode_Account_id is a foreign key attribute
            product.QrCode_Account_id = request.user.account_id
            qr_payload = {
                'product ID': product.Products_id,
                'Product Name': product.ProductName,
                # 'Category': product.Category,
                # 'Lender name': request.user.Name_First + ' ' + request.user.Name_Last,
                # 'Lender number': request.user.phone_number
            }

            generated_qr_image = generate_qr(qr_payload, 'user/tmp/{}.png'.format(product.Products_id))
            product.QrCode_Product.save('{}.jpg'.format(product.Products_id), ContentFile(generated_qr_image))
            product.save()
            print(Products.objects.get(Products_id=product.Products_id))

            # https://stackoverflow.com/questions/52903232/how-to-upload-multiple-images-using-django-rest-framework
            images = dict((request.data).lists())['Product_Image']
            # print("***************product",product)

            for each_image in images:
                print(each_image)
                product_image = Product_Images(Product_Image=each_image)
                product_image.product_id_id = product.Products_id
                product_image.QrCode_Product_id = product.Products_id
                product_image.save()

            unavailabilityDate = dict((request.data).lists())['unavailabilityDate']
            if not unavailabilityDate == ['36028797018963968']:
                print(unavailabilityDate)
                for each_unavailabilityDate in unavailabilityDate:
                    product_unavailabilityDate = UnavailabilityDate(unavailabilityDate=each_unavailabilityDate)
                    product_unavailabilityDate.product_id = product.Products_id
                    product_unavailabilityDate.save()

            # product_category = dict((request.data))['Category']
            # for each_product_category in product_category:
            #     if not ProductCategory.objects.filter(category=each_product_category):
            #         prod_category = ProductCategory(category=each_product_category)
            #         prod_category.save()
            #     return Response({
            #         "status": 403,
            #         "success": False,
            #         "message": "Category already exist. Please select !"})
                    
            return Response({
                "status": 200,
                "success": True,
                "message": "Product Inserted"})

        error_field = [i for i in serializer.errors.keys()][0]
        message = serializer.errors[error_field][0].title()

        # print(message)

        return Response({
            "status": 200,
            "success": False,
            "message": message})


class ViewAllMyProductView(APIView):
    permission_classes = [IsAuthenticated, ]
    print(permission_classes)
    serializer_class = ProductViewSerializer

    def get(self, request):
        try:
            products = Products.objects.filter(QrCode_Account_id=request.user.account_id)
            list = []
            for i in products:
                Products_id = i.Products_id
                QrCode_Account_id = i.QrCode_Account_id
                prodAvgRatings = lender_and_product_avg(Products_id, QrCode_Account_id)
                combined = {
                    **ProductViewSerializer(i).data,
                    # **ProductImageSerializer(Product_Images.objects.filter(product_id_id=i.Products_id).first()).data,
                    **prodAvgRatings,
                    # **UnavailabiltyDateSerializer(UnavailabilityDate.objects.filter(product_id = i.Products_id).first()).data
                }
                list.append(combined)
            # print('****************',list)

            return Response({
                "products": list,
                # "unavailability_date" : unavailability_date,
                "status": 200,
                "success": True,
                "message": "list of all products"})

        except Exception as e:
            return Response({
                "status": 200,
                "success": False,
                "message": str(e)
                })

    def put(self, request, *args, **kwargs):
        try:
            #product = Products.objects.filter(QrCode_Account_id=request.user.account_id)
            # print(request.data)

            product_id_param = request.query_params.get('product_id', None)

            if product_id_param is None:
                raise Exception("Product provide product parameter")

            if Products.objects.filter(Products_id=product_id_param, QrCode_Account_id=request.user.account_id).exists() is not True:
                raise Exception("Product doesn't exist")

            # instead of .filter, .get can also be used
            product = Products.objects.filter(
                Products_id=product_id_param, QrCode_Account_id=request.user.account_id).first()

            print('***', product)

            serializer = self.serializer_class(
                product, data=request.data, partial=True)
            serializer.is_valid(raise_exception=True)
            serializer.save()

            return Response({'updated': serializer.data,
                             'success': True,
                             'status': status.HTTP_200_OK,
                             'message': "successfully updated"})

        except Exception as e:
            return Response({
                "status": 200,
                "success": False,
                "message": str(e)})

    def delete(self, request, *args, **kwargs):

        try:
            product_id_param = request.query_params.get('product_id', None)

            if product_id_param is None:
                raise Exception("Product provide product parameter")

            if Products.objects.filter(Products_id=product_id_param, QrCode_Account_id=request.user.account_id).exists() is not True:
                raise Exception("Product doesn't exist")

            Products.objects.get(Products_id=product_id_param,
                                 QrCode_Account_id=request.user.account_id).delete()

            return Response({
                "message": "Deleted Product Successfully",
                "status": 200,
                "success": True})

        except Exception as e:
            return Response({
                "status": 200,
                "success": False,
                "message": str(e)})

# By Anand
class ProductUnavailabiltyDate(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request):
        try:
            pID = request.query_params.get('product_id', None)
            unavailability_date = UnavailabilityDate.objects.filter(
                product_id=pID)
            print(unavailability_date)
            PSerializer = UnavailabiltyDateSerializer(
                unavailability_date, many=True)
            return Response({
                'unavailibilty_date': PSerializer.data,
                "status": 200,
                "success": True,
                "message": "Product Unavailability date!"
            })
        except Exception as e:
            return Response({
                "status": 403,
                "success": False,
                "message": str(e)
            })

    def put(self, request):
        try:
            UNDate = request.query_params.get('unavailabilty_id', None)
            print(UNDate)
            UN_Date_obj = UnavailabilityDate.objects.get(id=UNDate)
            UNSerializer = UnavailabiltyDateSerializer(
                UN_Date_obj, data=request.data, partial=True)
            if UNSerializer.is_valid():
                UNSerializer.save()
                return Response({
                    "status": 200,
                    "success": True,
                    "Message": "Updated Successfully!"
                })
            return Response({
                "status": 403,
                "success": False,
                "Message": "Something went wrong"
            })
        except Exception as e:
            return Response({
                "status": 403,
                "success": False,
                "Message": str(e)
            })


class ViewAllProductView(APIView):
    permission_classes = [IsAuthenticated,]
    def get(self, request):
        try:
            
            user_verified = User.objects.filter(is_verified = True)
            if not user_verified:
                return Response({
                    "products":user_verified ,
                    "status": 200,
                    "success": True,
                    "message": "All Products",
                })
            product_obj = Products.objects.exclude(QrCode_Account_id=request.user.account_id)
            for x in product_obj:
                products_lat_long = (x.Product_long, x.Product_lat)
                user_let_long = (request.user.user_long, request.user.user_lat)
                distance = geopy.distance.geodesic(products_lat_long, user_let_long).km
                product = Products.objects.get(Products_id = x.Products_id)
                product.distance = distance=round(distance, 4)
                product.save()
            list = []
            # products = Products.objects.filter(distance__lte=10000).exclude(QrCode_Account_id=request.user.account_id)
            for x in user_verified:
                products = Products.objects.filter(QrCode_Account_id = x.account_id).exclude(QrCode_Account_id=request.user.account_id)
                for i in products:
                    Products_id = i.Products_id
                    QrCode_Account_id = i.QrCode_Account_id
                    prodAvgRatings = lender_and_product_avg(Products_id, QrCode_Account_id)
                    if Wishlist.objects.filter(user_id=request.user.account_id, product_id=i.Products_id):
                        prod_obj = Products.objects.get(Products_id=i.Products_id)
                        prod_obj.is_wishlist = True
                        prod_obj.save()
                    else:
                        prod_obj = Products.objects.get(Products_id=i.Products_id)
                        prod_obj.is_wishlist = False
                        prod_obj.save()
                    combined = {
                        **ProductViewSerializer(i).data,
                        **prodAvgRatings,
                    }
                    list.append(combined)
            return Response({
                "products": list,
                "status": 200,
                "success": True,
                "message": "All Products",
            })

        except Exception as e:
            return Response({
                "status": 200,
                "success": False,
                "message": "All Products",
                "message": str(e)})


class TestRelationsView(APIView):
    permission_classes = [IsAuthenticated, ]
    def get(self, request):

        try:
            print(dir(request.user))
            print('++', dir(request.user.products_set.all()))
            print('**', request.user.products_set.all())

            for each_product in request.user.products_set.all():
                print(each_product.Products_id,
                      each_product.product_id.all().query)
                print(request.user.products_set.all().query)
                print(request.user.products_set.all().query, Product_Images.objects.select_related(
                    'product_id', 'QrCode_Account').all().query)

            return Response({
                "products": None,
                "status": 200,
                "success": True})

        except Exception as e:
            return Response({
                "status": 200,
                "success": False,
                "message": str(e)})


class ProductImage(APIView):
    permission_classes = [IsAuthenticated, ]
    print(permission_classes)

    def get(self, request, *args, **kwargs):
        try:
            product_id = request.query_params.get('product_id', None)
            print('product_id', product_id)
            product_images_qs = Product_Images.objects.filter(QrCode_Product_id=product_id)
            print(product_images_qs)
            #product_images_qs = ProductImageSerializer(Product_Images.objects.filter(product_id_id=i.Products_id).first()).data
            product_images_qs = [ProductImageSerializer(
                each_image).data for each_image in product_images_qs]

            return Response({
                "message": product_images_qs,
                "status": 200,
                "success": True})

        except Exception as e:
            return Response({
                "status": 200,
                "success": False,
                "message": str(e)})

    def put(self, request, *args, **kwargs):

        try:
            image_id = request.query_params.get('image_id', None)
            print('image_id', image_id)
            image_obj = Product_Images.objects.get(id=image_id)
            serializer = ProductImageSerializer(image_obj, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
            return Response({
                "message": serializer.data,
                "status": 200,
                "success": True})

        except Exception as e:
            return Response({
                "status": 200,
                "success": False,
                "message": str(e)})

    def delete(self, request,  *args, **kwargs):

        try:
            image_id = request.query_params.get('image_id', None)
            print('image_id', image_id)

            Product_Images.objects.get(id=image_id).delete()

            return Response({
                "message": "image Deleted",
                "status": 200,
                "success": True})

        except Exception as e:
            return Response({
                "status": 200,
                "success": False,
                "message": str(e)})

    def post(self, request, *args, **kwargs):
        # https://stackoverflow.com/questions/52903232/how-to-upload-multiple-images-using-django-rest-framework

        try:
            Products_id = request.query_params.get('product_id', None)

            if Products_id is None:
                raise Exception(" please add image of your product")

            print('Products_id', Products_id)
            images = dict((request.data).lists())['Product_Image']

            for each_image in images:
                print(each_image)
                product_image = Product_Images(Product_Image=each_image)
                product_image.product_id_id = Products_id
                product_image.QrCode_Product_id = Products_id
                product_image.save()

            return Response({
                "message": "image Added",
                "status": 200,
                "success": True})

        except Exception as e:
            return Response({
                "status": 200,
                "success": False,
                "message": str(e)})


class Product_Explore(APIView):
    permission_classes = [IsAuthenticated, ]
    print(permission_classes)

    def get(self, request, *args, **kwargs):

        try:
            product_id = request.query_params.get("product_id", None)
            prod_details = Products.objects.get(Products_id=product_id)
            prod_img = Product_Images.objects.filter(product_id=product_id)
            img_serializer = ProductImageSerializer(prod_img, many=True)
            serializer = ProductViewSerializer(prod_details)
            user = User.objects.get(account_id=prod_details.QrCode_Account_id)
            user_serializer = UserSerializer(user)
            user_product = Products.objects.filter(QrCode_Account=user)
            product_count = user_product.count()
            unavail_date = UnavailabilityDate.objects.filter(
                product_id=product_id)
            SUnavail_Date = UnavailabiltyDateSerializer(
                unavail_date, many=True)
            return Response({
                "product Details": serializer.data,
                "product Image": img_serializer.data,
                "user_data": user_serializer.data,
                "unavailibilty_date": SUnavail_Date.data,
                "lander_products": product_count,
                "status": 200,
                "success": True,
            })

        except Exception as e:
            return Response({
                "status": 403,
                "success": False,
                "message": str(e)
            })

# By Anand
class ViewMyWishlist(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            my_wishlist = Wishlist.objects.filter(user_id=request.user.account_id)
            list=[]
            for i in my_wishlist:
                Products_id = i.product.Products_id
                QrCode_Account_id = i.product.QrCode_Account
                prodAvgRatings = lender_and_product_avg(Products_id, QrCode_Account_id)
                combined = {
                    **ProductWishlistSerializer(i).data,
                    **prodAvgRatings
                }
                list.append(combined)
            return Response({
                'wishlist': list,
                'success': True
            })
        except Exception as e:
            return Response({
                "status": 200,
                "success": False,
                "message": str(e)
            })


# By Anand
class UserWishlist(APIView):
    permission_classes = [IsAuthenticated]
    serializer_class = WishlistSerializer
    def post(self, request):
        try:
            user_wishlist = WishlistSerializer(data=request.data)
            # print(user_wishlist)
            product_id = request.data.get('product_id')
            if user_wishlist.is_valid():
                print("data is fully Validated")
                if Wishlist.objects.filter(user_id=request.user.account_id, product_id=product_id).first():
                    return Response({
                        "status": 200,
                        "success": False,
                        "message": "Already Added in Your Wishlist!"
                    })
                user_obj = user_wishlist.save()
                user_obj.user_id = request.user.account_id
                user_obj.save()
                return Response({
                    "message": "Added To Wishlist Successfully",
                    "status": 200,
                    "success": True
                })

            print(user_wishlist.errors)
            error_field = [i for i in user_wishlist.errors.keys()][0]
            message = user_wishlist.errors[error_field][0].title()
            return Response({
                "status": 200,
                "success": False,
                "message": message})
        except Exception as e:
            print(e)
            return Response({
                "status": 200,
                "success": False,
                "message": str(e)
            })

    def delete(self, request):
        try:
            product_id = request.data.get('product_id')
            if product_id is not None:
                Wishlist.objects.get(user_id=request.user.account_id, product_id=product_id).delete()
                product_obj = Products.objects.get(Products_id=product_id)
                product_obj.is_wishlist = False
                product_obj.save()
                return Response({
                    "status": 200,
                    "success": True,
                    "message": "Product Removed from Your Wishlist!"
                })
            return Response({
                "status": 403,
                "success": False,
                "message": "Enter Valid Product Id!!"
            })
        except Exception as e:
            print(e)
            return Response({
                "status": 200,
                "success": False,
                "message": str(e)
            })


# By Anand
class ProductCategoryView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            category = ProductCategory.objects.all().order_by('category')
            if category:
                serializer = ProductCategorySerialzer(category, many=True)
                return Response({
                    "category": serializer.data,
                    "status": 200,
                    "success": True,
                    "message": "Awesome!"
                })
            else:
                return Response({
                    "status": 403,
                    "success": False,
                    "message": "No Category Found!"
                })

        except Exception as e:
            return Response({
                "status": 200,
                "success": False,
                "message": str(e)
            })

    def post(self, request):
        try:
            return Response({
                "status": 200,
                "success": True,
                "message": "Category Created Successfully!"
            })
        except Exception as e:
            return Response({
                "status": 200,
                "success": False,
                "message": str(e)
            })

    def put(self, request):
        try:
            return Response({
                "status": 200,
                "success": True,
                "message": "Updated Successfully!"
            })
        except Exception as e:
            return Response({
                "status": 200,
                "success": False,
                "message": str(e)
            })


# https://stackoverflow.com/questions/58153698/multi-searching-django

# Product filter API Deepak
class ProductFilterView(APIView):
    permission_classes = [IsAuthenticated, ]
    print(permission_classes)

    def get(self, request):
        try:
            products_query_set = Products.objects.all()
            address_table_filters = ["city"]
            account_table_filters = ["AccountType"]
            user_table_filters = ["email", "Name_First"]
            product_table_filters = ["Category", "ProductName__icontains", "availability_date"]

            def filterByKey(keys, data): return {x: data[x] for x in keys if x in data.keys()}
            account_table_filters_dict = filterByKey(account_table_filters, request.query_params.dict())
            address_table_filters_dict = filterByKey(address_table_filters, request.query_params.dict())
            user_table_filters_dict = filterByKey(user_table_filters, request.query_params.dict())
            product_table_filters_dict = filterByKey(product_table_filters, request.query_params.dict())

            print(product_table_filters_dict, "jdghghgdshgdshgd")

            if len(account_table_filters_dict) != 0:

                account_table_filters_dict['AccountType__icontains'] = account_table_filters_dict['AccountType']

                del account_table_filters_dict['AccountType']

                acc_obj = Account_type.objects.get(**account_table_filters_dict)

                user_table_filters_dict['UserAccountType'] = acc_obj

            if len(address_table_filters_dict) != 0:

                address_table_filters_dict['Address_City__icontains'] = address_table_filters_dict['city']

                del address_table_filters_dict['city']

                add_obj = Address.objects.filter(**address_table_filters_dict)

                address_query_set = [str(each_qs.QrCode_Account_id)for each_qs in add_obj]

                print(address_query_set)

                user_table_filters_dict['account_id__in'] = address_query_set

                print(user_table_filters_dict)

            if len(user_table_filters_dict) != 0:
                products_query_set = User.objects.filter(**user_table_filters_dict)
                print(products_query_set, user_table_filters_dict)

            if len(product_table_filters_dict) != 0:

                print(len(products_query_set))

                if len(user_table_filters_dict) != 0:

                    products_query_set = [each_lender_in.my_products.all() for each_lender_in in products_query_set]
                    print('98989898',products_query_set,products_query_set[0])
                    products_query_set = products_query_set[0]
                    products_query_set = products_query_set.filter(**product_table_filters_dict)
                    Pserializer = ProductViewSerializer(products_query_set, many=True)
                    print(Pserializer.data)
                    my_list = [i for i in Pserializer.data]

                else:
                    products_query_set = Products.objects.filter(**product_table_filters_dict)

                    Pserializer = ProductViewSerializer(products_query_set, many=True)
                    # print(Pserializer.data)
                    my_list = [i for i in Pserializer.data]

            else:

                print(len(products_query_set))
                #products_query_set = [each_products.my_products.all() for each_products in products_query_set if len(each_products.my_products.all())>0]

                products_query_set = [
                    each_products for each_products in Products.objects.all()]

                print('products_query_set', products_query_set)

                Pserializer = ProductViewSerializer(products_query_set, many=True)
                # print(Pserializer.data)
                my_list = [i for i in Pserializer.data]
            print(products_query_set)

            return Response({
                "status": 200,
                "success": "True",
                "message": "products as per filter",
                "products": my_list
            })

        except Exception as e:
            return Response({
                "status": 200,
                "success": "True",
                "message": str(e)
            })

# By Anand
class ProductsFilterView(APIView):
    permission_classes = [IsAuthenticated]
    def post(self, request):
        try:
            AccountType = request.data.get('AccountType')
            category = request.data.get('category')
            distance = request.data.get('distance')
            city = request.data.get('city')
            availability_date = request.data.get('availability_date')
            sortBy = request.data.get('sortBy')
            query = Q()
            list  = []
            if AccountType:
                query &= Q(QrCode_Account__UserAccountType__AccountType = AccountType)
            
            if category:
                query &= Q(Category__category = category)

            if distance:
                query &= Q(distance__range=[0, distance])

            if city:
                query &= Q(QrCode_Account__my_address__Address_City__icontains = city)

            if availability_date:
                query &= Q(product_availability_date__unavailabilityDate__icontains = availability_date)

            if sortBy =='lowToHigh':
                products = Products.objects.filter(query).exclude(QrCode_Account = request.user).exclude(QrCode_Account__is_verified = False).order_by('OneDay_BasePrice')
                if products:
                    for i in products:
                        Products_id = i.Products_id
                        QrCode_Account_id = i.QrCode_Account
                        prodAvgRatings = lender_and_product_avg(Products_id, QrCode_Account_id)
                        combined = {
                            **ProductViewSerializer(i).data,
                            **prodAvgRatings
                        }
                        list.append(combined)
                return Response({
                    "status": 200,
                    "success" : True,
                    "count" : len(list),
                    "filtered_products": list,
                })
            
            if sortBy =='highToLow':
                products = Products.objects.filter(query).exclude(QrCode_Account = request.user).exclude(QrCode_Account__is_verified = False).order_by('-OneDay_BasePrice')
                if products:
                    for i in products:
                        Products_id = i.Products_id
                        QrCode_Account_id = i.QrCode_Account
                        prodAvgRatings = lender_and_product_avg(Products_id, QrCode_Account_id)
                        combined = {
                            **ProductViewSerializer(i).data,
                            **prodAvgRatings
                        }
                        list.append(combined)
                return Response({
                    "status": 200,
                    "success" : True,
                    "count" : len(list),
                    "filtered_products": list,
                })
            products = Products.objects.filter(query).exclude(QrCode_Account = request.user).exclude(QrCode_Account__is_verified = False).order_by('-created_at')
            if products:
                for i in products:
                    Products_id = i.Products_id
                    QrCode_Account_id = i.QrCode_Account
                    prodAvgRatings = lender_and_product_avg(Products_id, QrCode_Account_id)
                    combined = {
                        **ProductViewSerializer(i).data,
                        **prodAvgRatings
                    }
                    list.append(combined)
            return Response({
                "status": 200,
                "success" : True,
                "count" : len(list),
                "filtered_products": list,
            })
    
        except Exception as e:
            return Response({
                "status" : 400,
                "success" : False,
                "message": str(e)
            })



class ProductsFilters(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request):
        try:
            filter_data = self.request.query_params
            category = filter_data.get('category', None)
            distance = filter_data.get('distance', None)

            list = []
            distance_list = []
            
            if category is not None:
                products = Products.objects.filter(Category= category)
                # ps = ProductViewSerializer(products, many=True).data
                list.append(products)

            if distance is not None:
                products = Products.objects.filter(distance__lte = int(distance))
                #ps = ProductViewSerializer(products, many=True).data
                distance_list.append(products)
            
            PS = ProductViewSerializer(products, many=True).data
            return Response({
                "products" : list,
                "status":200,
                "success" : True,
                "message": "Product as per Filters"
            })
            # for item in filter_data:
            #     products = Products.objects.filter()
        except Exception as e:
            return Response({
                "status" : 403,
                "success": False,
                "message": str(e)
            })



# By Anand
class FilterSort(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            all_product = Products.objects.all()
            my_list1 = []
            print("My List54444444444444444444444444444444444444444444444444", my_list1)
            sort_by = request.query_params.get("sort")
            sort_item = request.query_params.get('OneDay_BasePrice')
            print(sort_item)

            if sort_by is not None:
                if sort_by == 'ascending':
                    product = Products.objects.order_by('product_initial_cost')
                    PSerializer = ProductViewSerializer(product, many=True)
                    my_list = [i for i in PSerializer.data]

                elif sort_by == 'descending':
                    product = Products.objects.order_by(
                        '-product_initial_cost')
                    PSerializer = ProductViewSerializer(product, many=True)
                    my_list = [i for i in PSerializer.data]
                    print("Descending Order", my_list)

                elif sort_by == 'arrival':
                    product = Products.objects.all().exclude(QrCode_Account = request.user).order_by('-created_at')
                    PSerializer = ProductViewSerializer(product, many=True)
                    my_list = [i for i in PSerializer.data]

                return Response({
                    "products": my_list,
                    "status": 200,
                    "success": True,
                    "message": "Sorted Product"
                })
            else:
                product_query_set = Products.objects.all()
                PSerializer = ProductViewSerializer(
                    product_query_set, many=True)
                my_list = [i for i in PSerializer.data]
                return Response({
                    "statuc": 200,
                    "success": False,
                    "message": "Product Without Sorting!",
                    "products": my_list
                })
        except Exception as e:
            return Response({
                "status": 403,
                "success": False,
                "message": str(e)
            })


# By Anand
class LenderRatingView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            rating_data = request.data
            LSerializer = LenderReviewsSerializer(data=rating_data)
            if LSerializer.is_valid():
                lender_obj = LSerializer.save()
                lender_obj.renter_id = request.user.account_id
                lender_obj.save()
                return Response({
                    "status": 200,
                    "success": True,
                    "message": "Thanks"
                })
            else:
                error_field = [i for i in LSerializer.errors.keys()][0]
                message = LSerializer.errors[error_field][0].title()
                return Response({
                    "status": 200,
                    "success": False,
                    "message": message
                })
        except Exception as e:
            return Response({
                "status": 403,
                "success": False,
                "message": str(e)
            })

    def get(self, request):
        try:
            lender_id = request.query_params.get('lender_id', None)
            # https://stackoverflow.com/questions/68255990/how-to-show-average-of-star-rating-in-django
            list = []
            if lender_id is not None:
                lender_rating = LenderReviews.objects.filter(lender_id=lender_id)
                lender_rate_avg = lender_rating.aggregate(lender_ratings=Avg('rating'))
                list.append(lender_rate_avg)
                rated_renter_count = lender_rating.aggregate(users_rated_to_the_lender=Count('user_id'))
                list.append(rated_renter_count)
                LSerializer = LenderReviewsSerializer(lender_rating, many=True)

            return Response({
                "lender_review": list,
                "review": LSerializer.data,
                "status": 200,
                "success": True,
                "message": "Lender Reviews"
            })

        except Exception as e:
            return Response({
                "status": 403,
                "success": False,
                "message": str(e)
            })
        
class MyProfileReviewView(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request):
        as_a_lender = LenderReviews.objects.filter(lender_id = request.user.account_id)
        as_a_lender_serialize = LenderReviewsSerializer(as_a_lender, many=True)
        as_a_renter = RenterReviews.objects.filter(renter_id = request.user.account_id)
        as_a_renter_serialize = RenterSerializer(as_a_renter, many=True)
        return Response({
            "as_a_lender": as_a_lender_serialize.data,
            "as_a_renter": as_a_renter_serialize.data,
            "status": 200,
            "success": True,
        })

# By Anand
class ProductRatingView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):  
        try:
            rating_data = request.data
            PSerializer = ProductReviewsSerializer(data=rating_data)
            if PSerializer.is_valid():
                product_obj = PSerializer.save()
                product_obj.renter_id = request.user.account_id
                product_obj.save()
                return Response({
                    "status": 200,
                    "success": True,
                    "message": "Thanks"
                })
            else:
                error_field = [i for i in PSerializer.errors.keys()][0]
                message = PSerializer.errors[error_field][0].title()
                return Response({
                    "status": 200,
                    "success": False,
                    "message": message
                })
        except Exception as e:
            return Response({
                "status": 403,
                "success": False,
                "message": str(e)
            })

    def get(self, request):
        try:
            product_id = request.query_params.get('product_id', None)
            # https://stackoverflow.com/questions/68255990/how-to-show-average-of-star-rating-in-django
            list = []
            if product_id is not None:
                product_rating = ProductReviews.objects.filter(product_id=product_id)
                rating_avg = product_rating.aggregate(product_ratings=Avg('rating'))
                list.append(rating_avg)
                renter_count = product_rating.aggregate(users_rated_to_the_product=Count('renter_id'))
                list.append(renter_count)
                PSerializer = ProductReviewsSerializer(product_rating, many=True).data
                
            return Response({
                "product_review": list,
                "review": PSerializer,
                "status": 200,
                "success": True,
                "message": "Product Reviews"
            })

        except Exception as e:
            return Response({
                "status": 403,
                "success": False,
                "message": str(e)
            })
from django.core.mail import EmailMessage
# By Anand
class ReportIncidentViews(APIView):
    permission_classes = [IsAuthenticated]
    def post(self, request):
        try:
            reported_data = request.data
            report_title = request.data.get('about')
            description = request.data.get('description')
            securityDeposit = request.data.get('securityDeposit')
            lateFees = request.data.get('lateFees')
            # transaction_id = request.data['transaction_id']
            file = request.FILES.get('photo')
            photo = request.FILES.get('document')
            first_name = request.user.Name_First
            email = request.user.email
            device_token_obj = UserDeviceToken.objects.get(user_id =  request.user.account_id)
            fcm_token = device_token_obj.device_id
            ReportSerializer = ReportIncidentSerializer(data=reported_data)
            if ReportSerializer.is_valid():
                user_obj = ReportSerializer.save()
                user_obj.user_id = request.user.account_id,
                user_obj.save()

                # Send Push Notification and Mail
                title = f"Regarding {report_title}!"
                message_body = "Thank you for helping to keep our community safe.  We will get back to you shortly."
                push_service = FCMNotification(api_key=FCM_DJANGO_SETTINGS['FCM_SERVER_KEY'])
                Notifications.objects.create(user_id = request.user.account_id,title=title, body=message_body, screen_name = "noReply")
                res = push_service.notify_single_device(
                    registration_id=fcm_token,
                    message_title=title, 
                    message_body=message_body
                    )
                subject = f"Regarding {report_title},"
                body = f"{description}"
                email_from = settings.EMAIL_HOST_USER
                to_email = ['support@nextdoorrental.ca', ]
                emailMess = EmailMessage(subject, body, email_from, to_email)
                attachment = [
                    file,
                    photo
                ]
                for x in attachment:
                    emailMess.attach('file.pdf', x.read(), 'application/pdf')
                emailMess.send()
            
                subject = f"Regarding {report_title},"
                html_content = f"Hi {first_name}, <br> <br> Thank you for helping to keep our community safe.  We will get back to you shortly."
                email_from = settings.EMAIL_HOST_USER
                recipient_list = [email, ]
                message = EmailMultiAlternatives(subject, html_content, email_from, recipient_list)
                # send_mail( subject, message, email_from, recipient_list ,"text/html")
                message.attach_alternative(html_content, "text/html")
                try:
                    message.send()
                except:
                    return Response({
                        "status": 403,
                        "success": False,
                        "message": "Unable to send mail."
                    })
                return Response({
                    "status": 200,
                    "success": True,
                    "message": "Your Report Sent Successfully!",
                    "res" : res
                })
            else:
                error_field = [i for i in ReportSerializer.errors.keys()][0]
                message = ReportSerializer.errors[error_field][0].title()
                return Response({
                    "status": 200,
                    "success": False,
                    "message": message
                })
        except Exception as e:
            return Response({
                "status": 403,
                "success": False,
                "message": str(e)

            })

# By Anand
class SendRequestInboxView(APIView):
    permission_classes = [IsAuthenticated]
    def post(self, request):
        try:
            lender_id = request.data.get('lender_id')
            product_id = request.data.get('product_id')
            from_date = request.data.get('from_date')
            to_date = request.data.get('to_date')
            price = request.data.get('price')
            lenderDetails = User.objects.get(account_id = lender_id)
            lenderName = lenderDetails.Name_First
            email = lenderDetails.email
            productDetails = Products.objects.get(Products_id = product_id)
            productName = productDetails.ProductName
            serialize_data = RequestInboxSerializer(data=request.data)
            if serialize_data.is_valid():
                get_data = serialize_data.save()
                get_data.renter_id = request.user.account_id
                get_data.save()

                # Send Push Notification and Mail
                device_token_obj = UserDeviceToken.objects.get(user_id =  lender_id)
                fcm_token = device_token_obj.device_id
                title = f"You have received a new Request"
                message_body = f"Hey ! {lenderName} You have received a new request for product {productName} for the period {from_date} to {to_date} at total amount of C${price}."
                push_service = FCMNotification(api_key=FCM_DJANGO_SETTINGS['FCM_SERVER_KEY'])
                Notifications.objects.create(user_id = lender_id, title=title, body=message_body, screen_name = "requestInbox")
                res = push_service.notify_single_device(
                    registration_id=fcm_token,
                    message_title=title, 
                    message_body=message_body
                    )
                # send mail
                subject = f"You have received a new Request"
                html_content = f"Hey ! {lenderName} You have received a new request for product {productName} for the period {from_date} to {to_date} at total amount of C${price}."
                email_from = settings.EMAIL_HOST_USER
                recipient_list = [email, ]
                message = EmailMultiAlternatives(subject, html_content, email_from, recipient_list)
                # send_mail( subject, message, email_from, recipient_list ,"text/html")
                message.attach_alternative(html_content, "text/html")
                try:
                    message.send()
                except:
                    return Response({
                        "status": 403,
                        "success": False,
                        "message": "Unable to sent mail."
                    })
                return Response({
                    "status": 200,
                    "success": True,
                    "push_notification_res": res,
                    "message": "Request has been Sent Successfully"
                })
            else:
                error_field = [i for i in serialize_data.errors.keys()][0]
                message = serialize_data.errors[error_field][0].title()

                return Response({
                    "status": 403,
                    "success": False,
                    "message": message
                })
        except Exception as e:
            return Response({
                "status": 403,
                "success": False,
                "message": str(e)
            })

# By Anand
class ViewAllRequestInboxView(APIView):
    def get(self, request):
        try:
            user_id = request.user.account_id
            if user_id is not None:
                get_queryset = RequestInbox.objects.filter(lender_id=user_id).exclude(request_status = "Rejected")
                count = RequestInbox.objects.filter(lender_id=user_id, isRead = False).count()
                serializer = ViewRequestInbox(get_queryset, many=True)
                return Response({
                    "status": 200,
                    "success": True,
                    "unreadCount": count,
                    "message": "Requested Data!",
                    "Request Inbox": serializer.data,
                })
            else:
                return Response({
                    "status": 200,
                    "success": False,
                    "message": "User Not Found!"
                })
        except Exception as e:
            return Response({
                "status": 403,
                "success": False,
                "message": str(e)
            })
    def post(self, request):
        try:
            requestInboxId = request.data.get('requestInboxId')
            requestinboxObj = RequestInbox.objects.get(id = requestInboxId)
            requestinboxObj.isRead = True
            requestinboxObj.save()
            return Response({
                "status": 200,
                "success": True,
                "message":"Read"
            })
        except Exception as e:
            return Response({
                "status": 403,
                "success": False,
                "message": str(e)
            })
    def put(self, request):
        try:
            inbox_id = request.query_params.get('request_inbox_id')
            inbox_obj = RequestInbox.objects.get(id=inbox_id)
            product_name = inbox_obj.product.ProductName
            model_number = inbox_obj.product.model_number
            make = inbox_obj.product.make
            price = inbox_obj.price
            from_date = inbox_obj.from_date
            to_date = inbox_obj.to_date
            email = inbox_obj.renter.email
            renter_name = inbox_obj.renter.Name_First
            renter_id = inbox_obj.renter.account_id
            lender_name = inbox_obj.lender.Name_First
            print("product name is", product_name, "price is", price, "email is",
                  email, "renter name", renter_name, "lender name", lender_name)
            serializer = RequestInboxSerializer(inbox_obj, data=request.data, partial=True)
            if serializer.is_valid(raise_exception=True):
                get_data = serializer.save()

                # Send Push Notification and Mail
                device_token_obj = UserDeviceToken.objects.get(user_id =  renter_id)
                fcm_token = device_token_obj.device_id

                title = f"Request that has been {get_data.request_status}"
                message_body = f"Dear {renter_name}, Your rent request regarding product {product_name} {model_number} {make}  for the period {from_date} to {to_date} at total amount of C${price} has been {get_data.request_status} by {lender_name}. Go to App to pay the amount. Thanks for choosing Next Door Rental services"
                push_service = FCMNotification(api_key=FCM_DJANGO_SETTINGS['FCM_SERVER_KEY'])
                Notifications.objects.create(user_id = renter_id, title=title, body=message_body, screen_name = "requestInbox")
                res = push_service.notify_single_device(
                    registration_id=fcm_token,
                    message_title=title, 
                    message_body=message_body
                    )
                # send mail
                subject = f"Request that has been {get_data.request_status}"
                html_content = f"Dear {renter_name}, <br> <br> Your rent request regarding product <b>{product_name}</b> <b>{model_number}</b> <b>{make}</b> for the period <b>{from_date}</b> to <b>{to_date}</b> at total amount of <b>C${price}</b> has been <b>{get_data.request_status}</b> by <b>{lender_name}</b>.<br> <br> Go to App to pay the amount.<br> <br>  Thanks for choosing <strong>Next Door Rental services.</strong>"
                email_from = settings.EMAIL_HOST_USER
                recipient_list = [email, ]
                message = EmailMultiAlternatives(subject, html_content, email_from, recipient_list)
                # send_mail( subject, message, email_from, recipient_list ,"text/html")
                message.attach_alternative(html_content, "text/html")
                try:
                    message.send()
                except:
                    return Response({
                        "status": 403,
                        "success": False,
                        "message": "Unable to send mail."
                    })
                return Response({
                    "status": 200,
                    "success": True,
                    "notificationSuccess": res,
                    "message": "Thanks!"
                })
            return Response({
                "status": 403,
                "success": False,
                "message": "Data is Not Validate!"
            })
        except Exception as e:
            return Response({
                "status": 403,
                "success": False,
                "message": str(e)
            })

# By Anand
class RenterRequestedProducts(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request):
        try:
            user_id = request.user.account_id
            print(user_id)
            if user_id is not None:
                get_queryset = RequestInbox.objects.filter(renter_id=user_id)
                serializer = ViewRenterInbox(get_queryset, many=True)
                return Response({
                    "Request Inbox": serializer.data,
                    "status": 200,
                    "success": True,
                    "message": "Requested Data!"
                })
            else:
                return Response({
                    "status": 200,
                    "success": False,
                    "message": "User Not Found!"
                })
        except Exception as e:

            return Response({
                "statuc": 403,
                "success": False,
                "message": str(e)
            })

# By Anand
class ViewLenderProducts(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            lender_id = request.query_params.get('lender_id')
            product_obj = Products.objects.filter(QrCode_Account_id=lender_id)
            print(product_obj)
            PSerializer = ProductViewSerializer(product_obj, many=True)
            return Response({
                'lender_products': PSerializer.data,
                'status': 200,
                'success': True,
                'message': "Lender Products"
            })
        except Exception as e:
            return Response({
                'status': 403,
                "success": False,
                "message": str(e)
            })

# By Anand
class NDRTaxViewAPI(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        tax_list = NDR_Taxes.objects.all()
        TaxSerializer = NDRTaxSerializer(tax_list, many=True)
        return Response({
            "ndr_tax": TaxSerializer.data,
            "status": 200,
            "success": True
        })



# By Anand
class CreateOrder(APIView):
    permission_classes = [IsAuthenticated]
    def post(self, request):
        try:
            serializer = CreateOrderSerializer(data=request.data)
            amount = float(request.data['amount'])
            # convert Doller into Points
            total_points = amount * 100
            # Calculate Reward Points
            points = int(total_points * float(1.5) / 100)
            inbox_obj = RequestInbox.objects.get(id =request.data['request_inbox_id'], product_id=request.data['product_id'])
            inbox_obj.payment_status = "Paid"
            inbox_obj.save()
            if serializer.is_valid():
                serializer_obj = serializer.save()
                serializer_obj.renter_id = request.user.account_id
                # serializer_obj.renter_id.reward_points += points
                serializer_obj.save()
                renter_obj = User.objects.get(account_id = request.user.account_id)
                if renter_obj:
                    avl_points = renter_obj.reward_points
                    if avl_points is None:
                        renter_obj.reward_points = float(points)
                        renter_obj.save()
                    renter_obj.reward_points = float(avl_points) + float(points)
                    renter_obj.save() 
                return Response({
                    "status": 200,
                    "success": True,
                    "message": "Order Created Successfully!!"
                })
            else:
                return Response({
                    "status": 403,
                    "success": False,
                    "message": "Something went wrong!"
                })
        except Exception as e:
            return Response({
                "status": 403,
                "success": False,
                "message": str(e)
            })

# By Anand
class RenterOrderView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            renter_order_details = OrderDetails.objects.filter(renter_id=request.user.account_id).order_by('-date_of_payment')
            RenterSerializer = ViewRenterOrderSerializer(renter_order_details, many=True).data
            return Response({
                "order_details": RenterSerializer,
                "status": 200,
                "success": True
            })
        except Exception as e:
            return Response({
                "status": 403,
                "success": False,
                "message": str(e)
            })


# By Anand
class TransactionView(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request):
        
        lender_transaction = OrderDetails.objects.filter(lender_id=request.user.account_id).order_by('-date_of_payment')
        LenderSerializer = ViewTransactionSerializer(lender_transaction, many=True)
        renter_transaction = OrderDetails.objects.filter(renter_id=request.user.account_id).order_by('-date_of_payment')
        renterSerializer = ViewRenterOrderSerializer(renter_transaction, many=True)
        return Response({
            "received": LenderSerializer.data,
            "paid": renterSerializer.data,
            "status": 200,
            "success": True
        })

class TransactionFilterView(APIView):
    def get(self, request):
        userType = request.query_params.get('userType', None)
        amountSort = request.query_params.get('amountSort', None)
        
        if userType:
            if userType == 'Renter':
                renterQueryset = OrderDetails.objects.filter(renter=request.user.account_id)
                renterSerialize = ViewRenterOrderSerializer(renterQueryset, many=True).data
                return Response({
                    "status": 200,
                    "success": True,
                    "paid": renterSerialize,
                })
            if userType == 'Lender':
                lenderQueryset = OrderDetails.objects.filter(lender=request.user.account_id)
                lenderSerialize = ViewTransactionSerializer(lenderQueryset, many=True).data
                return Response({
                    "status": 200,
                    "success": True,
                    "received": lenderSerialize,
                })
        
        if amountSort:
            renterQueryset = OrderDetails.objects.filter(renter=request.user)
            lenderQueryset = OrderDetails.objects.filter(lender=request.user)
            
            if amountSort == 'lowToHigh':
                renterQueryset = renterQueryset.order_by('amount')
                lenderQueryset = lenderQueryset.order_by('amount')
            elif amountSort == 'highToLow':
                renterQueryset = renterQueryset.order_by('-amount')
                lenderQueryset = lenderQueryset.order_by('-amount')
            
            lenderSerialize = ViewTransactionSerializer(lenderQueryset, many=True).data
            renterSerialize = ViewRenterOrderSerializer(renterQueryset, many=True).data
            
            return Response({
                "status": 200,
                "success": True,
                "received": lenderSerialize,
                "paid": renterSerialize,
            })

# By Anand
# Product Pickup By Renter GET POST API
class RenterPickupConfirmation(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request):
        try:
            renter_order_details = OrderDetails.objects.filter(renter_id=request.user.account_id).exclude(renter_pickup_status = True).order_by('-date_of_payment')
            RenterSerializer = ViewRenterOrderSerializer(renter_order_details, many=True).data
            return Response({
                "renter_pickup_product": RenterSerializer,
                "status": 200,
                "success": True
            })
        except Exception as e:
            return Response({
                "status": 403,
                "success": False,
                "message": str(e)
            })

    def post(self, request):
        try:
            get_pickUp_data = PickupSerailizer(data=request.data)
            order_id = request.data['order_id']
            pickupLocation = request.data.get('renterPickupLocation')
            userName = request.user.Name_First
            userId = request.user.account_id
            userEmail = request.user.email
            if get_pickUp_data.is_valid():
                pickup = get_pickUp_data.save()
                pickup.renter_pickup_status = True
                pickup.renter_pickup_location = pickupLocation
                pickup.renter_pickUp_date = datetime.datetime.now()
                pickup.renter_id = userId
                pickup.save()
                order_obj = OrderDetails.objects.get(id=order_id, renter_id=userId)
                order_obj.renter_pickup_status = True
                order_obj.save()
                productName = order_obj.product.ProductName

                # Send Push Notification and Mail
                device_token_obj = UserDeviceToken.objects.get(user_id =  userId)
                fcm_token = device_token_obj.device_id

                title = f"Order Pickup Confirmation"
                message_body = f"Dear {userName}, Thank you for picking up your product! We hope you enjoy it. Have a great day!"
                Notifications.objects.create(user_id = userId, title=title, body=message_body, screen_name = "orderPickup")
                send_push_notification(title, message_body,fcm_token)
                # send mail
                subject = f"Order Pickup Confirmation"
                html_content = f"Dear {userName}, <br> <br> We hope this email finds you well. We are delighted to inform you that your order has been successfully picked up from our location. We appreciate your business and would like to confirm the details of your pickup. <br> <br> Order Details: <br> Product Name: {productName} <br> Pickup Date: {datetime.datetime.now()} <br> Pickup Location: {pickupLocation}"
                send_email(subject, html_content, userEmail)
                return Response({
                    "status": 200,
                    "success": True,
                    "message": "Successfully product picked up from renter side!"
                })
            else:
                return Response({
                    "status": 200,
                    "success": False,
                    "message": "Something went wrong"
                })

        except Exception as e:
            return Response({
                "status": 400,
                "success": True,
                "message": str(e)
            })

# Anand
class RenterProductReturnView(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request):
        try:
            renter_return_product = ProductPickUpReturn.objects.filter(renter_id = request.user.account_id).exclude(renter_return_status = True).order_by('-renter_pickUp_date')
            return_serializer = ViewPickupReturnSerializer(renter_return_product, many=True).data
            return Response({
                "renter_return_product" : return_serializer,
                "status" : 200,
                "success" : True,
                "message" : "Renter Return Product",
            })
        except Exception as e:
            return Response({
                "status" : 403,
                "success" : False,
                "message" : str(e)
            })
    def post(self, request):
        try:
            product_id = request.data['product_id']
            lender_id = request.data['lender_id']
            productRating = request.data.get('productRating', None)
            lenderRating = request.data.get('lenderRating', None)
            aboutLender = request.data.get('aboutLender', None)
            pickUp_id = request.data['pickUp_id']
            order_id = request.data['order_id']
            about_product = request.data['about_product']
            returnLocation = request.data.get('renterReturnLocation')
            userId = request.user.account_id
            userName = request.user.Name_First
            userEmail = request.user.email
            obj = ProductPickUpReturn.objects.get(order_id=order_id, pickUp_id=pickUp_id)
            obj.renter_return_img = request.data["renter_return_img"]
            obj.renter_return_status = True
            obj.renter_return_location = returnLocation
            obj.renter_return_date = datetime.datetime.now()
            obj.save()
            order_obj = OrderDetails.objects.get(id=order_id)
            order_obj.renter_return_status = True
            order_obj.save()

            ProductReviews.objects.create(product_id=product_id, rating=productRating, about_product=about_product, renter_id=request.user.account_id)
            if lenderRating is None:
                return False
            LenderReviews.objects.create(lender_id=lender_id, rating=lenderRating,about_lender=aboutLender, user_id=request.user.account_id)

            device_token_obj = UserDeviceToken.objects.get(user_id =  userId)
            fcm_token = device_token_obj.device_id

            # Send Push Notification and Mail
            title = f"Order Return Confirmation"
            message_body = f"Dear {userName}, Thank you for returning your product! We hope you enjoy it. Have a great day!"
            Notifications.objects.create(user_id = userId, title=title, body=message_body, screen_name = "orderReturn")
            send_push_notification(title, message_body,fcm_token)

            # send mail
            subject = f"Order Return Confirmation"
            html_content = f"Dear {userName}, <br> <br> We hope this email finds you well. We are delighted to inform you that your order has been successfully return from our location."
            send_email(subject, html_content, userEmail)

            return Response({
                "status": 200,
                "success": True,
                "message": "Successfully product return from the renter side !"
            })
        except Exception as e:
            return Response({
                "status": 403,
                "success": False,
                "message": str(e)
            })


# Product Pickup By lender GET POST API
class LenderPickupConfirmation(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request):
        try:
            lender_pickup_products = ProductPickUpReturn.objects.filter(lender_id=request.user.account_id).exclude(lender_pickup_status = True).order_by('-renter_pickUp_date')
            LenderSerializer = ViewPickupReturnSerializer(lender_pickup_products, many=True).data
            return Response({
                "lender_pickup_product" : LenderSerializer,
                "status" : 200,
                "success" : True
            })
            
        except Exception as e:
            return Response({
                "status": 403,
                "success": False,
                "message": str(e)
            })

    def post(self, request):
        try:
            pickup_id = request.data['pickUp_id']
            img = request.data['lender_pickup_img']
            order_id = request.data['order_id']
            userId = request.user.account_id
            userName = request.user.Name_First
            userEmail = request.user.email
            if pickup_id:
                pickup_obj = ProductPickUpReturn.objects.get(pickUp_id = pickup_id)
                pickup_obj.lender_pickup_img  = img
                pickup_obj.lender_pickup_status  = True
                pickup_obj.lender_pickUp_date  = datetime.datetime.now()
                pickup_obj.final_pickup_status  = True
                pickup_obj.save()
                order_obj = OrderDetails.objects.get(id=order_id, lender_id=request.user.account_id)
                order_obj.lender_pickup_status = True
                order_obj.final_pickup_status = True
                order_obj.save()
                productName = order_obj.product.ProductName
                # Send Push Notification and Mail
                device_token_obj = UserDeviceToken.objects.get(user_id =  userId)
                fcm_token = device_token_obj.device_id

                title = f"Order Pickup Confirmation"
                message_body = f"Dear {userName}, We hope this notification finds you well. We are delighted to inform you that your order has been successfully picked up from our location."
                Notifications.objects.create(user_id = userId, title=title, body=message_body, screen_name = "orderPickup")
                send_push_notification(title, message_body,fcm_token)
                # send mail
                subject = f"Order Pickup Confirmation"
                html_content = f"Dear {userName}, <br> <br> We hope this email finds you well. We are delighted to inform you that your order has been successfully picked up from our location."
                send_email(subject, html_content, userEmail)
                return Response({
                    "status": 200,
                    "success": True,
                    "message": "Successfully product picked up from lender side!"
                })
            else:
                return Response({
                    "status": 200,
                    "success": False,
                    "message": "Something went wrong"
                })
            
        except Exception as e:
            return Response({
                "status": 400,
                "success": True,
                "message": str(e)
            })




class LenderProductReturnView(APIView):
    def get(self, request):
        try:
            lender_return_product = ProductPickUpReturn.objects.filter(lender_id = request.user.account_id).exclude(lender_return_status = True)
            return_serializer = ViewPickupReturnSerializer(lender_return_product, many=True).data
            return Response({
                "lender_return_product" : return_serializer,
                "status" : 200,
                "success" : True,
                "message" : "Lender Return Product",
            })
        except Exception as e:
            return Response({
                "status" : 403,
                "success" : False,
                "message" : str(e)
            })

    def post(self , request):
        try:
            pickup_id = request.data['pickUp_id']
            order_id = request.data['order_id']
            renterRating = request.data.get('renterRating', None)
            aboutRenter = request.data.get('aboutRenter', None)
            renter_id = request.data.get('renter_id', None)
            userId = request.user.account_id
            userName = request.user.Name_First
            userEmail = request.user.email
            lender_return_img = request.data['lender_return_img']
            return_obj = ProductPickUpReturn.objects.get(pickUp_id = pickup_id)
            return_obj.lender_return_img = lender_return_img
            return_obj.lender_return_status = True
            return_obj.final_return_status = True
            return_obj.lender_return_date = datetime.datetime.now()
            return_obj.save()
            order_obj = OrderDetails.objects.get(id=order_id)
            order_obj.lender_return_status = True
            order_obj.final_return_status = True
            order_obj.save()
            
            RenterReviews.objects.create(renter_id=renter_id, renterRating=renterRating, about_renter=aboutRenter, user_id=request.user.account_id)

            device_token_obj = UserDeviceToken.objects.get(user_id =  userId)
            fcm_token = device_token_obj.device_id

            # Send Push Notification and Mail
            title = f"Order Return Confirmation"
            message_body = f"Dear {userName}, Thank you for returning your product! We hope you enjoy it. Have a great day!"
            Notifications.objects.create(user_id = userId, title=title, body=message_body, screen_name = "orderReturn")
            send_push_notification(title, message_body,fcm_token)

            # send mail
            subject = f"Order Return Confirmation"
            html_content = f"Dear {userName}, <br> <br> We hope this email finds you well. We are delighted to inform you that your order has been successfully return from our location."
            send_email(subject, html_content, userEmail)
            return Response({
                "status": 200,
                "success":True,
                "message": "Successfully product return from the lender side"
            })
        except Exception as e:
            return Response({
                "status": 403,
                "success":False,
                "message": str(e)
            })

# By Anand
class GPSOnOffLatLong(APIView):
    permission_classes = [IsAuthenticated]
    def post(self, request):
        try:
            user_lat = request.data['user_lat']
            user_long = request.data['user_long']
            user = User.objects.get(account_id=request.user.account_id)
            user.user_lat = user_lat
            user.user_long = user_long
            user.save()
            return Response({
                "status": 200,
                "success": True,
                "message": "Locations Updated"
            })
        except Exception as e:
            return Response({
                "status": 403,
                "success": False,
                "message": str(e)
            })

# By Anand
class SubscriptionsView(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request):
        try:
            subs = subscription.objects.all()
            if not subs:
                return Response({
                "status" : 403,
                "success": False,
                "message": "No Data Found!"
            })
            SS = SubscriptionSerializer(subs, many=True).data
            return Response({
                "status": 200,
                "success": True,
                "subscriptions" : SS
            })
        except Exception as e:
            return Response({
                "status" : 403,
                "success": False,
                "message": str(e)
            })


class FAQsView(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request):
        try:
            faqs_list = NDR_FAQs.objects.all()
            FS = FAQsSerializer(faqs_list, many=True).data
            return Response({
                "status":200,
                "success":True,
                "faqs_list" : FS
            })
        except Exception as e:
            return Response({
                "status":403,
                "success": False,
                "message": str(e)
            })
