from celery import shared_task
from .models import *
from datetime import datetime, timedelta
import time

@shared_task
def hello():
    print("Hello, world! 1")
    time.sleep(10)
    print("Hello, world! 2")

@shared_task
def printer(N):
    for i in range(N):
        time.sleep(1)
        print(i+1)

@shared_task
def send_week_digest():
    print('Новости за неделю')
    for category in Category.objects.all():
        news_category = []
        week_news = Post.objects.filter(post_category__name=category).filter(
            data_create__range=[datetime.now() - timedelta(days=7), datetime.now()])
        for news in week_news:
            url = f'http://127.0.0.1:8000/news/{news.id} {news.title} '
            news_category.append(url)


        send_news = '\n'.join(news_category)

        for user in category.subscriber.all():
            sub_send_mail = user.email
            #Добавить фильтрацию чтобы был не пустой список
            if len(send_news) != 0:
                send_mail(
                    subject = 'Новости за неделю!',
                    message = f'Новости за неделю: \n {send_news}',
                    from_email = 'Asmodey256@yandex.ru',
                    recipient_list = [sub_send_mail],
                )

@shared_task
def  send_news_update ():
    print ('новые посты за неделю')    #здесь должен быть код  запускаемый по расписанию с рассылкой апдейтов новостей за неделю

@shared_task
def new_news(oid):
    print('новый пост')     #здесь должен быть код запускаемый ппри появлении новой новости