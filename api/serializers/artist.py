from django.contrib.auth import get_user_model
from rest_framework import serializers

from api.models import Artist, Answer, Question


class QuestionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Question
        fields = ['question']


class AnswersSerializers(serializers.ModelSerializer):
    question = serializers.SlugRelatedField(
        read_only=True, many=False, slug_field='question'
    )

    class Meta:
        model = Answer
        fields = ['question', 'answer']


class ArtistDetailSerializer(serializers.ModelSerializer):
    current_answers = AnswersSerializers(many=True, read_only=True)

    class Meta:
        model = Artist
        fields = ['id', 'name', 'biography', 'created', 'image',
                  'current_answers']
        depth = 1


class ArtistListSerializer(serializers.ModelSerializer):

    class Meta:
        model = Artist
        fields = ['id', 'name', 'bio_preview', 'created', 'image']
