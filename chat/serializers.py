from rest_framework import serializers
from .models import *
from accounts.models import User
from accounts.serializers import UserSerializer


class MessageSerializer(serializers.ModelSerializer):
    sender_name = serializers.SlugRelatedField(many=False, slug_field='email', queryset=User.objects.all())
    receiver_name = serializers.SlugRelatedField(many=False, slug_field='email', queryset=User.objects.all())

    class Meta:
        model = Messages
        fields = ['sender_name', 'receiver_name', 'description', 'attachment', 'time']


class AttachmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Attachments
        fields = ['attachment']


class FriendsSerialiser(serializers.ModelSerializer):
    friend = UserSerializer(read_only=True)

    class Meta:
        model = Friends
        fields = ['user', 'friend']
