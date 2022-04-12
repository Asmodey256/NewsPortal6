from django.db import models
from django.contrib.auth.models import User
from django.db.models import Sum
from datetime import datetime, date, time
from django.contrib.auth.forms import UserCreationForm
from django import forms


class Author(models.Model):
    authorUser = models.OneToOneField(User, on_delete=models.CASCADE)
    ratingAuthor = models.SmallIntegerField(default=0)

    def __str__(self):
        return f'{self.authorUser.username.title()}'

    def update_rating(self):
        postRat = self.post_set.aggregate(postRating=Sum("rating"))
        pRat = 0
        pRat += postRat.get("postRating")

        commentRat = self.authorUser.comment_set.aggregate(commentRating=Sum("rating"))
        cRat = 0
        cRat += commentRat.get("commentRating")

        self.ratingAuthor = pRat * 3 + cRat
        self.save()


class Category(models.Model):
    name = models.CharField(max_length=256, unique=True)
    subscribers = models.ManyToManyField(User)

    def __str__(self) -> str:
        return self.name

class Post(models.Model):
    author = models.ForeignKey('Author', on_delete=models.CASCADE)
    NEWS = "NW"
    ARTICLE = "AR"
    Choices = (
        (NEWS, "Новость"),
        (ARTICLE, "Статья"),
    )
    categoryType = models.CharField(max_length=2, choices=Choices, default=ARTICLE)
    dateCreation = models.DateTimeField(auto_now_add=True)
    postCategory = models.ManyToManyField(Category, through="PostCategory")
    title = models.CharField(max_length=256)
    text = models.TextField()
    rating = models.SmallIntegerField(default=0)


    def __str__(self) -> str:
        return f'{self.title()}'

    def get_absolute_url(self):  # добавим абсолютный путь, чтобы после создания нас перебрасывало на страницу с новостями
        return f'/news/{self.id}'

    def like(self):
        self.rating += 1
        self.save()

    def dislike(self):
        self.rating -= 1
        self.save()

    def preview(self):
        return self.text[0:124] + "..."


class PostCategory(models.Model):
    postTrough = models.ForeignKey(Post, on_delete=models.CASCADE)
    categoryTrough = models.ForeignKey(Category, on_delete=models.CASCADE)

    def __str__(self):
        return f'{self.postTrough.name.title()} : {self.categoryTrough.title.title()}'

class Comment(models.Model):
    commentPost = models.ForeignKey(Post, on_delete=models.CASCADE)
    commentUser = models.ForeignKey(User, on_delete=models.CASCADE)
    text = models.TextField()
    dateCreation = models.DateTimeField(auto_now_add=True)
    rating = models.SmallIntegerField(default=0)

    def __str__(self) -> str:
        return self.text[:20]

    def like(self):
        self.rating += 1
        self.save()

    def dislike(self):
        self.rating -= 1
        self.save()


class BaseRegisterForm(UserCreationForm):
    email = forms.EmailField(label = "Email")
    first_name = forms.CharField(label = "Имя")
    last_name = forms.CharField(label = "Фамилия")

    class Meta:
        model = User
        fields = ("username",
                  "first_name",
                  "last_name",
                  "email",
                  "password1",
                  "password2", )

