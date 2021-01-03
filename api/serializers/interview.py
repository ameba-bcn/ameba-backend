from rest_framework import serializers

from api.models import Interview, Answer, Question


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


class InterviewDetailSerializer(serializers.ModelSerializer):
    artist = serializers.SlugRelatedField(slug_field='name', read_only=True)
    current_answers = AnswersSerializers(many=True, read_only=True)

    class Meta:
        model = Interview
        fields = ['id', 'artist', 'title', 'introduction', 'created', 'image',
                  'current_answers']
        depth = 1


class InterviewListSerializer(serializers.ModelSerializer):
    artist = serializers.SlugRelatedField(slug_field='name', read_only=True)

    class Meta:
        model = Interview
        fields = ['id', 'artist', 'title', 'intro_preview', 'created', 'image']
