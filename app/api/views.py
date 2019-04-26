from calendar import monthrange
from datetime import date, timedelta

import numpy as np
from django.http import Http404
from rest_framework import status
from rest_framework.authentication import TokenAuthentication
from rest_framework.generics import GenericAPIView, ListAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .. import models
from ..regions import REGION_LIST
from . import serializers


class PemiluPostGenericView(GenericAPIView):
    serializer_class = serializers.TimeCrawlingSerialize
    permission_classes = (IsAuthenticated, )
    authentication_classes = (TokenAuthentication, )

    def post(self, request):
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
        return sdt.strftime('%Y-%m-%d') + ' 00:00'

    def get_end_date(self, edt):
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


class PemiluChartRangeApiView(GenericAPIView):
    def get_start_date(self, sdt):
        return sdt.strftime('%Y-%m-%d') + ' 00:00'

    def get_end_date(self, edt):
        return edt.strftime('%Y-%m-%d') + ' 23:59'

    def get_queryset(self):
        if 'time' in self.request.GET:
            param = self.request.GET['time']
            start = date.today()
            end = date.today()

            if param == 'today':
                pass
            elif param == 'weeks':
                start = start - timedelta(days=7)
            elif param == 'month':
                days = monthrange(start.year, start.month)
                start = start - timedelta(days=days[1])
            else:
                raise Http404

            return models.TimeCrawling.objects.distinct('time_server').filter(create_at__range=[
                self.get_start_date(start),
                self.get_end_date(end),
            ])
        return models.TimeCrawling.objects.order_by('-time_server').distinct().all()[:25]

    def separate_series(self, data):
        series_1 = []
        series_2 = []
        for s in series:
            if s['stack'] == '01':
                series_1.append(s['data'])
            else:
                series_2.append(s['data'])

        return series_1, series_2

    def series_substractor(self, series):
        returden_list = []
        data = sorted(series)
        for i in range(len(data), 0, -1):
            if i == 1:
                n1 = np.array(data[i - 1]) - np.array(data[i - 1])
            else:
                n1 = np.array(data[i - 1]) - np.array(data[i - 1 - 1])
            returden_list.append(n1.tolist())
        return returden_list

    def reformat_data(self, old_series, new_series):
        new_s = []
        for i, s in enumerate(old_series):
            s['data'] = new_series[i]
            new_s.append(s)
        return new_s

    def formatter(self, queryset):
        bt_categories = []
        series = []
        range_series = []

        for (_, name) in REGION_LIST:
            bt_categories.append(name)

        tp_categories = ['01', '02']

        queryset = {x.time_server: x for x in queryset}
        for k, q in queryset.items():
            for cat in tp_categories:
                chart_data = [float(v.value1) if cat == '01' else float(v.value2) for v in q.votings.all().order_by('region')]
                series.append({
                    'server_date': f"Waktu server pantau : <b>{q.create_at.strftime('%Y-%m-%d %H:%M:%S')}</b>",
                    'kpu_ts': f"Waktu server KPU : <b>{q.time_server}</b>",
                    'showInLegend': False,
                    'stacking': True,
                    'stack': cat,
                    'data': chart_data,
                    'main_data': chart_data
                })

        series_data_1 = []
        series_data_2 = []
        series_1, series_2 = [], []
        for s in series:
            if s['stack'] == '01':
                series_1.append(s)
                series_data_1.append(s['data'])
            else:
                series_2.append(s)
                series_data_2.append(s['data'])

        series_data_11 = self.series_substractor(series_data_1)
        series_data_22 = self.series_substractor(series_data_2)

        s1_new = self.reformat_data(series_1, series_data_11)
        s2_new = self.reformat_data(series_2, series_data_22)
        newer_series = s1_new + s2_new

        return {
            'title': 'Grafik pemantauan perkembangan suara SINTUNG KPU dari waktu ke waktu',
            'bt_categories': sorted(bt_categories),
            'tp_categories': tp_categories * len(bt_categories),
            'series': newer_series,
            'total_title': 'Pertambahan suara',
            'total_main_title': 'Total suara paslon'
        }

    def get(self, request):
        return Response(
            data=self.formatter(self.get_queryset()),
            status=status.HTTP_200_OK
        )


