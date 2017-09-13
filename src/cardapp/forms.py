import json
from django import forms
from .models import Card, CardMap, Deck

class CustomBaseForm(forms.ModelForm):

    tag_list = forms.CharField(required=False, help_text='Type in comma separated values')
    
    def __init__(self, user=None, *args, **kwargs):
        super(CustomBaseForm, self).__init__(*args, **kwargs)
        self.user = user
        if self.instance:
            self.fields['tag_list'].initial = self.instance.flat_tag_list
    
    def save(self, force_insert=False, force_update=False, commit=True):
        instance = super(CustomBaseForm, self).save(commit=False)
        instance.flat_tag_list = self.cleaned_data['tag_list']
        if commit:
            instance.save()
        return instance

class CardMapForm(CustomBaseForm):

    image = forms.ImageField(required=False)
    user = None

    def __init__(self, *args, **kwargs):
        super(CardMapForm, self).__init__(*args, **kwargs)
        self.fields['deck'].queryset = Deck.objects.visible_to_user(self.user)
        
    def save(self, force_insert=False, force_update=False, commit=True):
        instance = super(CardMapForm, self).save(commit=False)
        instance.author = self.user
        if commit:
            instance.save()
        return instance

    class Meta:
        model = CardMap
        fields = ['title', 'description', 'image', 'deck', 'public', 'tag_list']

class CardMapJsonForm(forms.Form):

    json_file = forms.FileField(
        label = 'JSON File',
        required = True,
        widget = forms.FileInput(attrs={'accept':'.json'}),
    )
    image = forms.ImageField(
        label = 'Background image',
        help_text = '(optional)',
        required = False,
    )
    public = forms.BooleanField(
        required = False,
        initial = True,
        help_text = 'Uncheck this box to make the card map only visible to yourself',
    )

    def clean_json_file(self):
        jsonf = self.cleaned_data['json_file']
        json_str = jsonf.read().decode('utf-8')
        try:
            json_data = json.loads(json_str)
        except:
            raise forms.ValidationError(
                'This is not a valid JSON file!',
                code='json_error',
            )
        for field_name in ['title', 'cards']:
            if not field_name in json_data:
                raise forms.ValidationError(
                    'The JSON file has no "%s" property'%field_name,
                    code='json_no_%s'%field_name,
                )
        if not len(json_data['cards']):
            raise forms.ValidationError(
                'The JSON file has no cards',
                code='json_no_cards',
            )
        for card in json_data['cards']:
            search_tbl = []
            card_obj = None
            if 'magellan_id' in card:
                search_tbl.append(('magellan_id', card['magellan_id']))
            if 'title' in card:
                search_tbl.append(('title', card['title']))
            try:
                float(card.get('x'))
                float(card.get('y'))
            except (ValueError, TypeError):
                raise forms.ValidationError(
                    "All cards must have valid X and Y coordinates",
                    code='card_invalid_x_y',
                )
            for search_index in search_tbl:
                try:
                    card_obj = Card.objects.get(**dict([search_index]))
                except (Card.DoesNotExist, Card.MultipleObjectsReturned):
                    pass
            if not card_obj:
                raise forms.ValidationError(
                    "One or more cards in the JSON file couldn't be found in the database through its title or Magellan ID (%s)"%(card.get('magellan_id',card.get('title','none'))),
                    code='card_no_match',
                )
            card['card'] = card_obj
        self.cleaned_data['cardmap_data'] = json_data
    
    class Meta:
        fields = ['json_file', 'image', 'public']
