from modeltranslation.translator import register, TranslationOptions
from .models import About, Artist, Interview, Item, Subscription


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
