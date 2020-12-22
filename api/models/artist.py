from django.db import models
from django.utils.translation import gettext as _


BIO_PREVIEW = 160


class Artist(models.Model):
    name = models.CharField(max_length=55)
    contact = models.CharField(max_length=55)
    biography = models.TextField(max_length=2000)
    updated = models.DateTimeField(auto_now=True)
    created = models.DateTimeField(auto_now_add=True)
    image = models.ImageField(upload_to='artists')
    email = models.EmailField()

    def __str__(self):
        return f'{self.name}'

    @property
    def bio_preview(self):
        return self.biography[:BIO_PREVIEW]

    @property
    def current_answers(self):
        return self.answers.filter(is_active=True)


class Question(models.Model):
    question = models.TextField(max_length=200)
    is_default = models.BooleanField(default=False)

    def __str__(self):
        return f'{self.question}'


class Answer(models.Model):
    artist = models.ForeignKey(
        'Artist',
        on_delete=models.DO_NOTHING,
        related_name='answers',
        verbose_name=_('artist')
    )
    answer = models.TextField(max_length=1000, verbose_name=_('answer'))
    question = models.ForeignKey(
        to='Question',
        on_delete=models.DO_NOTHING,
        verbose_name=_('question')
    )
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f'{self.artist.name} - {self.question.question} '
