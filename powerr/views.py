from django.http import HttpResponse
from django.shortcuts import render

# Create your views here.
def home(request):
    return HttpResponse("You're looking at the homepage.")


def player(request, player):
    return HttpResponse("Player: " + player)