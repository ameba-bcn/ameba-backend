from django.contrib import admin
from api.models import Interview, Answer, Question
from django.forms.models import BaseInlineFormSet
from django.utils.html import mark_safe
from django.utils.translation import gettext as _


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
    extra = ArtistQuestionsInLineFormSet.get_default_question_num()
    verbose_name = 'Answer'
    formset = ArtistQuestionsInLineFormSet
    fields = ('question', 'answer', 'is_active')


class ArtistAdmin(admin.ModelAdmin):
    fieldsets = [
        (None, {'fields': ['name', 'biography', 'image',
                           'thumbnail_preview']}),
        ('Contact info', {'fields': ['contact', 'email']})
    ]
    readonly_fields = ('thumbnail_preview', )
    inlines = [ChoiceInline]

    def thumbnail_preview(self, obj):
        if obj.image:
            return mark_safe(
                '<img src="{}" width="300" height="300" />'.format(
                    obj.image.url
                ))

    thumbnail_preview.short_description = _('Preview')
    thumbnail_preview.allow_tags = True


admin.site.register(Interview, ArtistAdmin)


class QuestionAdmin(admin.ModelAdmin):
    search_fields = ['question']
    list_display = ['question']


admin.site.register(Question, QuestionAdmin)
