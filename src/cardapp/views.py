import json
from collections import OrderedDict
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.shortcuts import redirect, get_object_or_404
from django.core.exceptions import PermissionDenied
from django.http import HttpResponse, HttpResponseBadRequest
from django.views.decorators.http import require_POST
from django.views.generic import TemplateView, DetailView, ListView, CreateView, UpdateView
from django.urls import reverse
from .models import Deck, CardMap, Card, CardOnCardMap, filter_visible_to_user
from .forms import CardMapForm

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
        raise PermissionDenied

@method_decorator(login_required, name='dispatch')
class OwnItemsListView(ListView):
    
    def get_queryset(self, **kwargs):
        return super(OwnItemsListView, self).get_queryset(**kwargs).filter(author=self.request.user)

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
    
class MyCardmapsListView(OwnItemsListView):
    
    template_name = "cardapp/cardmap_my_list.html"
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
        } for card in context['object'].cardoncardmap_set.select_related('card').all()])
        return context

def cardmap_json(request, pk=None):
    cardmap = get_object_or_404(CardMap,pk=pk)
    if not cardmap.public and cardmap.author != self.request.user:
        raise PermissionDenied
    resdata = OrderedDict([
        ('title', cardmap.title),
        ('description', cardmap.description_text),
        ('tags', cardmap.tag_list),
        ('image', request.build_absolute_uri(cardmap.image.url)),
        ('width', cardmap.image_width),
        ('height', cardmap.image_height),
        ('cards', [
            OrderedDict([
                ('title', card.card.title),
                ('description', card.card.description_text),
                ('tags', card.card.tag_list),
                ('image', request.build_absolute_uri(card.card.image.url) if card.card.image else None),
                ('x', card.x),
                ('y', card.y),
            ])
            for card in cardmap.cardoncardmap_set.select_related('card').all()])
    ])
    return HttpResponse(
        json.dumps(resdata,indent=2),
        content_type="application/json"
    )

@method_decorator(login_required, name='dispatch')
class CardmapCreateView(CreateView):

    template_name = "cardapp/cardmap_create.html"
    model = CardMap
    form_class = CardMapForm

    def get_success_url(self):
        return reverse(
            'cardapp:cardmap_edit_map',
            kwargs={'pk':self.object.pk}
        )
    
    def get_form_kwargs(self, *args, **kwargs):
        res = super(CardmapCreateView, self).get_form_kwargs(*args, **kwargs)
        res['user'] = self.request.user
        return res

@method_decorator(login_required, name='dispatch')
class CardmapEditMetadataView(UpdateView):

    template_name = "cardapp/cardmap_edit_metadata.html"
    model = CardMap
    form_class = CardMapForm

    def get_success_url(self):
        return reverse(
            'cardapp:cardmap_edit_map',
            kwargs={'pk':self.object.pk}
        )

    def get_object(self, *args, **kwargs):
        obj = super(CardmapEditMetadataView, self).get_object(*args, **kwargs)
        if obj.author != self.request.user:
            raise PermissionDenied
        return obj
    
    def get_form_kwargs(self, *args, **kwargs):
        res = super(CardmapEditMetadataView, self).get_form_kwargs(*args, **kwargs)
        res['user'] = self.request.user
        return res
    
@method_decorator(login_required, name='dispatch')
class CardmapEditMapView(DetailView):
    
    template_name = "cardapp/cardmap_edit_map.html"
    model = CardMap

    def post(self, *args, **kwargs):
        cardmap = self.get_object()
        try:
            data = json.loads(self.request.POST['data'])
            cardmap.cardoncardmap_set.all().delete()
            CardOnCardMap.objects.bulk_create([
                CardOnCardMap(
                    cardmap = cardmap,
                    card_id = card['card_id'],
                    x = card['x'],
                    y = card['y'],
                )
                for card in data
            ])
        except:
            return HttpResponseBadRequest()
        return redirect(cardmap)
    
    def get_object(self, *args, **kwargs):
        obj = super(CardmapEditMapView, self).get_object(*args, **kwargs)
        if obj.author != self.request.user:
            raise PermissionDenied
        return obj
    
    def get_context_data(self, **kwargs):
        context = super(CardmapEditMapView, self).get_context_data(**kwargs)
        context['cards_json'] = json.dumps([{
            'x': card.x,
            'y': card.y,
            'id': card.id,
            'card_id': str(card.card.id),
            'title': card.card.title,
        } for card in context['object'].cardoncardmap_set.all()])
        return context

