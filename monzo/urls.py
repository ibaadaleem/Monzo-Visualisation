from django.conf.urls import include,url
from django.contrib import admin

from visualisation import views

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^home/', include('visualisation.urls')),
    url(r'^$', views.firstpage, name='firstpage'),
]
