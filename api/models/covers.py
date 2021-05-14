from django.db import models


class Cover(models.Model):
    file = models.FileField(upload_to='covers')
    is_active = models.BooleanField()
    index = models.IntegerField()
    created = models.DateTimeField(auto_now_add=True)

    @property
    def url(self):
        return self.file.url

    def __str__(self):
        return self.file.name
