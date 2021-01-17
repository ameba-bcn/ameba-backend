from django.db import models


BIO_PREVIEW = 160


class Artist(models.Model):
    name = models.CharField(max_length=50)
    biography = models.TextField(max_length=2500)
    images = models.ManyToManyField(to='Image', blank=True)

    def __str__(self):
        return self.name

    @property
    def bio_preview(self):
        return self.biography[:BIO_PREVIEW]
