from django.conf.urls import url

from . import views

app_name = 'visualisation'
urlpatterns = [
    url(r'^$', views.index, name='home'),
    url(r'^visuals/$', views.Visuals.as_view(), name='visuals'),
    url(r'^analytics/$', views.analytics, name='analytics'),
    url(r'^upload/$', views.upload, name='upload'),
    url(r'^csv_data/$', views.csv_data, name='csv_data'),
]