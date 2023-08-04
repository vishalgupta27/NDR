from django.db import models
from accounts.models import User
import uuid

class Messages(models.Model):

    description = models.TextField()
    # sender_name = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name='sender')
    # receiver_name = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name='receiver')
    sender_name = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sender')
    receiver_name = models.ForeignKey(User, on_delete=models.CASCADE, related_name='receiver')
    attachment = models.FileField(upload_to='user/chat_attachment', null=True, blank=True)
    time = models.TimeField(auto_now_add=True)
    seen = models.BooleanField(default=False)
    timestamp = models.DateTimeField(null=True,auto_now_add=True)

    def __str__(self):
        return f"To: {self.receiver_name} From: {self.sender_name}"

    class Meta:
        ordering = ('timestamp',)


class Friends(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    friend = models.ForeignKey(User, on_delete=models.CASCADE,related_name = 'my_friends')
    def __str__(self):
        return f"{self.friend}"

class Attachments(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    attachment = models.FileField(upload_to='user/chat_attachment', null=True, blank=True)
    def __str__(self):
        return f"{self.attachment}"