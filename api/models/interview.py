from django.db import models
from django.utils.translation import gettext as _


INTRO_PREVIEW = 160


class Interview(models.Model):
    artist = models.ForeignKey(to='Artist', on_delete=models.DO_NOTHING)
    title = models.CharField(max_length=55)
    introduction = models.TextField(max_length=2000)
    updated = models.DateTimeField(auto_now=True)
    created = models.DateTimeField(auto_now_add=True)
    image = models.ImageField(upload_to='interviews')

    def __str__(self):
        return f'{self.title}'

    @property
    def intro_preview(self):
        return self.introduction[:INTRO_PREVIEW]

    @property
    def current_answers(self):
        return self.answers.filter(is_active=True)


class Question(models.Model):
    question = models.TextField(max_length=200)
    is_default = models.BooleanField(default=False)

    def __str__(self):
        return f'{self.question}'


class Answer(models.Model):
    interview = models.ForeignKey(
        'api.Interview',
        on_delete=models.CASCADE,
        related_name='answers',
        verbose_name=_('interview')
    )
    answer = models.TextField(max_length=1000, verbose_name=_('answer'))
    question = models.ForeignKey(
        to='Question',
        on_delete=models.CASCADE,
        verbose_name=_('question')
    )
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f'{self.interview.title} - {self.question.question} '
