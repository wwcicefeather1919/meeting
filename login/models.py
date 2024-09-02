# Create your models here.
from django.db import models


# class Employee(models.Model):
#     account = models.CharField(max_length=200)
#     password = models.CharField(max_length=200)

#     class Meta:
#         ordering = ['-pub_date']

#     def __str__(self):
#         return self.title


# class Guestbook(models.Model):
#     name = models.CharField(max_length=20)
#     email = models.CharField(max_length=100)
#     phone = models.CharField(max_length=20)
#     message = models.TextField()
#     rep_time = models.DateTimeField(auto_now_add=True)

#     class Meta:
#         ordering = ['-rep_time']

#     def __str__(self):
#         return self.name
