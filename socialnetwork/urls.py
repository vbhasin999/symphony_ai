from django.contrib import admin
from django.urls import path
from socialnetwork import views

urlpatterns = [
    path('login/', views.login_action, name='login'),
    path('register/', views.register_action, name='register'),
    path('', views.global_action, name='global'),
    path('global/', views.global_action, name='global'),
    path('follower_stream/', views.follower_stream_action, name='follower'),
    path('logout/', views.logout_action, name='logout'),
    path('user_profile/', views.user_profile_action, name='user_profile'),
    path('other_profile/<int:id>', views.other_profile_action, name='other_profile'),
    path('follow/<int:id>', views.follow, name='follow'),
    path('unfollow/<int:id>', views.unfollow, name='unfollow'),
    path('photo/<int:id>', views.get_photo, name='photo'),
    path('get-global', views.get_global_action, name='get-global'),
    path('get-follower', views.get_follower_action, name='get-follower'),
    path('add-comment', views.add_comment_action, name='add-comment'),

]