from django import forms
from .models import CardMap, Deck

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