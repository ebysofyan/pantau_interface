from rest_framework import serializers
from .. import models


class VotingSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Voting
        exclude = ['time']


class TimeCrawlingSerialize(serializers.ModelSerializer):
    votings = VotingSerializer(many=True)

    class Meta:
        model = models.TimeCrawling
        exclude = []
