from django.contrib import admin
from django.utils.html import format_html_join
from imagekit.admin import AdminThumbnail
from .models import Tag, Deck, Card, CardMap, CardOnCardMap, AnnotationOnCardMap

def make_public(modeladmin, request, queryset):
    queryset.update(public=True)
    
def make_private(modeladmin, request, queryset):
    queryset.update(public=False)


def tag_list(obj):
    return ", ".join(o.name for o in obj.tags.all())

@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    readonly_fields = ('related_objects',)
    
    def related_objects(self, obj):
        return format_html_join(
            '\n',
            '<p><strong>{}</strong> {}: {}</p>',
            ((related_object._meta.verbose_name, related_object.id, str(related_object)) for related_object in obj.get_related_objects())
        )
    
@admin.register(Deck)
class DeckAdmin(admin.ModelAdmin):
    actions = (make_public, make_private)
    list_display = ('__str__', 'author', 'public', 'card_count', tag_list, 'admin_thumbnail')
    readonly_fields = ('admin_thumbnail',)
    list_filter = ('author', 'public')
    admin_thumbnail = AdminThumbnail(image_field='thumbnail')
    
    def card_count(self, obj):
        return obj.cards.count()

    def get_queryset(self, request):
        return super(DeckAdmin, self).get_queryset(request).prefetch_related('cards', 'tags')

@admin.register(Card)
class CardAdmin(admin.ModelAdmin):
    actions = (make_public, make_private)
    list_display = ('title', 'author', 'public', 'deck', tag_list, 'admin_thumbnail')
    readonly_fields = ('admin_thumbnail',)
    list_filter = ('author', 'public', 'deck')
    admin_thumbnail = AdminThumbnail(image_field='thumbnail')
    
    def get_queryset(self, request):
        return super(CardAdmin, self).get_queryset(request).prefetch_related('tags')

class CardOnCardMapInline(admin.TabularInline):
    model = CardOnCardMap
    extra = 1
    
class AnnotationInline(admin.TabularInline):
    model = AnnotationOnCardMap
    extra = 1

@admin.register(CardMap)
class CardMapAdmin(admin.ModelAdmin):
    actions = (make_public, make_private)
    list_display = ('__str__', 'author', 'public', 'deck', 'card_count', 'annotation_count', tag_list, 'admin_thumbnail')
    readonly_fields = ('admin_thumbnail',)
    list_filter = ('author', 'public', 'deck')
    admin_thumbnail = AdminThumbnail(image_field='thumbnail')
    inlines = (CardOnCardMapInline, AnnotationInline,)

    def card_count(self, obj):
        return obj.cardoncardmap_set.count()

    def annotation_count(self, obj):
        return obj.annotationoncardmap_set.count()
    
    def get_queryset(self, request):
        return super(CardMapAdmin, self).get_queryset(request).prefetch_related('annotationoncardmap_set', 'cardoncardmap_set', 'tags')