from modeltranslation.translator import register, TranslationOptions
from .models import (
    Manifest, Artist, Interview, Item, Subscription, Article,
    Event, ItemAttributeType, EventType, ArtistTag
)


@register(Manifest)
class AboutTranslationOptions(TranslationOptions):
    fields = ('text', )


@register(Artist)
class ArtistTranslationOptions(TranslationOptions):
    fields = ('biography', )


@register(Interview)
class InterviewTranslationOptions(TranslationOptions):
    fields = ('title', 'introduction')


@register(Item)
class ItemTranslationOptions(TranslationOptions):
    fields = ('name', 'description')


@register(Subscription)
class SubscriptionTranslationOptions(TranslationOptions):
    fields = ('benefits', )


@register(Article)
class ArticleTranslationOptions(TranslationOptions):
    pass


@register(EventType)
class EventTypeTranslationOptions(TranslationOptions):
    fields = ('name', )


@register(Event)
class EventTranslationOptions(TranslationOptions):
    fields = ('header', )


@register(ItemAttributeType)
class ItemAttributeTypeTranslationOptions(TranslationOptions):
    fields = ('name', )


@register(ArtistTag)
class ArtistTagTranslationOptions(TranslationOptions):
    fields = ('name', )
