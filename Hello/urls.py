from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

admin.site.site_header = "What2Watch Admin"
admin.site.site_title = "What2Watch Admin Portal"
admin.site.index_title = "Welcome to What2Watch"

urlpatterns = [
    path("__reload__/", include("django_browser_reload.urls")),
    path('admin/', admin.site.urls),
    path('', include('Home.urls')),  # Routes all URLs from your app
]

# This serves media files (like profile images) during development
if settings.DEBUG:
     urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
