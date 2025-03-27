from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('sign_up/', views.sign_up, name='sign_up'),
    path('group_login/', views.group_login, name='group_login'),
    path('create_group/', views.create_group, name='create_group'),
    path('admin_login/', views.admin_login, name='admin_login'),
    path('admin_dashboard/<int:group_id>/', views.admin_dashboard, name='admin_dashboard'),
    path('delete_poll/<int:poll_id>/', views.delete_poll, name='delete_poll'), 
    path('user_dashboard/<int:group_id>/', views.user_dashboard, name='user_dashboard'),
    path('vote/<int:poll_id>/', views.vote, name='vote'),
    path('results/<int:group_id>/', views.show_results, name='show_results'),
    path('randomize_tie/<int:group_id>/', views.randomize_tie, name='randomize_tie'),
    path('search/<int:group_id>/', views.search_movies, name='search_movies'),
    path('watch/<int:group_id>/', views.watch_movie, name="watch_movie"),
]
