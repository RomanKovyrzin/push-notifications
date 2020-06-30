from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('pushes/', views.PushListView.as_view(), name='pushes'),
    path('push/<int:pk>', views.PushDetailView.as_view(), name='push_detail'),
    path('options/', views.OptionListView.as_view(), name='options'),
    path('option/<int:pk>', views.OptionDetailView.as_view(), name='option_detail'),
    path('push/create/', views.create_push, name='push_create'),
    path('push/<int:pk>/send/', views.send_push, name='push_send'),
    path('push/<int:pk>/update/', views.send_push, name='push_update'),
    path('push/<int:pk>/delete/', views.PushDelete.as_view(), name='push_delete'),
]