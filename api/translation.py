from modeltranslation.translator import register, TranslationOptions
from .models import (
    About, Artist, Interview, Item, Subscription, Article,
    Event, ItemAttributeType, EventTag
)


@register(About)
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


@register(Event)
class EventTranslationOptions(TranslationOptions):
    pass


@register(EventTag)
class EventTypeTranslationOptions(TranslationOptions):
    fields = ('name', )


@register(ItemAttributeType)
class ItemAttributeTypeTranslationOptions(TranslationOptions):
    fields = ('name', )
