from rest_framework import status
from rest_framework.generics import GenericAPIView
from rest_framework.response import Response

from . import serializers
from .. import models


class PemiluGenericView(GenericAPIView):
    serializer_class = serializers.TimeCrawlingSerialize

    def get(self, request):
        pass

    def post(self, request):
        """
        post data
        """
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            votings = serializer.validated_data.pop('votings')
            timec = models.TimeCrawling.objects.create(**serializer.validated_data)

            for voting in votings:
                models.Voting.objects.create(**voting, time=timec)

            return Response(data={
                'msg': 'success'
            }, status=status.HTTP_201_CREATED)

        return Response(data={
            'msg': 'failed!'
        }, status=status.HTTP_400_BAD_REQUEST)
