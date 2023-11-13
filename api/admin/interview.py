from django.contrib import admin
from api.models import Interview, Answer, Question
from django.forms.models import BaseInlineFormSet
from django.utils.html import mark_safe
from django.utils.translation import gettext as _
from django.contrib import messages

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

def set_position(request, queryset, position):
    if len(queryset) != 1:
        messages.add_message(
            request, messages.WARNING, 'Only one question change at a time'
        )
        return
    queryset.first().set_order(position)

@admin.action(description="Set order to 1")
def set_first(modeladmin, request, queryset):
    set_position(request, queryset, 1)

@admin.action(description="Set order to 2")
def set_second(modeladmin, request, queryset):
    set_position(request, queryset, 2)


@admin.action(description="Set order to 3")
def set_third(modeladmin, request, queryset):
    set_position(request, queryset, 3)


@admin.action(description="Set order to 4")
def set_fourth(modeladmin, request, queryset):
    set_position(request, queryset, 4)


@admin.action(description="Set order to 5")
def set_fifth(modeladmin, request, queryset):
    set_position(request, queryset, 5)


@admin.action(description="Set order to 6")
def set_sixth(modeladmin, request, queryset):
    set_position(request, queryset, 6)


@admin.action(description="Set order to 7")
def set_seventh(modeladmin, request, queryset):
    set_position(request, queryset, 7)


@admin.action(description="Set order to 8")
def set_eighth(modeladmin, request, queryset):
    set_position(request, queryset, 8)


@admin.action(description="Set order to 9")
def set_ninth(modeladmin, request, queryset):
    set_position(request, queryset, 9)


@admin.action(description="Set order to 10")
def set_tenth(modeladmin, request, queryset):
    set_position(request, queryset, 10)



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
    list_display = ['question', 'position']
    ordering = ['position']
    actions = [set_first, set_second, set_third, set_fourth, set_fifth,
               set_sixth, set_seventh, set_eighth, set_ninth, set_tenth]


admin.site.register(Question, QuestionAdmin)