class PemiluChartRangeMergeApiView(GenericAPIView):
    def get_start_date(self, sdt):
        return sdt.strftime('%Y-%m-%d') + ' 00:00'

    def get_end_date(self, edt):
        return edt.strftime('%Y-%m-%d') + ' 23:59'

    def get_queryset(self):
        if 'time' in self.request.GET:
            param = self.request.GET['time']
            start = date.today()
            end = date.today()

            if param == 'today':
                pass
            elif param == 'weeks':
                start = start - timedelta(days=7)
            elif param == 'month':
                days = monthrange(start.year, start.month)
                start = start - timedelta(days=days[1])
            else:
                raise Http404

            return models.TimeCrawling.objects.distinct('time_server').filter(create_at__range=[
                self.get_start_date(start),
                self.get_end_date(end),
            ])
        return models.TimeCrawling.objects.order_by('-time_server').distinct().all()[:25]

    def separate_series(self, data):
        series_1 = []
        series_2 = []
        for s in series:
            if s['stack'] == '01':
                series_1.append(s['data'])
            else:
                series_2.append(s['data'])

        return series_1, series_2

    def series_substractor(self, series):
        returden_list = []
        data = sorted(series)
        for i in range(len(data), 0, -1):
            if i == 1:
                n1 = np.array(data[i - 1]) - np.array(data[i - 1])
            else:
                n1 = np.array(data[i - 1]) - np.array(data[i - 1 - 1])
            returden_list.append(n1.tolist())
        return returden_list

    def reformat_data(self, old_series, new_series):
        new_s = []
        for i, s in enumerate(old_series):
            s['data'] = new_series[i]
            s['stack'] = ''
            new_s.append(s)
        return new_s

    def formatter(self, queryset):
        bt_categories = []
        series = []
        range_series = []

        for (_, name) in REGION_LIST:
            bt_categories.append(name)

        tp_categories = ['01', '02']

        queryset = {x.time_server: x for x in queryset}
        for k, q in queryset.items():
            for cat in tp_categories:
                qs_by_region = q.votings.all().order_by('region')
                series.append({
                    'server_date': f"Waktu server pantau : <b>{q.create_at.strftime('%Y-%m-%d %H:%M:%S')}</b>",
                    'kpu_ts': f"Waktu server KPU : <b>{q.time_server}</b>",
                    'showInLegend': False,
                    'stacking': True,
                    'stack': cat,
                    'data': [float(v.value1) if cat == '01' else float(v.value2) for v in qs_by_region],
                    'nolsatu_data': [float(v.value1) for v in qs_by_region],
                    'noldua_data': [float(v.value2) for v in qs_by_region],
                    'main_data': [float(v.value1) + float(v.value2) for v in qs_by_region]
                })

        series_data_1 = []
        series_data_2 = []
        series_1, series_2 = [], []
        for s in series:
            if s['stack'] == '01':
                series_1.append(s)
                series_data_1.append(s['data'])
            else:
                series_2.append(s)
                series_data_2.append(s['data'])

        series_data_11 = self.series_substractor(series_data_1)
        series_data_22 = self.series_substractor(series_data_2)

        series_data_33 = np.array(series_data_11, dtype='int32') + np.array(series_data_22, dtype='int32')

        newer_series = self.reformat_data(series_1, series_data_33.tolist())
        # s2_new = self.reformat_data(series_2, series_data_22)
        # newer_series = s1_new + s2_new

        return {
            'title': 'Grafik Akumulatif pemantauan perkembangan suara SINTUNG KPU dari waktu ke waktu',
            'bt_categories': sorted(bt_categories),
            'tp_categories': tp_categories * len(bt_categories),
            'series': newer_series,
            'total_title': 'Total pertambahan suara',
            'total_main_title': 'Total gabungan suara'
        }

    def get(self, request):
        return Response(
            data=self.formatter(self.get_queryset()),
            status=status.HTTP_200_OK
        )


