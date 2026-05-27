from django.contrib import admin
from django.urls import path
from django.contrib.auth.views import LogoutView
from Home import views # from app importing the views file
from django.contrib.auth import views as auth_views
from django.conf import settings
from django.conf.urls.static import static


urlpatterns = [
    path('', views.homepage, name='homepage'),
    path('about',views.about,name='about'),
    path('tvshows/', views.tv_shows, name='tv_shows'),
    path('movies',views.movies,name='movies'),
    path('movieview/<str:title>/',views.movieview,name='movieview'),
    path('contact',views.contact,name='contact'),
    path('dramaview/<str:title>/', views.dramaview, name='dramaview'),
    path('actor_profile/<slug:actor_name>/', views.actor_profile, name='actor_profile'),
    path('actors/', views.actors, name='actors'),    
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('signup/', views.signup, name='signup'),
    path("userprofile/",views.userprofile,name="userprofile"),
    path('profile/upload_avatar/', views.upload_avatar, name='upload_avatar'),
    path('add-to-watchlist/', views.add_to_watchlist, name='add_to_watchlist'),
    path('search/', views.search, name='search'),
    path('chatbot/', views.chatbot, name='chatbot'),

    



] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)