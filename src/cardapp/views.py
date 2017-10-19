import json
from collections import OrderedDict
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.shortcuts import redirect, get_object_or_404, render
from django.core.exceptions import PermissionDenied
from django.http import HttpResponse, HttpResponseBadRequest
from django.template.defaultfilters import truncatechars
from django.views.decorators.http import require_POST
from django.views.generic import TemplateView, DetailView, ListView, CreateView, UpdateView, DeleteView
from django.urls import reverse, reverse_lazy
from .models import Deck, CardMap, Card, CardOnCardMap, AnnotationOnCardMap, filter_visible_to_user
from .forms import CardMapForm
# Magellan-specific
from .models import Tag
from django.db.models import Count
from .forms import CardMapJsonForm
from PIL import Image, ImageDraw
from io import BytesIO
from django.core.files.base import ContentFile

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
            'icon': card.card.icon.url if card.card.image else None,
            'icon_width': card.card.icon.width if card.card.image else None,
            'icon_height': card.card.icon.height if card.card.image else None,
        } for card in context['object'].cardoncardmap_set.select_related('card').all()])
        context['annotations_json'] = json.dumps([{
            'x': annotation.x,
            'y': annotation.y,
            'id': annotation.id,
            'content': truncatechars(annotation.content,200),
        } for annotation in context['object'].annotationoncardmap_set.all()])
        # Magellan-specific
        context['tags'] =  Tag.objects.filter(
            card__cardoncardmap__cardmap=context['object']
        ).annotate(count=Count('card')).order_by('-count').values('name','count')[:10]
        # End of Magellan-specific
        return context

def get_image_url(obj, request):
    if obj.image:
        return request.build_absolute_uri(obj.image.url)
    else:
        return None

