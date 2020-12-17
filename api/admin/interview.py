from django.contrib import admin

from api.models import Interview, Question, Answer


class InterviewAdmin(admin.ModelAdmin):
    search_fields = ('artist', 'title')
    list_display = (
        'title',
        'artist',
        'created',
        'updated'
    )
    list_display_links = ('artist', 'title')


admin.site.register(Interview, InterviewAdmin)


class QuestionAdmin(admin.ModelAdmin):
    search_fields = ('question', )
    list_display = ('question', )


admin.site.register(Question, QuestionAdmin)


class AnswerAdmin(admin.ModelAdmin):
    search_fields = ('answer', 'question', 'interview')
    list_display = ('answer', 'question', 'interview')


admin.site.register(Answer, AnswerAdmin)
