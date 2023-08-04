from django.urls import path, include
from . import views
from .views import *
urlpatterns = [
    #path("", views.index, name="index"),
    #path("search/", views.search, name="search"),
    path('api/search_user/',SearchUserView.as_view() , name="SearchUserView"),
    #path("addfriend/<str:name>", views.addFriend, name="addFriend"),
    path("api/addfriend/", AddFriendView.as_view(), name="addFriend"),
    path("api/chat/",ChatView.as_view(), name = "chat"),
    #path("chat/<str:username>", views.chat, name="chat"),
    #path('api/messages/<int:sender>/<int:receiver>', views.message_list, name='message-detail'),
    #path('api/messages', views.message_list, name='message-list'),
    path('api/messages', MessageView.as_view(), name='message-list'),
    path('api/ShowFriendView/',ShowFriendView.as_view(),name="ShowFriendView"),
    path('api/attachment/',AttachmentView.as_view(),name="AttachmentView"),
    path('api/chat-history/',ChatHistoryView.as_view(),name="ChatHistoryView"),


]

