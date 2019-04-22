from calendar import monthrange
from datetime import date, datetime, timedelta

from rest_framework import status
from rest_framework.authentication import TokenAuthentication
from rest_framework.generics import GenericAPIView, ListAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from . import serializers
from .. import helpers, models


class PemiluPostGenericView(GenericAPIView):
    serializer_class = serializers.TimeCrawlingSerialize
    permission_classes = (IsAuthenticated, )
    authentication_classes = (TokenAuthentication, )

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

        return Response(data=serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class PemiluPublicApiGenericView(ListAPIView):
    serializer_class = serializers.TimeCrawlingSerialize

    def get_start_date(self, sdt):
        """get_start_date"""
        return sdt.strftime('%Y-%m-%d') + ' 00:00'

    def get_end_date(self, edt):
        """get_start_date"""
        return edt.strftime('%Y-%m-%d') + ' 23:59'

    def get_queryset(self):
        if 'time' in self.request.GET:
            param = self.request.GET['time']
            now = date.today()

            if param == 'today':
                qs = models.TimeCrawling.objects.filter(create_at__range=[
                    self.get_start_date(now),
                    self.get_end_date(now),
                ])
            elif param == 'weeks':
                week = now - timedelta(days=7)
                qs = models.TimeCrawling.objects.filter(create_at__range=[
                    self.get_start_date(week),
                    self.get_end_date(now),
                ])
            elif param == 'month':
                days = monthrange(now.year, now.month)
                month = now - timedelta(days=days[1])
                qs = models.TimeCrawling.objects.filter(create_at__range=[
                    self.get_start_date(month),
                    self.get_end_date(now),
                ])
            else:
                return models.TimeCrawling.objects.all()
            return qs
        return models.TimeCrawling.objects.all()
