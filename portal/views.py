from django.shortcuts import render
from django.http import HttpResponseRedirect
from django import views

# Create your views here.

class IndexView(views.View):

    def get(self, request):
        return render(request, "portal/index.html")