from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.views.generic.edit import CreateView
from .models import Post, Category, Author
from .models import BaseRegisterForm
from datetime import datetime, timedelta, date
from django.core.exceptions import PermissionDenied
from django.core.paginator import Paginator
from .filters import PostFilter
from .forms import PostForm, UserForm, CategoryForm
from django.contrib.auth.models import User, Group
from django.contrib.auth.mixins import PermissionRequiredMixin, LoginRequiredMixin
from django.views.generic import TemplateView
from django.shortcuts import redirect
from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail
from django.http import HttpResponseRedirect
from django.http import HttpResponse
from django.db.models.signals import post_save,m2m_changed
from django.views import View
from .tasks import *
import logging

logger = logging.getLogger(__name__)

class NewsList(ListView):
    model = Post
    template_name = 'news.html'
    context_object_name = 'news'
    queryset = Post.objects.order_by('-id')
    paginate_by = 5
    form_class = PostForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['time_now'] = datetime.now()
        return context

    def post(self, request, *args, **kwargs):
        form = self.form_class(request.POST)  # создаём новую форму, забиваем в неё данные из POST-запроса

        if form.is_valid():  # если пользователь ввёл всё правильно и нигде не ошибся, то сохраняем новый товар
            form.save()

        return super().get(request, *args, **kwargs)

class NewsDetail(DetailView):
    model = Post
    template_name = 'newsdetail.html'
    context_object_name = 'newsdetail'

class Search(ListView):
    model = Post
    template_name = 'search.html'
    context_object_name = 'search'
    queryset = Post.objects.order_by('-id')
    paginate_by = 5

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['time_now'] = datetime.now()
        context['filter'] = PostFilter(self.request.GET, queryset=self.get_queryset())
        return context

class PostCreateView(PermissionRequiredMixin, CreateView):
    permission_required = ('arandnw.add_post')
    template_name = 'add.html'
    form_class = PostForm

class PostUpdateView(UpdateView, PermissionRequiredMixin):
    permission_required = ('arandnw.change_post')
    template_name = 'add.html'
    form_class = PostForm

    def get_object(self, **kwargs):
        id = self.kwargs.get('pk')
        return Post.objects.get(pk=id)



class PostDeleteView(DeleteView, PermissionRequiredMixin):
    permission_required = ('arandnw.delete_post',)
    template_name = 'delete.html'
    queryset = Post.objects.all()
    success_url = '/news/'

    def get_object(self, **kwargs):
        author = Post.objects.get(pk=self.kwargs.get('pk')).author.user
        user = User.objects.get(username=self.request.user)
        if user != author:
            raise PermissionDenied
        return Post.objects.get(pk=self.kwargs.get('pk'))


class UserDetailView(LoginRequiredMixin, TemplateView):
    template_name = 'user_inform.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['is_not_authors'] = not self.request.user.groups.filter(name='authors').exists()
        return context


@login_required
def upgrade_me(request):
    user = request.user
    try:
        author_group = Group.objects.get(name='authors')
    except Group.DoesNotExist:
        Group.objects.create(name="authors")
        author_group = Group.objects.get(name='authors')
    if not request.user.groups.filter(name='authors').exists():
        author_group.user_set.add(user)
    if not Author.objects.filter(user=user).exists():
        Author.objects.create(user=user)
    return redirect('/')

@login_required
def add_subscribe( request, pk):
    user = request.user
    sid = str(pk)
    Category.objects.get(pk=pk).subscribers.add(user)
    return redirect('/news/categorynews')


@login_required
def del_subscribe(request, pk):
    user = request.user
    #print('Пользователь', request.user, 'удален из подписчиков категории:', Category.objects.get(pk=pk))
    Category.objects.get(pk=pk).subscribers.remove(request.user)
    return redirect('/news/categorynews')


class BaseRegisterView(CreateView):
    model = User
    form_class = BaseRegisterForm
    success_url = '/'

    def post(self, request, *args, **kwargs):
        form = self.form_class(request.POST)
        if form.is_valid():
            first_name = form.cleaned_data.get("first_name")
            last_name = form.cleaned_data.get("last_name")
            email = form.cleaned_data.get("email")
            subject = f' Привет, {first_name}   {last_name}'
            form.save()

        send_mail(
            subject=subject,
            message='Спасибо за регистрацию на сайте News and Articals',
            from_email='Asmodey256@yandex.ru',
            recipient_list=[email]
        )

        return HttpResponseRedirect('/news/')

class CategoryList(ListView):
    model = Category
    template_name = 'categorynews.html'
    context_object_name = 'categorynews'
    queryset = Category.objects.order_by('-id')
    paginate_by = 10
    form_class = CategoryForm


class IndexView(View):
    def get(self, request):
        printer.delay(10)
        hello.delay()
        return HttpResponse('Hello!')