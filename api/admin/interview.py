from django.contrib import admin
from api.models import Interview, Answer, Question
from django.forms.models import BaseInlineFormSet
from django.utils.html import mark_safe
from django.utils.translation import gettext as _

from django import forms
from django.forms import ModelForm
from trumbowyg.widgets import TrumbowygWidget

from api.admin.image import get_image_preview


# class InterviewAdminForm(ModelForm):
#     introduction = forms.CharField(widget=TrumbowygWidget)
#
#     class Meta:
#         model = Interview
#         fields = ['introduction']
#         widgets = {
#             'text': TrumbowygWidget(),
#         }


class ArtistQuestionsInLineFormSet(BaseInlineFormSet):
    def __init__(self, *args, **kwargs):
        kwargs['initial'] = [
            {'question': question_id} for question_id in
            self.get_default_questions()
        ]
        super(ArtistQuestionsInLineFormSet, self).__init__(*args, **kwargs)

    @staticmethod
    def get_default_questions():
        try:
            return list(Question.objects.filter(is_default=True))
        except Exception as err:
            return []

    @classmethod
    def get_default_question_num(cls):
        return len(cls.get_default_questions())


class ChoiceInline(admin.TabularInline):
    model = Answer
    extra = 0
    verbose_name = 'Answer'
    formset = ArtistQuestionsInLineFormSet
    fields = ('question', 'answer', 'is_active')


class InterviewAdmin(admin.ModelAdmin):
    # form = InterviewAdminForm
    fieldsets = [
        (None, {'fields': ['title', 'artist', 'is_active','thumbnail_preview']}),
    ]
    readonly_fields = ('thumbnail_preview', 'list_preview')
    inlines = [ChoiceInline]
    list_display = ('title', 'artist', 'list_preview', )

    def thumbnail_preview(self, obj):
        if obj.artist and obj.artist.image.all():
            return mark_safe(
                '<img src="{}" width="300" height="300" />'.format(
                    obj.artist.images.first().url
                ))

    thumbnail_preview.short_description = _('Preview')
    thumbnail_preview.allow_tags = True

    @staticmethod
    def list_preview(obj):
        return get_image_preview(obj.artist.images.first(), 75)


admin.site.register(Interview, InterviewAdmin)


class QuestionAdmin(admin.ModelAdmin):
    search_fields = ['question']
    list_display = ['question']


admin.site.register(Question, QuestionAdmin)