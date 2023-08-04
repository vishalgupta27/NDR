from django.shortcuts import render, HttpResponse, redirect
from .models import *
from django.views.decorators.csrf import csrf_exempt
from django.http.response import JsonResponse
from rest_framework.parsers import JSONParser
from chat.serializers import *
from accounts.models import User
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import generics, permissions
from rest_framework.permissions import IsAuthenticated, AllowAny
import json
import yaml
from accounts.serializers import UserSerializer


def getFriendsList(id):
    """
    Get the list of friends of the  user
    :param: user id
    :return: list of friends
    """
    try:
        user = User.objects.get(account_id=id)
        ids = list(user.friends_set.all())
        print(ids)
        friends = []
        for id in ids:
            id = str(id.friend_id)
            fr = User.objects.get(account_id=id)
            friends.append(fr.Name_First + fr.Name_Last)
        return friends
    except Exception as e:
        print(e)
        return []


def getUserId(email):
    """
    Get the user id by the username
    :param username:
    :return: int
    """
    use = User.objects.get(email=email)
    id = use.account_id
    return id


def index(request):
    """
    Return the home page
    :param request:
    :return:
    """
    if not request.user.is_authenticated:
        print("Not Logged In!")
        return render(request, "chat/index.html", {})
    else:
        username = request.user.username
        id = getUserId(username)
        friends = getFriendsList(id)
        return render(request, "chat/Base.html", {'friends': friends})


class SearchUserView(generics.GenericAPIView):
    # permission_classes = [IsAuthenticated, ]
    # print(permission_classes)
    # def get(self, request):
    def post(self, request):
        """
        Search users page
        :param request:
        :return:
        """
        users = list(User.objects.all())
        for user in users:
            if user.email == request.user.email:
                users.remove(user)
                break

        print("SEARCHING!!")
        query = request.query_params.get('Name_First')
        print(query)
        user_ls = []

        for user in users:
            print(user)
            if query in user.Name_First or query in user.Name_Last:
                user_ls.append(user.Name_First + ' ' + user.Name_Last)

        print('user_ls', user_ls)
        # return render(request, "chat/search.html", {'users': user_ls, })
        return Response({'users': user_ls})

    def get(self, request):
        users = list(User.objects.all())
        for user in users:
            if user.email == request.user.email:
                users.remove(user)
                break
        try:
            users = users[:10]
        except:
            users = users[:]
        id = getUserId(request.user.email)
        friends = getFriendsList(id)
        print(friends, id, users)
        # return Response ({'users': users[0].email, 'friends': friends})
        users = [each_user.Name_First + ' ' + each_user.Name_Last for each_user in users]

        return Response({'users': users, 'friends': friends})


# class AddFriendView(generics.GenericAPIView):
#    def get(self, request, *args, **kwargs):
#        """
#        Add a user to the friend's list
#        :param request:
#        :param name:
#        :return:
#        """
#        print(request.query_params.get('email'))
#        curr_user_email = request.user.email
#        id = getUserId(curr_user_email)
#        email = request.query_params.get('email')
#        friend = User.objects.get(email=email)
#        curr_user = User.objects.get(account_id=id)
#        print(curr_user.email)
#        ls = curr_user.my_friends.all()
#        flag = 0
#        for username in ls:
#            if username.friend == friend.account_id:
#                flag = 1
#                #break
#                return Response({
#                    "success": True,
#                    "message":"Please chat",
#                    "status" : 200
#                })
#
#        if flag == 0:
#            print("Friend Added!!")
#            curr_user.friends_set.create(friend_id=friend.account_id, user_id=curr_user.account_id)
# friend.objects.create(friend_id=curr_user.account_id, user_id=friend.account_id)

# return redirect("/search")
#            return Response({
#                "success": True,
#                "message": " friend added, Please chat",
#                "status": 200
#            })

