from django.http import HttpResponse
from django.shortcuts import render, redirect

# Create your views here.
from django.template import Context

from powerr.challonge_util import load_tournament


def home(request):
    return HttpResponse("You're looking at the homepage.")


def player(request, p):
    return render(request, template_name="player.html", context={"player": p})


def load_challonge(request, url):
    t = load_tournament(url)
    print "Success: ", t.name
    return redirect("/")