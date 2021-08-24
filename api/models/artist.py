from django.db import models


BIO_PREVIEW = 160


class ArtistTag(models.Model):
    name = models.CharField(max_length=20)


class ArtistMediaUrl(models.Model):
    url = models.URLField()
    created = models.DateTimeField(auto_now_add=True)
    artist = models.ForeignKey(
        to='Artist', on_delete=models.CASCADE, related_name='media_urls'
    )

    def __str__(self):
        return self.url


class Artist(models.Model):
    name = models.CharField(max_length=50)
    biography = models.TextField(max_length=2500)
    images = models.ManyToManyField(to='Image', blank=True)
    tags = models.ManyToManyField(to='ArtistTag', blank=True)

    def __str__(self):
        return self.name

    @property
    def bio_preview(self):
        return self.biography[:BIO_PREVIEW]
