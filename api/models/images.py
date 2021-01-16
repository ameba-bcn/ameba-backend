from django.db import models


class Image(models.Model):
    image = models.ImageField(upload_to='images')

    @property
    def url(self):
        return self.image.url

    def __str__(self):
        return self.image.name
