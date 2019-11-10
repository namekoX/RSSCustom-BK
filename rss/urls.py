from django.urls import path
from . import views

urlpatterns = [
  path("gettitle/",views.get_title,name="get_title"),
  path('get_entry_list/', views.get_entry_list, name='get_entry_list'),
  path('get_entry/', views.get_entry, name='get_entry'),
  path('create_entry/', views.create_entry, name='create_entry'),
  path('update_entry/', views.update_entry, name='update_entry'),
  path('delete_entry/', views.delete_entry, name='delete_entry'),
  path('get_rss/<int:entryno>.xml/', views.get_rss, name='get_rss'),
  path('create_user/', views.create_user, name='create_user'),
  path('update_user/', views.update_user, name='update_user'),
  path('login/', views.login, name='login'),
]