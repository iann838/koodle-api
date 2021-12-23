from django.shortcuts import render
from django.views import View
from django.http.request import HttpRequest


class HomeView(View):

    def get(self, request: HttpRequest):
        return render(request, 'shops/home.html', {})
