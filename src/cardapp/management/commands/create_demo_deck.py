import json
from django.core.management.base import BaseCommand, CommandError
from django.core.files.base import ContentFile
from cardapp.models import Deck, Card, CardMap, CardOnCardMap
from django.utils.html import format_html
from urllib.request import urlopen
from urllib.parse import urlencode

class Command(BaseCommand):
    help = 'Creates a standard playing cards deck'

    def handle(self, *args, **options):

        def download_image(url, filename, model_with_image_field, save=True):
            try:
                imgcontent = urlopen(url).read()
                model_with_image_field.image.save(filename, ContentFile(imgcontent), save)
            except Exception as e:
                print("Couldn't retrieve %s: %s"%(url, e))
        
        deck = Deck.objects.create(
            title = 'Playing cards demo deck',
            description_text = 'This is a standard 52-card deck',
            url = 'https://en.wikipedia.org/wiki/Standard_52-card_deck',
            public = True,
            tag_list = ['Demo'],
        )
        download_image(
            "https://upload.wikimedia.org/wikipedia/commons/0/0a/Deck_of_cards_used_in_the_game_piquet.jpg",
            "democards.jpg",
            deck,
        )

        cardmap = CardMap.objects.create(
            title = 'Playing cards demo card map',
            description_text = 'This is a photo of a 52-card deck taken from Wikipedia',
            deck = deck,
            tag_list = ['Demo'],
        )
        download_image(
            "https://upload.wikimedia.org/wikipedia/commons/0/02/Piatnikcards.jpg",
            "democards.jpg",
            cardmap,
        )
        xstep = cardmap.image_width // 13
        ystep = cardmap.image_height // 4
        y = -(ystep // 2)

        cardvalues = [
            '2', '3', '4', '5', '6', '7', '8',
            '9', '10', 'Jack', 'Queen', 'King', 'Ace',
        ]
        suites = [
            'diamond', 'club', 'heart', 'spade'
        ]
        suitecolors = {
            'diamond': '#ff0000',
            'heart': '#ff0000',
            'spade': '#000000',
            'club': '#000000',
        }
        for suite in suites:
            y += ystep
            x = -(xstep // 2)
            for value in cardvalues:
                x += xstep
                cardname = "%s of %ss"%(value, suite)
                print("Processing %s"%cardname)
                card = Card.objects.create(
                    deck = deck,
                    title = cardname,
                    description_text = cardname,
                    background_color = suitecolors[suite],
                    public = True,
                    tag_list = ['Demo', suite.capitalize(), value]
                )
                apiurl = "https://commons.wikimedia.org/w/api.php?%s"%(urlencode({
                    "action": "query",
                    "titles": "File:Playing_card_%s_%s.svg"%(suite, value if value == '10' else value[0] ),
                    "prop": "imageinfo",
                    "iiprop": "url",
                    "iiurlwidth": "200",
                    "format": "json"
                }));
                CardOnCardMap.objects.create(
                    cardmap = cardmap,
                    card = card,
                    x = x,
                    y = y,
                )
                try:
                    jsondata = json.loads(urlopen(apiurl).read().decode())
                    thumbnail_url = list(jsondata["query"]["pages"].values())[0]["imageinfo"][0]["thumburl"]
                    download_image(
                        thumbnail_url,
                        '%s_of_%ss.jpg'%(value,suite),
                        card
                    )
                except Exception as e:
                    print("Couldn't retrieve %s: %s"%(apiurl, e))