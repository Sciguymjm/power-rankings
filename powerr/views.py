import uuid

import challonge
from django.http import Http404
from django.shortcuts import render, redirect

import creds
from powerr import skill_util, models
from powerr.challonge_util import load_tournament
from powerr.models import Match, Player, Rating, Tournament

# Create your views here.
challonge.set_credentials("Sciguymjm", creds.CHALLONGE_API_KEY)


def home(request):
    rating_set = []
    for user in Player.objects.all():
        if len(user.ratings[0]) == 0:
            skill_util.add_default_skill_ratings()
        r = Rating.objects.filter(id=user.ratings[0]).first()
        r.mu -= 3 * r.sigma  #
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
            match.tournament = Tournament.objects.filter(matches__contains=[str(match.id)]).first()
            matches.append(match)
    return render(request, template_name="player.html", context={"player": play, "matches": sorted(matches, key=lambda x: x.tournament.date, reverse=True)})


def load_challonge(request, url):
    if request.user.is_superuser:
        t = load_tournament(url)
        print "Success: ", t.name
        return redirect("/")
    raise Http404()


def list_ratings(request):
    pass


def full_update_ratings(request, region):
    if request.user.is_superuser:
        players = Player.objects.all()
        for p in players:
            r = Rating.objects.filter(id=p.ratings[int(region)]).first()
            r.mu = 25.
            r.sigma = 25. / 3
            r.save()
        ts = Tournament.objects.filter(region=models.REGIONS[int(region)]).order_by("date").all()
        for t in ts:
            matches = t.matches
            for mat in matches:
                m = Match.objects.filter(id=mat).first()
                winner = Player.objects.filter(id=m.winner).first()
                loser = Player.objects.filter(id=m.loser).first()
                skill_util.update_trueskill_ratings(int(region), winner=winner, loser=loser)
        return redirect("/reset")
    raise Http404()


def add_alias(request, player, alias):
    if request.user.is_superuser:
        p = Player.objects.filter(name__iexact=player).first()
        p.aliases.append(alias)
        p.save()
        return redirect("/")
    raise Http404()


def rescan_all_tournaments(request):
    if request.user.is_superuser:
        ts = Tournament.objects.filter(type="challonge").all()
        for t in ts:
            load_tournament(t.url.split("/")[-1])
        return redirect("/load/reload_all/0")
    else:
        raise Http404()


def delete_all_but_tournaments(request):
    if request.user.is_superuser:
        Player.objects.all().delete()
        Rating.objects.all().delete()
        Match.objects.all().delete()
        return redirect('/reload_all')
    raise Http404()


def admin(request):
    if request.user.is_superuser:
        return render(request, "admin.html")
    else:
        raise Http404()


def about(request):
    return render(request, "about.html")


def tournaments(request):
    t = Tournament.objects.order_by('-date').all()
    return render(request, "tournaments.html", context={"tournaments": t})


def show_tournament(request, id):
    id = uuid.UUID(id)
    t = Tournament.objects.filter(id=id).first()
    c = challonge.tournaments.show(t.url.split("/")[-1])
    return render(request, "tournament.html",
                  context={"tourney_url": c["full_challonge_url"], "t": t, "url": c["live_image_url"]})
