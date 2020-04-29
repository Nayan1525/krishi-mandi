from django.contrib.auth.models import AbstractUser
from django.db import models
from kmapp.models import *
from PIL import Image

class User(AbstractUser):
    is_farmer = models.BooleanField(default=False)
    is_dealer = models.BooleanField(default=False)

def get_foo():
    return 1

class Profile(models.Model):
    usern = models.OneToOneField(User, on_delete=models.CASCADE)
    image = models.ImageField(default='default.jpg', upload_to='prifile_pics')
    state = models.ForeignKey(State,on_delete=models.CASCADE,default=1)
    description = models.TextField(blank=True,null=True)
    activate_profile = models.BooleanField(default=False)

    def __str__(self):
        return f'{self.usern.username} Profile'

    # def save(self,*args,**kwargs):
    #     super().save(*args,**kwargs)
    #     img = Image.open(self.image.path)
    #     if img.height > 300 or img.width > 300:
    #         output_size = (300,300)
    #         img.thumbnail(output_size)
    #         img.save(self.image.path)

class Farmer(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True)


    def __str__(self):
        return self.user.username
    # quizzes = models.ManyToManyField(Quiz, through='TakenQuiz')
    # interests = models.ManyToManyField(Subject, related_name='interested_students')


class Dealer(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True)

    def __str__(self):
        return self.user.username
    # quizzes = models.ManyToManyField(Quiz, through='TakenQuiz')
    # interests = models.ManyToManyField(Subject, related_name='interested_students')
