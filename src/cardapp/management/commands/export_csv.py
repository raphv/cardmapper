try:
    import unicodecsv as csv
except:
    import csv
import argparse
from django.db.models import Count
from django.core.management.base import BaseCommand
from cardapp.models import CardMap, Tag, Card

class Command(BaseCommand):
    help = 'Exports card maps to a CSV file'
    
    def add_arguments(self, parser):
        parser.add_argument(
            'file',
            type = argparse.FileType('w+b'),
            help = "A CSV file to write"
        )

    def handle(self, *args, **options):
        csv_fields = ['Title', 'Author', 'URL', 'Card count', 'CARDS:' ]
        csv_fields += [v[0] for v in Card.objects.all().values_list('title')]
        csv_fields.append('CARD TAGS:')
        csv_fields += [v[0] for v in Tag.objects.exclude(card=None).values_list('name')]
        writer = csv.DictWriter(options['file'], fieldnames=csv_fields)
        writer.writeheader()
        for c in CardMap.objects.all():
            tags = Tag.objects.filter(card__cardoncardmap__cardmap=c).annotate(count=Count('card')).values_list('name','count')
            cards = Card.objects.filter(cardoncardmap__cardmap=c).annotate(count=Count('cardoncardmap')).values_list('title','count')
            csv_dict = {
                'Title': c.title,
                'Author': c.author.username if c.author else '',
                'URL': c.get_absolute_url(),
                'Card count': c.cardoncardmap_set.count()
            }
            csv_dict.update(tags)
            csv_dict.update(cards)
            writer.writerow(csv_dict)