class AddFriendView(generics.GenericAPIView):
    def get(self, request, *args, **kwargs):
        try:
            print(request.query_params.get('email'))
            curr_user_email = request.user.email
            id = getUserId(curr_user_email)
            email = request.query_params.get('email')
            friend = User.objects.get(email=email)
            curr_user = User.objects.get(account_id=id)
            print(curr_user.email)
            if friend.account_id == curr_user.account_id:
                raise Exception("operation not valid")
            # Friends.objects.filter(friend_id=friend.account_id, user_id=curr_user.account_id)
            flag = 0
            if Friends.objects.filter(friend_id=friend.account_id,
                                      user_id=curr_user.account_id).exists() and Friends.objects.filter(
                    friend_id=curr_user.account_id, user_id=friend.account_id).exists():
                flag = 1
                # break
                return Response({
                    "success": True,
                    "message": "Please chat",
                    "status": 200
                })

            if flag == 0:
                print("Friend Added!!")
                # if curr_user.friends_set.objects.filter(friend_id=friend.account_id, user_id=curr_user.account_id).exists() and
                #    friend.friends_set.objects.filter(friend_id=curr_user.account_id, user_id=friend.account_id).exists():
                print(curr_user.account_id, friend.account_id)
                curr_user.friends_set.create(friend_id=friend.account_id, user_id=curr_user.account_id)
                friend.friends_set.create(friend_id=curr_user.account_id, user_id=friend.account_id)

                return Response({
                    "success": True,
                    "message": " friend added, Please chat",
                    "status": 200
                })

        except Exception as e:
            return Response({
                "status": 200,
                "success": False,
                "message": str(e)
            })


class ShowFriendView(generics.GenericAPIView):
    def get(self, request, *args, **kwargs):
        myfrieldns = Friends.objects.filter(user_id=request.user.account_id)
        print(myfrieldns)
        frnd_ls = []
        for each_friend in myfrieldns:
            frnd_ls.append(UserSerializer(User.objects.get(account_id=each_friend.friend_id)).data)

        print(frnd_ls)

        return Response({
            "success": True,
            "message": "list of friends",
            'friends': frnd_ls,
            "status": 200
        })


# class ChatView(generics.GenericAPIView):
#    def get(self, request, *args, **kwargs):
#
#
#
#        """
#        Get the chat between two users.
#        :param request:
#        :param username:
#        :return:
#        """
#        email = request.query_params.get('email')
#        print(email)
#        friend = User.objects.get(email=email)
#        id = getUserId(request.user.email)
#        curr_user = User.objects.get(account_id=id)
#        messages = Messages.objects.filter(sender_name=id, receiver_name=friend.account_id) | Messages.objects.filter(sender_name=friend.account_id, receiver_name=id)
#
#        friends = getFriendsList(id)
#
#        print(messages,'\n',curr_user,'\n',friend,'\n')
#        print(type(messages), '\n', type(curr_user), '\n',type( friend), '\n')
#        serializer = MessageSerializer(messages, many=True, context={'request': request})
#        for message in messages:
#            message.seen = True
#            message.save()
#        return JsonResponse(serializer.data, safe=False)


class ChatView(generics.GenericAPIView):
    def get(self, request, *args, **kwargs):

        try:

            """
            Get the chat between two users.
            :param request:
            :param username:
            :return:
            """

            email = request.query_params.get('email')
            friend = User.objects.get(email=email)
            id = getUserId(request.user.email)
            curr_user = User.objects.get(account_id=id)
            print(curr_user.account_id, friend.account_id)
            if Friends.objects.filter(friend_id=friend.account_id,
                                      user_id=curr_user.account_id).exists() is False and Friends.objects.filter(
                friend_id=curr_user.account_id, user_id=friend.account_id).exists() is False:
                raise Exception("Not friends")

            messages = Messages.objects.filter(sender_name=id,
                                               receiver_name=friend.account_id) | Messages.objects.filter(
                sender_name=friend.account_id, receiver_name=id)
            msg_list = []
            for i in messages:
                msg_dict = {}
                print(MessageSerializer(i).data.keys())
                print(MessageSerializer(i))
                if MessageSerializer(i).data['sender_name'] == str(curr_user):
                    # print("{}{}{",str(curr_user))
                    msg_dict['you'] = str(MessageSerializer(i).data["description"])
                    msg_dict['attachment'] = str(MessageSerializer(i).data["attachment"])
                    msg_dict['time'] = str(MessageSerializer(i).data["time"])

                else:
                    msg_dict["{}".format(friend.Name_First + ' ' + friend.Name_Last)] = str(
                        MessageSerializer(i).data["description"])
                    msg_dict['attachment'] = str(MessageSerializer(i).data["attachment"])
                    msg_dict['time'] = str(MessageSerializer(i).data["time"])

                msg_list.append(msg_dict)

            # messages = ["'you' : " + str(MessageSerializer(each_message).data["description"])+ ", time : {}".format(str(MessageSerializer(each_message).data["time"])) if
            #            MessageSerializer(each_message).data['sender_name'] == str(curr_user) or
            #            MessageSerializer(each_message).data['receiver_name'] == curr_user else "'{}' : ".format(friend.Name_First +' '+friend.Name_Last) +' '+ str(
            #    MessageSerializer(each_message).data["description"]) +", time : {}".format(str(MessageSerializer(each_message).data["time"])) for each_message in messages]

            return Response({
                "success": True,
                # "messages": messages,
                "messages": msg_list,
                "status": 200,
                "curr_user": str(curr_user),
                "friend": str(friend)
            })

        except Exception as e:
            return Response({
                "status": 200,
                "success": False,
                "message": str(e)
            })


