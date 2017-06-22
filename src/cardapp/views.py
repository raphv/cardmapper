import json
from django.shortcuts import render
from django.http import Http404
from django.views.generic import TemplateView, DetailView, ListView
from .models import Deck, CardMap, Card, filter_visible_to_user

class VisibleToUserListView(ListView):

    def get_queryset(self, **kwargs):
        return filter_visible_to_user(
            super(VisibleToUserListView, self).get_queryset(**kwargs),
            self.request.user
        )

class VisibleToUserDetailView(DetailView):

    def get_object(self, **kwargs):
        res = super(VisibleToUserDetailView, self).get_object(**kwargs)
        if res.public or res.author == self.request.user:
            return res
        raise Http404

class HomeView(TemplateView):

    template_name = "cardapp/home.html"

    def get_context_data(self, **kwargs):
        context = super(HomeView, self).get_context_data(**kwargs)
        visible_decks = Deck.objects.visible_to_user(self.request.user)
        context['deck_count'] = visible_decks.count()
        context['latest_decks'] = visible_decks[:6]
        visible_cardmaps = CardMap.objects.visible_to_user(self.request.user)
        context['cardmap_count'] = visible_cardmaps.count()
        context['latest_cardmaps'] = visible_cardmaps[:6]
        return context

class DeckListView(VisibleToUserListView):
    
    template_name = "cardapp/deck_list.html"
    model = Deck

class DeckDetailView(VisibleToUserDetailView):
    
    template_name = "cardapp/deck_detail.html"
    model = Deck
    
class DeckCardsView(VisibleToUserDetailView):
    
    template_name = "cardapp/deck_cards.html"
    model = Deck

    def get_context_data(self, **kwargs):
        context = super(DeckCardsView, self).get_context_data(**kwargs)
        context['cards'] = context['object'].cards.visible_to_user(self.request.user)
        return context
    
class DeckCardmapsView(VisibleToUserDetailView):
    
    template_name = "cardapp/deck_cardmaps.html"
    model = Deck

    def get_context_data(self, **kwargs):
        context = super(DeckCardmapsView, self).get_context_data(**kwargs)
        context['cardmaps'] = context['object'].cardmaps.visible_to_user(self.request.user)
        return context

class CardDetailView(VisibleToUserDetailView):
    
    template_name = "cardapp/card_detail.html"
    model = Card
    
    def get_context_data(self, **kwargs):
        context = super(CardDetailView, self).get_context_data(**kwargs)
        context['cardmaps'] = filter_visible_to_user(
            context['object'].get_all_cardmaps(),
            self.request.user,
        ).distinct()
        return context

class CardmapListView(VisibleToUserListView):
    
    template_name = "cardapp/cardmap_list.html"
    model = CardMap

class CardmapDetailView(VisibleToUserDetailView):
    
    template_name = "cardapp/cardmap_detail.html"
    model = CardMap
    
    def get_context_data(self, **kwargs):
        context = super(CardmapDetailView, self).get_context_data(**kwargs)
        context['cards_json'] = json.dumps([{
            'x': card.x,
            'y': card.y,
            'id': card.id,
            'title': card.card.title,
        } for card in context['object'].cardoncardmap_set.all()])
        return context