class PemiluChartAccumulationApiView(GenericAPIView):
    def get_start_date(self, sdt):
        return sdt.strftime('%Y-%m-%d') + ' 00:00'

    def get_end_date(self, edt):
        return edt.strftime('%Y-%m-%d') + ' 23:59'

    def get_queryset(self):
        if 'time' in self.request.GET:
            param = self.request.GET['time']
            start = date.today()
            end = date.today()

            if param == 'today':
                pass
            elif param == 'weeks':
                start = start - timedelta(days=7)
            elif param == 'month':
                days = monthrange(start.year, start.month)
                start = start - timedelta(days=days[1])
            else:
                raise Http404

            return models.TimeCrawling.objects.distinct('time_server').filter(create_at__range=[
                self.get_start_date(start),
                self.get_end_date(end),
            ])
        return models.TimeCrawling.objects.order_by('-time_server').distinct().all()[:25]

    def formatter(self, queryset):
        bt_categories = []
        series = []

        for (_, name) in REGION_LIST:
            bt_categories.append(name)

        tp_categories = ['01', '02']

        queryset = {x.time_server: x for x in queryset}
        for k, q in queryset.items():
            for cat in tp_categories:
                series.append({
                    'server_date': f"Waktu server pantau : <b>{q.create_at.strftime('%Y-%m-%d %H:%M:%S')}</b>",
                    'kpu_ts': f"Waktu server KPU : <b>{q.time_server}</b>",
                    'showInLegend': False,
                    'stacking': True,
                    'stack': cat,
                    'data': [float(v.value1) if cat == '01' else float(v.value2)
                             for v in q.votings.all().order_by('region')]
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
            'title': 'Grafik pemantauan perolehan suara SINTUNG KPU dari waktu ke waktu',
            'bt_categories': sorted(bt_categories),
            'tp_categories': tp_categories,
            'series': series,
            'total_title': 'Total suara'
        }

    def get(self, request):
        return Response(
            data=self.formatter(self.get_queryset()),
            status=status.HTTP_200_OK
        )


class PemiluChartTotalApiView(GenericAPIView):

    def get_object(self):
        return models.TimeCrawling.objects.all()[0]

    def get(self, request):
        obj = self.get_object()
        paslon_nolsatu_data = {
            'name': "(01) Ir. H. JOKO WIDODO - Prof. Dr. (H.C) KH. MA'RUF AMIN",
            'y': obj.total_nolsatu,
            'percentage': (obj.total_nolsatu / obj.total_suara) * 100 if obj.total_suara != 0 else 0
        }
        paslon_noldua_data = {
            'name': "(02) H. PRABOWO SUBIANTO - SANDIAGA SALAHUDIN UNO",
            'y': obj.total_noldua,
            'percentage': (obj.total_noldua / obj.total_suara) * 100 if obj.total_suara != 0 else 0
        }
        response = {
            'title': 'HASIL HITUNG SUARA PEMILU PRESIDEN & WAKIL PRESIDEN RI 2019 (sumber : <a href="https://pemilu2019.kpu.go.id/">https://pemilu2019.kpu.go.id/</a>)',
            'process_tps': obj.process_tps,
            'total_tps': obj.total_tps,
            'percentage_tps': '%.5f' % obj.percentage_tps,
            'series': [{
                'name': 'SUARA',
                'colorByPoint': True,
                'data': [paslon_noldua_data, paslon_nolsatu_data]
            }],
        }

        return Response(
            data=response,
            status=status.HTTP_200_OK
        )

class PemiluChartRegionRangeMergeApiView(GenericAPIView):
    def get_start_date(self, sdt):
        return sdt.strftime('%Y-%m-%d') + ' 00:00'

    def get_end_date(self, edt):
        return edt.strftime('%Y-%m-%d') + ' 23:59'

    def get_queryset(self):
        if 'time' in self.request.GET:
            param = self.request.GET['time']
            start = date.today()
            end = date.today()

            if param == 'today':
                pass
            elif param == 'weeks':
                start = start - timedelta(days=7)
            elif param == 'month':
                days = monthrange(start.year, start.month)
                start = start - timedelta(days=days[1])
            else:
                raise Http404

            return models.TimeCrawling.objects.distinct('time_server').filter(create_at__range=[
                self.get_start_date(start),
                self.get_end_date(end),
            ])
        return models.TimeCrawling.objects.order_by('-time_server').distinct().all()[:25]

    def separate_series(self, data):
        series_1 = []
        series_2 = []
        for s in series:
            if s['stack'] == '01':
                series_1.append(s['data'])
            else:
                series_2.append(s['data'])

        return series_1, series_2

    def series_substractor(self, series):
        returden_list = []
        data = sorted(series)
        for i in range(len(data), 0, -1):
            if i == 1:
                n1 = np.array(data[i - 1]) - np.array(data[i - 1])
            else:
                n1 = np.array(data[i - 1]) - np.array(data[i - 1 - 1])
            returden_list.append(n1.tolist())
        return returden_list

    def reformat_data(self, old_series, new_series):
        new_s = []
        for i, s in enumerate(old_series):
            s['data'] = new_series[i]
            s['stack'] = ''
            new_s.append(s)
        return new_s

    def formatter(self, queryset):
        bt_categories = []
        series = []
        range_series = []

        for (_, name) in REGION_LIST:
            bt_categories.append(name)

        tp_categories = ['01', '02']

        queryset = {x.time_server: x for x in queryset}
        for k, q in queryset.items():
            for cat in tp_categories:
                qs_by_region = q.votings.all().order_by('region')
                series.append({
                    'server_date': f"Waktu server pantau : <b>{q.create_at.strftime('%Y-%m-%d %H:%M:%S')}</b>",
                    'kpu_ts': f"Waktu server KPU : <b>{q.time_server}</b>",
                    'showInLegend': False,
                    'stacking': True,
                    'stack': cat,
                    'data': [float(v.value1) if cat == '01' else float(v.value2) for v in qs_by_region],
                    'nolsatu_data': [float(v.value1) for v in qs_by_region],
                    'noldua_data': [float(v.value2) for v in qs_by_region],
                    'main_data': [float(v.value1) + float(v.value2) for v in qs_by_region]
                })

        series_data_1 = []
        series_data_2 = []
        series_1, series_2 = [], []
        for s in series:
            if s['stack'] == '01':
                series_1.append(s)
                series_data_1.append(s['data'])
            else:
                series_2.append(s)
                series_data_2.append(s['data'])

        series_data_11 = self.series_substractor(series_data_1)
        series_data_22 = self.series_substractor(series_data_2)

        series_data_33 = np.array(series_data_11, dtype='int32') + np.array(series_data_22, dtype='int32')

        newer_series = self.reformat_data(series_1, series_data_33.tolist())
        # s2_new = self.reformat_data(series_2, series_data_22)
        # newer_series = s1_new + s2_new

        return {
            'title': 'Grafik Akumulatif pemantauan perkembangan suara SINTUNG KPU dari waktu ke waktu',
            'bt_categories': sorted(bt_categories),
            'tp_categories': tp_categories * len(bt_categories),
            'series': newer_series,
            'total_title': 'Total pertambahan suara',
            'total_main_title': 'Total gabungan suara'
        }

    def get(self, request):
        return Response(
            data=self.formatter(self.get_queryset()),
            status=status.HTTP_200_OK
        )
