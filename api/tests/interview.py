from api.tests._helpers import BaseTest
from django.core.files.images import ImageFile
from rest_framework import status
from rest_framework.utils.serializer_helpers import ReturnList
from dateutil import parser
from django.test import tag

from api import models
from api.models.interview import INTRO_PREVIEW


def valid_date(date_text):
    parser.parse(date_text)
    return True


def valid_url(url_text):
    return url_text.startswith('http')


class TestInterview(BaseTest):
    DETAIL_ENDPOINT = '/api/interviews/{pk}/'
    LIST_ENDPOINT = '/api/interviews/'

    def setUp(self):
        self.create_questions()
        self.create_interviews()
        super().setUp()

    @staticmethod
    def create_questions():
        for i in range(10):
            models.Question.objects.create(
                question=f'Esta es la pregunta numero {i}?',
                is_default=bool(i % 2)
            )

    @staticmethod
    def create_answers(interview):
        for question in models.Question.objects.all():
            models.Answer.objects.create(
                interview=interview,
                is_active=bool(question.pk % 4),
                question=question,
                answer=f'Esta es mi respuesta de {interview.id}'
            )

    def create_interviews(self):
        for interview_num in range(10):
            artist = models.Artist.objects.create(
                name=f'Artist {interview_num}',
                biography=f'Biography for the artist Artit {interview_num}'
            )
            interview = models.Interview.objects.create(
                title=f'interview_{interview_num}',
                artist=artist,
                introduction=f'bio-{interview_num}' * 200,
                image=ImageFile(
                    open('api/tests/fixtures/media/interview-image.jpg', 'rb')
                )
            )
            self.create_answers(interview)

    @tag("interview")
    def test_get_list_no_auth(self):
        response = self._list(token='')
        total_interviews = models.Interview.objects.all()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIsInstance(response.data, ReturnList)
        self.assertEqual(len(response.data), len(total_interviews))

    @tag("interview")
    def test_get_list_interview_data(self):
        response = self._list(token='')
        interview_data = response.data[0]
        list_interview_data = {
            'id': int,
            'artist': str,
            'artist_id': int,
            'title': str,
            'intro_preview': str,
            'created': str,
            'image': str
        }
        for key in list_interview_data:
            self.assertIn(key, interview_data)
            self.assertIs(type(interview_data[key]), list_interview_data[key])

    @tag("interview")
    def test_get_list_interview_valid_image_url(self):
        response = self._list(token='')
        image_url = response.data[0]['image']
        self.assertTrue(valid_url(image_url))

    @tag("interview")
    def test_get_list_interview_valid_dates(self):
        response = self._list(token='')
        created = response.data[0]['created']
        self.assertTrue(valid_date(created))

    @tag("interview")
    def test_get_list_interview_intro_preview_length(self):
        response = self._list(token='')
        intro_preview = response.data[0]['intro_preview']
        self.assertEqual(len(intro_preview), INTRO_PREVIEW)

    @tag("interview")
    def test_get_interview(self):
        interview = models.Interview.objects.all()[0]
        pk = interview.pk
        response = self._get(pk=pk, token='')
        self.assertEqual(interview.id, response.data['id'])
        self.assertEqual(interview.artist.name, response.data['artist'])
        self.assertEqual(interview.artist.pk, response.data['artist_id'])
        self.assertEqual(interview.title, response.data['title'])
        self.assertEqual(interview.introduction, response.data['introduction'])
        self.assertEqual(interview.created, parser.parse(response.data['created']))
        self.assertIn(interview.image.url, response.data['image'])
        self.assertEqual(
            len(interview.current_answers), len(response.data['current_answers'])
        )
        for total_answer in interview.answers.all():
            if total_answer.is_active:
                self.assertIn(
                    {
                        'question': total_answer.question.question,
                        'answer': total_answer.answer
                    },
                    response.data['current_answers']
                )

    @tag("interview")
    def test_create_interview_not_allowed(self):
        artist = models.Artist.objects.create(name='Artist', biography='Bio')
        attrs = {
            'title': f'interview',
            'artist': artist.id,
            'introduction': f'bio ' * 200,
            'image': ImageFile(
                open('api/tests/fixtures/media/interview-image.jpg', 'rb')
            )
        }
        response = self._create(attrs, format=None)
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    @tag("interview")
    def test_delete_interview_not_allowed(self):
        interview_id = models.Interview.objects.all()[0].id
        response = self._delete(pk=interview_id, token='')
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    @tag("interview")
    def test_update_interview_not_allowed(self):
        artist = models.Artist.objects.create(name='Artist', biography='Bio')
        interview_id = models.Interview.objects.all()[0].id
        attrs = {
            'title': f'interview',
            'artist': artist.id,
            'introduction': f'bio ' * 200,
            'image': ImageFile(
                open('api/tests/fixtures/media/interview-image.jpg', 'rb')
            )
        }
        response = self._update(pk=interview_id, props=attrs, token='')
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)
