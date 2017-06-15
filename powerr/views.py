import uuid

from django.http import HttpResponse
from django.shortcuts import render, redirect

from powerr import skill_util, models, challonge_util
from powerr.challonge_util import load_tournament
from powerr.models import Match, Player, Rating, Tournament


# Create your views here.


def home(request):
    rating_set = []
    for user in Player.objects.all():
        if len(user.ratings[0]) == 0:
            skill_util.add_default_skill_ratings()
        r = Rating.objects.filter(id=user.ratings[0]).first()
        r.mu -= 3 * r.sigma #
        rating_set.append([user, r])
    rating_set = sorted(rating_set, key=lambda x: -x[1].mu)

    return render(request, "ratings.html", context={"rating_set": rating_set, "players": Player.objects.all()})


def player(request, p):
    print p
    id = uuid.UUID(p)
    play = Player.objects.filter(id=id).first()
    matches = []
    for match in Match.objects.all():
        if match.has_player(p):
            match.winner = Player.objects.filter(id=match.winner).first()
            match.loser = Player.objects.filter(id=match.loser).first()
            matches.append(match)
    return render(request, template_name="player.html", context={"player": play, "matches": matches})


def load_challonge(request, url):
    t = load_tournament(url)
    print "Success: ", t.name
    return redirect("/")


def list_ratings(request):
    pass


def full_update_ratings(request, region):
    players = Player.objects.all()
    for p in players:
        r = Rating.objects.filter(id=p.ratings[int(region)]).first()
        r.mu = 25.
        r.sigma = 25. / 3
        r.save()
    ts = Tournament.objects.filter(region=models.REGIONS[int(region)]).all()
    for t in ts:
        matches = t.matches
        for mat in matches:
            m = Match.objects.filter(id=mat).first()
            winnerid = m.winner
            loserid = m.loser
            winner = Player.objects.filter(id=winnerid).first()
            loser = Player.objects.filter(id=loserid).first()
            skill_util.update_trueskill_ratings(int(region), winner=winner, loser=loser)

    return redirect("/reset")


def add_alias(request, player, alias):
    p = Player.objects.filter(name__iexact=player).first()
    p.aliases.append(alias)
    p.save()
    return redirect("/")


def rescan_all_tournaments(request):
    ts = Tournament.objects.filter(type="challonge").all()
    for t in ts:
        load_tournament(t.url.split("/")[-1])
    return redirect("/reset")


def delete_all_but_tournaments(request):
    Player.objects.all().delete()
    Rating.objects.all().delete()
    Match.objects.all().delete()

    return redirect('/reset')

def admin(request):
    return render(request, "admin.html")

def about(request):
    return render(request, "about.html")