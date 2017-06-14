import challonge

import creds
from powerr.models import Match, Tournament, Player

challonge.set_credentials("Sciguymjm", creds.CHALLONGE_API_KEY)


def load_tournament(id):
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
    return t
