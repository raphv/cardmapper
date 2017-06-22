# -*- coding: utf-8 -*-

import uuid
from html.parser import HTMLParser
from urllib.parse import urlsplit
from django.conf import settings
from django.db import models
from django.template.defaultfilters import truncatechars
from django.utils.html import strip_tags
from django.utils.safestring import mark_safe
from django.utils.functional import cached_property
from django.urls import reverse
from colorful.fields import RGBColorField
from imagekit.models import ImageSpecField
from imagekit.processors import ResizeToFit
from ckeditor.fields import RichTextField

class Tag(models.Model):
    name = models.CharField(
        max_length = 200,
        unique = True,
    )

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name

    def get_related_objects(self):
        accessors = [tag.get_accessor_name() for tag in Tag._meta.get_fields() if tag.many_to_many]
        result = []
        for accessor_name in accessors:
            accessor = getattr(self, accessor_name)
            result += accessor.all()
        return result

def filter_visible_to_user(queryset, user=None):
    if user and user.is_authenticated:
        return queryset.filter(
            models.Q(public=True) | models.Q(author=user_obj)
        )
    return queryset.filter(public=True)


class PublicObjectManager(models.Manager):
    use_for_related_fields = True

    def get_public(self):
        return filter_visible_to_user(self.get_queryset())

    def visible_to_user(self, user):
        return filter_visible_to_user(self.get_queryset(), user)

def upload_dest(instance, filename):
    return '%s/%s/%s'%(
        instance._meta.model_name,
        instance.author or 'shared',
        filename
    )

class MetadataModel(models.Model):
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
    )
    title = models.CharField(
        max_length=200,
        blank=True,
        db_index = True,
    )
    description = RichTextField(
        blank=True,
    )
    tags = models.ManyToManyField(
        Tag,
        blank = True,
    )
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete = models.SET_NULL,
        db_index = True,
        blank = True,
        null = True,
        default = None,
    )
    image = models.ImageField(
        upload_to = upload_dest,
        blank = True,
        width_field = 'image_width',
        height_field = 'image_height',
    )
    image_width = models.PositiveIntegerField(
        editable = False,
        null = True,
    )
    image_height = models.PositiveIntegerField(
        editable = False,
        null = True,
    )
    thumbnail = ImageSpecField(source='image',
        processors=[ResizeToFit(220, 165, False)],
        format='JPEG',
        options={'quality': 60}
    )
    medium_image = ImageSpecField(source='image',
        processors=[ResizeToFit(800, 600, False)],
        format='JPEG',
        options={'quality': 60}
    )
    date_created = models.DateField(
        auto_now_add=True,
        db_index=True,
    )
    date_updated = models.DateField(
        auto_now=True,
        db_index=True,
    )
    public = models.BooleanField(
        default=True,
        db_index=True,
    )
    objects = PublicObjectManager()
    
    def get_content_html(self):
        return mark_safe(self.description)
    
    def get_content_text(self):
        return HTMLParser().unescape(strip_tags(self.description))
    
    def get_short_content(self):
        return truncatechars(self.get_content_text(),200)

    def get_tag_list(self):
        return [tag.name for tag in self.tags.all()]

    def get_tag_texts(self):
        return ", ".join(self.get_tag_list())

    def get_absolute_url(self):
        return reverse(
            'cardapp:%s_detail'%self._meta.model_name,
            kwargs={'pk':self.pk}
        )

    def __str__(self):
        return self.title or '<Untitled>'

    class Meta:
        abstract = True
        ordering = ['-date_created']

class Deck(MetadataModel):
    url = models.URLField(
        blank = True,
    )

    def get_url_host(self):
        return urlsplit(self.url).netloc


class Card(MetadataModel):
    background_color = RGBColorField(default='#ffffff')
    deck = models.ForeignKey(
        Deck,
        on_delete = models.CASCADE,
        related_name = "cards"
    )

    def get_all_cardmaps(self):
        return CardMap.objects.filter(cardoncardmap__card=self)

    @cached_property
    def public_cardmaps(self):
        return self.get_all_cardmaps().filter(public=True).distinct()

class CardMap(MetadataModel):
    deck = models.ForeignKey(
        Deck,
        on_delete=models.CASCADE,
        related_name = 'cardmaps',
    )

class ThingOnCardMap(models.Model):
    cardmap = models.ForeignKey(
        CardMap,
        on_delete=models.CASCADE,
    )
    x = models.IntegerField()
    y = models.IntegerField()

    class Meta:
        abstract = True

class CardOnCardMap(ThingOnCardMap):
    card = models.ForeignKey(
        Card,
        on_delete=models.CASCADE,
        db_index=True,
    )
    
    class Meta:
        verbose_name = "Card"
        verbose_name_plural = "Cards"

class AnnotationOnCardMap(ThingOnCardMap):
    content = models.TextField()
    
    class Meta:
        verbose_name = "Annotation"
        verbose_name_plural = "Annotations"