from django.views.generic import TemplateView
from django.conf.urls import patterns, include, url
from django.conf.urls.static import static
from django.conf import settings
from django.contrib.auth.views import login, logout

import empirebt.main.views as views

from empirebt.webapp.views import register, dashboard


urlpatterns = patterns('',

    url(r'^$', TemplateView.as_view(template_name="index.html")),

    #Login and Logout
    url(r'^login/$',  login ),
    url(r'^logout/$', logout, {'next_page' : '/'}),

    url(r'^register/$', register),
    url(r'^dashboard/$', dashboard),

    url(r'^authorization/general\.json', views.auth_general),
    url(r'^authorization/chat_empire\.json', views.empire_auth),
    url(r'^authorization/chat_oneonone\.json', views.oneonone_auth),
    url(r'^authorization/battle\.json', views.battle_auth),
    url(r'^chat_oneonone/connected\.json', views.connected_oneonone),
    url(r'^chat_empire/connected\.json', views.connected_empire),
    url(r'^chat_oneonone/list\.json', views.list_oneonone),
    url(r'^chat_empire/list\.json', views.list_empire),
	url(r'^battle/info\.json', views.battle_info),
    url(r'^battle/result\.json', views.battle_result),
    url(r'^login/', views.lock_summary),

) + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)