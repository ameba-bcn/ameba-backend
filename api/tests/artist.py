from api.tests._helpers import BaseTest
from django.core.files.images import ImageFile
from rest_framework import status
from rest_framework.utils.serializer_helpers import ReturnList
from dateutil import parser
from django.test import tag

from api import models
from api.models.artist import BIO_PREVIEW


def valid_date(date_text):
    parser.parse(date_text)
    return True


def valid_url(url_text):
    return url_text.startswith('http')


class TestArtist(BaseTest):
    DETAIL_ENDPOINT = '/api/artists/{pk}/'
    LIST_ENDPOINT = '/api/artists/'

    def setUp(self):
        self.create_questions()
        self.create_artists()
        super().setUp()

    @staticmethod
    def create_questions():
        for i in range(10):
            models.Question.objects.create(
                question=f'Esta es la pregunta numero {i}?',
                is_default=bool(i % 2)
            )

    @staticmethod
    def create_answers(artist):
        for question in models.Question.objects.all():
            models.Answer.objects.create(
                artist=artist,
                is_active=bool(question.pk % 4),
                question=question,
                answer=f'Esta es mi respuesta de {artist.id}'
            )

    def create_artists(self):
        for artist_num in range(10):
            artist = models.Artist.objects.create(
                name=f'artist_{artist_num}',
                biography=f'bio-{artist_num}' * 200,
                contact=f'contact-{artist_num}',
                image=ImageFile(
                    open('api/tests/fixtures/media/artist-image.jpg', 'rb')
                ),
                email=f'email-{artist_num}@ameba.cat',
            )
            self.create_answers(artist)

    @tag("artist")
    def test_get_list_no_auth(self):
        response = self._list(token='')
        total_artists = models.Artist.objects.all()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIsInstance(response.data, ReturnList)
        self.assertEqual(len(response.data), len(total_artists))

    @tag("artist")
    def test_get_list_artist_data(self):
        response = self._list(token='')
        artist_data = response.data[0]
        list_artist_data = {
            'id': int,
            'name': str,
            'bio_preview': str,
            'created': str,
            'image': str
        }
        for key in list_artist_data:
            self.assertIn(key, artist_data)
            self.assertIs(type(artist_data[key]), list_artist_data[key])

    @tag("artist")
    def test_get_list_artist_valid_image_url(self):
        response = self._list(token='')
        image_url = response.data[0]['image']
        self.assertTrue(valid_url(image_url))

    @tag("artist")
    def test_get_list_artist_valid_dates(self):
        response = self._list(token='')
        created = response.data[0]['created']
        self.assertTrue(valid_date(created))

    @tag("artist")
    def test_get_list_artist_bio_preview_length(self):
        response = self._list(token='')
        bio_preview = response.data[0]['bio_preview']
        self.assertEqual(len(bio_preview), BIO_PREVIEW)

    @tag("artist")
    def test_get_artist(self):
        artist = models.Artist.objects.all()[0]
        pk = artist.pk
        response = self._get(pk=pk, token='')
        self.assertEqual(artist.id, response.data['id'])
        self.assertEqual(artist.name, response.data['name'])
        self.assertEqual(artist.biography, response.data['biography'])
        self.assertEqual(artist.created, parser.parse(response.data['created']))
        self.assertIn(artist.image.url, response.data['image'])
        self.assertEqual(
            len(artist.current_answers), len(response.data['current_answers'])
        )
        for total_answer in artist.answers.all():
            if total_answer.is_active:
                self.assertIn(
                    {
                        'question': total_answer.question.question,
                        'answer': total_answer.answer
                    },
                    response.data['current_answers']
                )

    @tag("artist")
    def test_create_artist_not_allowed(self):
        attrs = {
            'name': f'artist',
            'biography': f'bio ' * 200,
            'contact': f'contact',
            'image': ImageFile(
                open('api/tests/fixtures/media/artist-image.jpg', 'rb')
            ),
            'email': f'email-@ameba.cat'
        }
        response = self._create(attrs)
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    @tag("artist")
    def test_delete_artist_not_allowed(self):
        artist_id = models.Artist.objects.all()[0].id
        response = self._delete(pk=artist_id, token='')
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    @tag("artist")
    def test_update_artist_not_allowed(self):
        artist_id = models.Artist.objects.all()[0].id
        attrs = {
            'name': f'artist',
            'biography': f'bio ' * 200,
            'contact': f'contact',
            'image': ImageFile(
                open('api/tests/fixtures/media/artist-image.jpg', 'rb')
            ),
            'email': f'email-@ameba.cat'
        }
        response = self._update(pk=artist_id, props=attrs, token='')
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)
