from django.db import models


class Artist(models.Model):
    member = models.ForeignKey('Member', related_name='artists',
                               on_delete=models.CASCADE, blank=True, null=True)
    artistic_name = models.CharField(max_length=55)
    personal_name = models.CharField(max_length=55, blank=True)
    biography = models.TextField(max_length=2000)
    updated = models.DateTimeField(auto_now=True)
    created = models.DateTimeField(auto_now_add=True)
    image = models.ImageField(upload_to='artists')