# class MessageView(generics.GenericAPIView):
# def message_list(request, sender=None, receiver=None):
#    def get(self, request, *args, **kwargs):
#
#        sender = request.user.account_id
#        email = request.query_params.get('email')
#        print(email)
#        receiver = User.objects.get(email = email).account_id
#
#        if request.method == 'GET':
#            #messages = Messages.objects.filter(sender_name=sender, receiver_name=receiver, seen=False)
#            messages = Messages.objects.filter(sender_name_id=sender, receiver_name_id=receiver, seen=False)
#            print("*****************",messages)
#            print("*****************", sender, receiver)
#            serializer = MessageSerializer(messages, many=True, context={'request': request})
#            for message in messages:
#                message.seen = True
#                message.save()
#            return JsonResponse(serializer.data, safe=False)
#
#
#    def post(self, request, *args, **kwargs):
#
#        #elif request.method == "POST":
#        print("request.data",request.data)
#        #data = JSONParser().parse(request.data)
#        data = request.data
#        print('data',data)
#        serializer = MessageSerializer(data=data)
#        if serializer.is_valid():
#            serializer.save()
#            return JsonResponse(serializer.data, status=201)
#        return JsonResponse(serializer.errors, status=400)


class MessageView(generics.GenericAPIView):
    # def message_list(request, sender=None, receiver=None):
    def get(self, request, *args, **kwargs):

        sender = request.user.account_id
        email = request.query_params.get('email')
        print(email)
        receiver = User.objects.get(email=email).account_id

        if request.method == 'GET':
            # messages = Messages.objects.filter(sender_name=sender, receiver_name=receiver, seen=False)
            messages = Messages.objects.filter(sender_name_id=sender, receiver_name_id=receiver, seen=False)
            print("*****************", messages)
            print("*****************", sender, receiver)
            serializer = MessageSerializer(messages, many=True, context={'request': request})
            for message in messages:
                message.seen = True
                message.save()
            return JsonResponse(serializer.data, safe=False)

    def post(self, request, *args, **kwargs):
        try:
            # elif request.method == "POST":
            print("request.data", request.data)
            # data = JSONParser().parse(request.data)
            data = request.data.dict()

            curr_user_id = getUserId(request.user.email)

            friend_id = getUserId(User.objects.get(email=data['receiver_name']).email)
            data['sender_name'] = request.user.email

            print('data', data)
            print(Friends.objects.filter(friend_id=friend_id,
                                         user_id=curr_user_id).exists() and Friends.objects.filter(
                friend_id=friend_id, user_id=curr_user_id).exists())

            if Friends.objects.filter(friend_id=friend_id,
                                      user_id=curr_user_id).exists() is False and Friends.objects.filter(
                friend_id=curr_user_id, user_id=friend_id).exists() is False:
                raise Exception("not friends")

            serializer = MessageSerializer(data=data)
            if serializer.is_valid():
                serializer.save()
                return Response({"message": serializer.data, "status": "200", "success": True})
            return Response({"message": serializer.errors, "status": 200, "success": False})
        except Exception as e:
            return Response({
                "status": 200,
                "success": False,
                "message": str(e)
            })


class AttachmentView(APIView):
    def post(self, request):
        attachment = request.FILES['attachment']
        Attachments.objects.update_or_create(attachment=attachment, user_id=request.user.account_id)
        file_1 = Attachments.objects.filter(user=request.user).last()
        return Response({
            "status": 200,
            "attachment": str(file_1)
        })


class ChatHistoryView(APIView):
    def post(self, request):
        friend_id = request.data.get('friend_id')
        Friends.objects.update_or_create(friend_id=friend_id, user_id=request.user.account_id)
        return Response({
            "status": 200,
            "success": True,
            "message": "Your friend successfully added in your chat list"
        })

    def get(self, request):
        friends = Friends.objects.filter(user=request.user)
        serialize = FriendsSerialiser(friends, many=True).data
        return Response({
            "status": 200,
            "success": True,
            "count": len(serialize),
            "friends": serialize
        })
