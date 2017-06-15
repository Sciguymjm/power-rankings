import challonge

import creds
from powerr import skill_util
from powerr.models import Match, Tournament, Player

challonge.set_credentials("Sciguymjm", creds.CHALLONGE_API_KEY)
aliases = {}


def load_tournament(id):
    with open("alias.txt") as f:
        lines = f.readlines()
        for line in lines:
            l = line.split(":")
            if "," in l[1]:
                n = l[1].split(",")
                aliases[l[0]] = [j.lower().replace("\n", "") for j in n]
            else:
                aliases[l[0]] = [l[1].lower().replace("\n", "")]

    def is_alias(s):
        s = s.lower()
        for i in range(len(aliases)):
            if s in aliases.values()[i]:
                return True
        return False

    def get_alias(s):
        s = s.lower()
        for i in range(len(aliases)):
            if s in aliases.values()[i]:
                return aliases.keys()[i]

    print get_alias("Randy for Ramsey")
    assert get_alias("Randy for Ramsey") == "Poodledeedoop"
    tournament = challonge.tournaments.show(id)
    t = Tournament()
    t.name = tournament["name"]
    t.type = "challonge"
    t.date = tournament["started_at"]
    t.region = "NEU"
    t.url = tournament["full_challonge_url"]
    t.players = []
    t.matches = []
    if Tournament.objects.filter(url=tournament["full_challonge_url"]).first() is not None:
        t = Tournament.objects.filter(url=tournament["full_challonge_url"]).first()
        t.matches = []
        t.players = []
    # Retrieve the participants for a given tournament.
    participants = challonge.participants.index(tournament["id"])
    for p in participants:
        pl = Player()
        pl.regions = ["NEU"]

        if is_alias(p["display_name"]):
            p["display_name"] = get_alias(p["display_name"])
        pl.name = p["display_name"]
        pl.ratings = []
        pl.aliases = []
        ps = Player.objects.filter(name__iexact=p["display_name"].lower()).first()

        if ps is None:
            pl.save()
            t.players.append(pl.id)
        else:
            t.players.append(ps.id)

    def find_player_by_id(id):
        return [i for i in participants if i['id'] == id][0]

    matches = challonge.matches.index(tournament["id"])

    for match in matches:
        if match['winner_id'] is None:
            continue
        winner_name = find_player_by_id(match['winner_id'])['display_name']
        loser_name = find_player_by_id(match['loser_id'])['display_name']

        winner = Player.objects.filter(name__iexact=winner_name.lower()).first()
        loser = Player.objects.filter(name__iexact=loser_name.lower()).first()

        m = Match()
        m.winner = winner.id
        m.loser = loser.id
        m.result = match['scores_csv']
        m.excluded = False
        t.matches.append(m.id)
        m.save()

    t.save()
    skill_util.add_default_skill_ratings()
    return t
