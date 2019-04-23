from calendar import monthrange
from datetime import date, datetime, timedelta

from rest_framework import status
from rest_framework.authentication import TokenAuthentication
from rest_framework.generics import GenericAPIView, ListAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from . import serializers
from .. import helpers, models
from ..regions import REGION_LIST


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


class PemiluChartApiView(GenericAPIView):

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
                qs = models.TimeCrawling.objects.all()

            return qs[:25]
        return models.TimeCrawling.objects.all()[:25]

    def get_voting_queryset(self):
        if 'time' in self.request.GET:
            param = self.request.GET['time']
            now = date.today()

            if param == 'today':
                qs = models.Voting.objects.filter(time__create_at__range=[
                    self.get_start_date(now),
                    self.get_end_date(now),
                ])
            elif param == 'weeks':
                week = now - timedelta(days=7)
                qs = models.Voting.objects.filter(time__create_at__range=[
                    self.get_start_date(week),
                    self.get_end_date(now),
                ])
            elif param == 'month':
                days = monthrange(now.year, now.month)
                month = now - timedelta(days=days[1])
                qs = models.Voting.objects.filter(time__create_at__range=[
                    self.get_start_date(month),
                    self.get_end_date(now),
                ])
            else:
                qs = models.Voting.objects.all()

            return qs
        return models.Voting.objects.all()

    def formatter(self, queryset):
        bt_categories = []
        series = []

        for (code, name) in REGION_LIST:
            bt_categories.append(name)

        tp_categories = ['01', '02']
        for q in queryset:
            for cat in tp_categories:
                series.append({
                    'name': q.create_at,
                    'showInLegend': False,
                    'stack': cat,
                    'data': [int(v.value1) if cat == '01' else int(v.value2) for v in q.votings.all().order_by('region')]
                })

        tp_categories = tp_categories * len(bt_categories)
        series_end = {
            'name': '',
            'showInLegend': False,
            'stack': '02',
            'data': [0 for i in tp_categories],
            'xAxis': 1
        }
        series.append(series_end)

        return {
            'title': 'Grafik aktifitas inputan data SINTUNG KPU',
            'bt_categories': sorted(bt_categories),
            'tp_categories': tp_categories,
            'series': series
        }

    def get(self, request):
        return Response(
            data=self.formatter(self.get_queryset()),
            status=status.HTTP_200_OK
        )
