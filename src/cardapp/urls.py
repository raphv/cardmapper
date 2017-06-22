from django.conf.urls import url
from cardapp import views

app_name = 'cardapp'

urlpatterns = [
    url(r'^$', views.HomeView.as_view(), name='home'),
    url(r'^decks/$', views.DeckListView.as_view(), name='deck_list'),
    url(r'^decks/(?P<pk>[0-9a-f-]+)/$', views.DeckDetailView.as_view(), name='deck_detail'),
    url(r'^decks/(?P<pk>[0-9a-f-]+)/cards/$', views.DeckCardsView.as_view(), name='deck_cards'),
    url(r'^decks/(?P<pk>[0-9a-f-]+)/cardmaps/$', views.DeckCardmapsView.as_view(), name='deck_cardmaps'),
    url(r'^cards/(?P<pk>[0-9a-f-]+)/$', views.CardDetailView.as_view(), name='card_detail'),
    url(r'^cardmaps/$', views.CardmapListView.as_view(), name='cardmap_list'),
    url(r'^cardmaps/(?P<pk>[0-9a-f-]+)/$', views.CardmapDetailView.as_view(), name='cardmap_detail'),
]