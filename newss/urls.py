from django.contrib import admin
from django.urls import path, include
from arandnw.views import UserDetailView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('news/', include('arandnw.urls')),
    path('', UserDetailView.as_view()),
    path('accounts/', include('allauth.urls')),

]