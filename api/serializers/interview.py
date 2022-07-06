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


class InterviewListSerializer(serializers.ModelSerializer):
    artist = serializers.SlugRelatedField(slug_field='name', read_only=True)
    artist_id = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Interview
        fields = ['id', 'artist', 'title', 'intro_preview', 'created',
                  'image', 'artist_id']

    @staticmethod
    def get_artist_id(interview):
        return interview.artist.id


class InterviewDetailSerializer(InterviewListSerializer):
    current_answers = serializers.SerializerMethodField()

    class Meta(InterviewListSerializer.Meta):
        fields = ['id', 'artist', 'title', 'introduction', 'created', 'image',
                  'current_answers', 'artist_id']
        depth = 1

    @staticmethod
    def get_current_answers(instance):
        return AnswersSerializers(
            instance.answers.all().order_by('question__position'), many=True,
            read_only=True
        ).data
