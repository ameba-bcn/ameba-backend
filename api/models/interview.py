from django.db import models
from django.utils.translation import gettext as _
from django.core.exceptions import ValidationError

import api.images as img_utils

INTRO_PREVIEW = 160


class Interview(models.Model):
    class Meta:
        verbose_name = _('Interview')
        verbose_name_plural = _('Interviews')

    artist = models.ForeignKey(
        to='Artist', on_delete=models.DO_NOTHING, verbose_name=_('artist')
    )
    title = models.CharField(max_length=55, verbose_name=_('title'))
    introduction = models.TextField(max_length=5000, blank=True,
                                    verbose_name=_('introduction'))
    updated = models.DateTimeField(auto_now=True, verbose_name=_('updated'))
    created = models.DateTimeField(auto_now_add=True, verbose_name=_(
        'created'))
    image = models.ImageField(upload_to='interviews', blank=True,
                              verbose_name=_('image'))
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f'{self.title}'

    @property
    def intro_preview(self):
        return self.introduction[:INTRO_PREVIEW]

    @property
    def current_answers(self):
        return self.answers.filter(is_active=True)

    def save(self, *args, **kwargs):
        if self.image:
            img_utils.replace_image_field(self.image)
        super().save(*args, **kwargs)



class Question(models.Model):
    class Meta:
        verbose_name = _('Question')
        verbose_name_plural = _('Questions')

    question = models.TextField(max_length=2000, verbose_name=_('question'))
    position = models.IntegerField(null=True, blank=True)
    is_default = models.BooleanField(default=False, verbose_name=_('is default'))

    def __str__(self):
        return f'{self.question}'

    def set_position(self, position):
        self.position = position
        self.save()


class Answer(models.Model):
    class Meta:
        verbose_name = _('Answer')
        verbose_name_plural = _('Answers')

    interview = models.ForeignKey(
        'api.Interview',
        on_delete=models.CASCADE,
        related_name='answers',
        verbose_name=_('interview')
    )
    answer = models.TextField(max_length=5000, verbose_name=_('answer'))
    question = models.ForeignKey(
        to='Question',
        on_delete=models.CASCADE,
        verbose_name=_('question')
    )
    is_active = models.BooleanField(default=True, verbose_name=_('is active'))

    def __str__(self):
        return f'{self.interview.title} - {self.question.question} '
