from django.db import models
from django.urls import reverse
from django.contrib.auth.models import User

# Create your models here.
class Option(models.Model):
    name = models.CharField("Название опции", max_length=50)
    value = models.BooleanField("Выбрать опцию", default=False)

    def __str__(self):
        return self.name


class Push(models.Model):
    title = models.CharField("Заголовок уведомления", max_length=50)
    text = models.CharField("Текст уведомления", max_length=250, blank=True, null=True)
    creation_date = models.DateTimeField("Дата создания", auto_now_add=True)
    send_date = models.DateTimeField("Дата отправки", auto_now_add=False, blank=True, null=True)
    is_sent = models.BooleanField("Отправлен", blank=True, null=False, default=False)
    sender = models.ForeignKey(
        User, 
        verbose_name='Отправитель сообщения', 
        on_delete=models.CASCADE,
        related_name='user_pushes',
        )

    class Meta:
        ordering = ['-creation_date']
        permissions = (('can_mark_is_sent', 'Set push notification as sended'),)

    def get_absolute_url(self):
        """Returns the url to access a particular instance of Push Model"""
        return reverse('push_detail', args=[str(self.id)])

    def __str__(self):
        return self.title