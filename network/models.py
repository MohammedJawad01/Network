from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    pass

class Post(models.Model):
    user = models.ForeignKey(User , on_delete=models.CASCADE , related_name="userPosts")
    content = models.CharField(max_length=255)
    date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user} posted {self.id} on {self.date.strftime('%d %b %Y %H:%M:%S')}"
    

class Follow(models.Model):
    user = models.ForeignKey(User , on_delete=models.CASCADE , related_name="user_following") 
    user_follower = models.ForeignKey(User , on_delete=models.CASCADE , related_name="followed_user")

    def __str__(self):
        return f"{self.user} following {self.user_follower}" 
    

class Like(models.Model):
    user = models.ForeignKey(User , on_delete=models.CASCADE , related_name="user_like") 
    post = models.ForeignKey(Post , on_delete=models.CASCADE , related_name="post_like")

    def __str__(self):
        return f"{self.user} liked {self.post}" 