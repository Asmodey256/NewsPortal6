from django_filters import FilterSet, DateTimeFilter
from .models import Post
from datetime import datetime

# создаём фильтр
class PostFilter(FilterSet):

    class Meta:
        model = Post
        fields = {'dateCreation': ['gt'],'title': ['icontains'], 'author':['in']}