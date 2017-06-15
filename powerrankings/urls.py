"""powerrankings URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.10/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url
from django.contrib import admin
from powerr import views
urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^$', views.home, name='home'),
    url(r'^player/(?P<p>[a-zA-Z0-9\-]+)$', views.player, name='player'),
    url(r'^load/challonge/(?P<url>[a-zA-Z0-9]+)$', views.load_challonge, name='load_challonge'),
    url(r'^load/reload_all/(?P<region>[0-9]+)$', views.full_update_ratings, name='full_update'),
    url(r'^alias/add/(?P<player>[^\/]+)/(?P<alias>[^\/]+)', views.add_alias, name="add_alias"),
    url(r'^reload_all$', views.rescan_all_tournaments, name='rescan_all'),
    url(r'^delete_all$', views.delete_all_but_tournaments, name='delete_all'),
    url(r'^reset$', views.admin, name='reset'),
    url(r'^about$', views.about, name='about'),
    url(r'^tournaments$', views.tournaments, name='tournaments'),
    url(r'^tournaments/(?P<id>[^\/]+)$', views.show_tournament, name='get_tournament'),
]
