from django.conf.urls import url
from django.urls import path

from . import views

urlpatterns = [
    path('', views.render_html, name='render_html'),
    url(r'^submit', views.submit),
    url(r'^submit_geo', views.submit_geo)

]