def cardmap_json(request, pk=None):
    cardmap = get_object_or_404(CardMap,pk=pk)
    if not cardmap.public and cardmap.author != self.request.user:
        raise PermissionDenied
    resdata = OrderedDict([
        ('id', cardmap.id),
        ('url', request.build_absolute_uri(cardmap.build_absolute_url())),
        ('title', cardmap.title),
        ('description', cardmap.description_text),
        ('tags', cardmap.tag_list),
        ('image', get_image_url(cardmap, request)),
        ('width', cardmap.image_width),
        ('height', cardmap.image_height),
        ('deck', OrdderedDict([
            ('id', cardmap.deck.id),
            ('url', request.build_absolute_uri(cardmap.deck.get_absolute_url())),
            ('title', cardmap.deck.title),
        ]),
        ('cards', [
            OrderedDict([
                ('id', card.card.id),
                ('magellan_id', card.card.magellan_id),
                ('url', request.build_absolute_uri(card.card.get_absolute_url())),
                ('title', card.card.title),
                ('x', card.x),
                ('y', card.y),
            ])
            for card in cardmap.cardoncardmap_set.select_related('card').all()
        ]),
        ('annotations', [
            OrderedDict([
                ('content', annotation.content),
                ('x', annotation.x),
                ('y', annotation.y),
            ])
            for annotation in cardmap.annotationoncardmap_set.all()
        ]),
    ])
    return HttpResponse(
        json.dumps(resdata,indent=2),
        content_type="application/json"
    )

def deck_json(request, pk=None):
    deck = get_object_or_404(Deck,pk=pk)
    if not deck.public and deck.author != self.request.user:
        raise PermissionDenied
    resdata = OrderedDict([
        ('id', deck.id),
        ('url', request.build_absolute_uri(deck.get_absolute_url())),
        ('title', deck.title),
        ('description', deck.description_text),
        ('tags', deck.tag_list),
        ('image', get_image_url(deck, request)),
        ('cards', [
            OrderedDict([
                ('magellan_id', card.magellan_id),
                ('title', card.title),
                ('description', card.description_text),
                ('tags', card.tag_list),
                ('image', get_image_url(card, request)),
                ('url', request.build_absolute_uri(card.get_absolute_url())),
            ])
            for card in deck.cards.visible_to_user(request.user)
        ]),
    ])
    return HttpResponse(
        json.dumps(resdata,indent=2),
        content_type="application/json"
    )

def all_cardmaps_json(request, pk=None):
    cardmaps = CardMap.objects.visible_to_user(self.request.user)
    resdata = [
        OrderedDict([
            ('id', cardmap.id),
            ('url', request.build_absolute_uri(cardmap.build_absolute_url())),
            ('title', cardmap.title),
            ('tags', cardmap.tag_list),
            ('deck', OrdderedDict([
                ('id', cardmap.deck.id),
                ('url', request.build_absolute_uri(cardmap.deck.get_absolute_url())),
                ('title', cardmap.deck.title),
            ]),
        ])
        for cardmap in cardmaps
    ]
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

@login_required
def cardmap_import_json(request):
    if request.method == 'POST':
        form = CardMapJsonForm(request.POST, request.FILES)
        if form.is_valid():
            cardmap_data = form.cleaned_data['cardmap_data']
            cardmap = CardMap(
                title = cardmap_data.get('title'),
                description = cardmap_data.get('description'),
                deck = cardmap_data['cards'][0]['card'].deck,
                public = form.cleaned_data.get('public', True),
                author = request.user,
            )
            if form.cleaned_data['image']:
                cardmap.image = form.cleaned_data['image']
            elif 'width' in cardmap_data and 'height' in cardmap_data:
                width = int(float(cardmap_data['width']))
                height = int(float(cardmap_data['height']))
                tmp_image = Image.new(
                    'RGB',
                    (width,height),
                    (200,200,200)
                )
                img_draw = ImageDraw.Draw(tmp_image)
                for k in range(0, width, 50):
                    img_draw.line((k,0,k,height),fill=(255,255,255))
                for k in range(0, height, 50):
                    img_draw.line((0,k,width,k),fill=(255,255,255))
                tmp_bytes = BytesIO()
                tmp_image.save(tmp_bytes,'PNG')
                cardmap.image.save(
                    'blank-%dx%d.png'%(width,height),
                    ContentFile(tmp_bytes.getvalue()),
                    save=False
                )
            cardmap.save()
            for card in cardmap_data['cards']:
                CardOnCardMap.objects.create(
                    card = card['card'],
                    cardmap = cardmap,
                    x = card['x'],
                    y = card['y'],
                )
            return redirect(
                'cardapp:cardmap_detail',
                pk = cardmap.pk
            )
    else:
        form = CardMapJsonForm()
    return render(
        request,
        "cardapp/cardmap_import_json.html",
        {'form': form}
    )

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
            cardmap.annotationoncardmap_set.all().delete()
            CardOnCardMap.objects.bulk_create([
                CardOnCardMap(
                    cardmap = cardmap,
                    card_id = card['card_id'],
                    x = card['x'],
                    y = card['y'],
                )
                for card in data['cards']
            ])
            AnnotationOnCardMap.objects.bulk_create([
                AnnotationOnCardMap(
                    cardmap = cardmap,
                    content = annotation['content'],
                    x = annotation['x'],
                    y = annotation['y'],
                )
                for annotation in data['annotations']
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
        context['annotations_json'] = json.dumps([{
            'x': annotation.x,
            'y': annotation.y,
            'content': annotation.content,
        } for annotation in context['object'].annotationoncardmap_set.all()])
        return context

@method_decorator(login_required, name='dispatch')
class CardmapDeleteView(DeleteView):

    template_name = "cardapp/cardmap_confirm_delete.html"
    model = CardMap
    success_url = reverse_lazy('cardapp:cardmap_my_list')

    def get_object(self, *args, **kwargs):
        obj = super(CardmapDeleteView, self).get_object(*args, **kwargs)
        if obj.author != self.request.user:
            raise PermissionDenied
        return obj
