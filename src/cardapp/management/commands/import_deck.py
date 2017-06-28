import argparse
import json
import re
from django.core.management.base import BaseCommand, CommandError
from django.core.files.base import ContentFile
from cardapp.models import Deck, Card, Tag
from urllib.request import urlopen
from urllib.parse import urlencode

url_re = re.compile(r'^https?:\/\/')

class Command(BaseCommand):
    help = 'Creates a standard playing cards deck from a JSON File'
    
    def add_arguments(self, parser):
        parser.add_argument(
            'file',
            type = argparse.FileType('r'),
            help = "A JSON file to load"
        )

    def handle(self, *args, **options):

        def set_image(url_or_file, model_with_image_field, save=True):
            if url_or_file:
                filename = url_or_file.split("/")[-1]
                if url_re.match(url_or_file):
                    try:
                        imgcontent = urlopen(url_or_file).read()
                    except Exception as e:
                        print("Couldn't retrieve %s: %s"%(url, e))
                else:
                    with open(url_or_file, "rb") as f:
                        imgcontent = f.read()
                if imgcontent:
                    model_with_image_field.image.save(filename, ContentFile(imgcontent), save)

        data = json.load(options['file'])

        deck = Deck.objects.create(
            title = data.get('title',''),
            description_text = data.get('description', data.get('title','')),
            url = data.get('url', ''),
            public = True, # Should be made an option
            tag_list = data.get('tags', [])
        )
        set_image(data.get('image',''),deck)
        
        for card_data in data['cards']:
            card = Card.objects.create(
                deck = deck,
                title = card_data.get('title',''),
                description_text = card_data.get('description', card_data.get('title','')),
                background_color = card_data.get('color',''),
                public = True, # Should be made an option
                tag_list = card_data.get('tags', [])
            )
            set_image(card_data.get('image',''),card)


 