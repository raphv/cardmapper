# -*- coding: utf-8 -*-

import uuid
from urllib.parse import urlsplit
from django.conf import settings
from django.db import models
from django.utils.html import strip_tags, format_html_join
from django.utils.safestring import mark_safe
from django.utils.functional import cached_property
from django.urls import reverse
from colorful.fields import RGBColorField
from imagekit.models import ImageSpecField
from imagekit.processors import ResizeToFit
from ckeditor.fields import RichTextField
from .utils import process_description, process_short_description

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
            models.Q(public=True) | models.Q(author=user)
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
    date_created = models.DateTimeField(
        auto_now_add=True,
        db_index=True,
    )
    date_updated = models.DateTimeField(
        auto_now=True,
        db_index=True,
    )
    public = models.BooleanField(
        default=True,
        db_index=True,
        help_text = 'Make it visible to all users. When unchecked, only you will be able to see it',
    )
    objects = PublicObjectManager()
    _tag_list = None
    
    def get_description_html(self):
        return mark_safe(self.description)
    
    @property
    def description_text(self):
        return process_description(self.description)

    @description_text.setter
    def description_text(self, value):
        self.description = format_html_join(
            '\n',
            '<p>{}</p>',
            ((part,) for part in value.split("\n"))
        )
    
    def get_short_description(self):
        return mark_safe(process_short_description(self.description))

    @property
    def tag_list(self):
        if self._tag_list is None:
            if self.pk:
                self._tag_list = [tag.name for tag in self.tags.all()]
            else:
                self._tag_list = []
        return self._tag_list
    
    @tag_list.setter
    def tag_list(self, value):
        self._tag_list = value
    
    @property
    def flat_tag_list(self):
        return (",").join(self.tag_list)
    
    @flat_tag_list.setter
    def flat_tag_list(self, value):
        tags = [t.strip() for t in value.split(",")]
        self.tag_list = [t for t in tags if t]
    
    def get_tag_texts(self):
        return ", ".join(self.tag_list)

    def get_absolute_url(self):
        return reverse(
            'cardapp:%s_detail'%self._meta.model_name,
            kwargs={'pk':self.pk}
        )

    def __str__(self):
        return self.title or '<Untitled>'
    
    def save(self, *args, **kwargs):
        super(MetadataModel, self).save(*args, **kwargs)
        new_tag_list = self.tag_list
        old_tag_list = [tag.name for tag in self.tags.all()]
        for tag in old_tag_list:
            if tag not in new_tag_list:
                self.tags.get(name=tag).delete()
        for tag in new_tag_list:
            if tag not in old_tag_list:
                tagobj, created = Tag.objects.get_or_create(name=tag)
                self.tags.add(tagobj)

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
    icon = ImageSpecField(source='image',
        processors=[ResizeToFit(80, 80, False)],
        format='JPEG',
        options={'quality': 80}
    )

    def get_all_cardmaps(self):
        return CardMap.objects.filter(cardoncardmap__card=self)

    @cached_property
    def public_cardmaps(self):
        return self.get_all_cardmaps().filter(public=True).distinct()

    def __str__(self):
        return "%s (in %s)"%(self.title, self.deck.title)
    
    class Meta:
        ordering = ['title']

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