from django.db import models


class Cover(models.Model):
    image = models.ImageField(upload_to='covers')
    is_active = models.BooleanField()
    index = models.IntegerField()
    created = models.DateTimeField(auto_now_add=True)

    @property
    def url(self):
        return self.image.url

    def __str__(self):
        return self.image.name
