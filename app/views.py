from django.shortcuts import render
from django.views.generic import TemplateView

from .regions import REGION_LIST
import re

# Create your views here.


class IndexView(TemplateView):
    template_name = 'index.html'

    def format_name_to_id(self, name):
        return re.sub('[^A-Za-z0-9]+', '', name.lower())

    def get_context_data(self, *args, **kwargs):
        ctx = super(IndexView, self).get_context_data(*args, **kwargs)
        ctx['regions'] = [{'code': code, 'name': name, 'id': self.format_name_to_id(name)} for (code, name) in REGION_LIST]
        return ctx
