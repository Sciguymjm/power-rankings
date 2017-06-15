import challonge

import creds
from powerr import skill_util
from powerr.models import Match, Tournament, Player

challonge.set_credentials("Sciguymjm", creds.CHALLONGE_API_KEY)
aliases = {}


def load_tournament(id):  # loads tournament from a given challonge id (http://challonge.com/xxxxxx), where xxxxxx is id
    with open("alias.txt") as f:  # loads alias list (anthony: there is probably a better way to handle this)
        lines = f.readlines()
        for line in lines:
            l = line.split(":")
            if "," in l[1]:
                n = l[1].split(",")
                aliases[l[0]] = [j.lower().replace("\n", "").replace("\r", "") for j in n]
            else:
                aliases[l[0]] = [l[1].lower().replace("\n", "").replace("\r", "")]

    def is_alias(s):  # checks if the given name is an alias TODO: Combine this with get_alias
        s = s.lower()
        for i in range(len(aliases)):
            print aliases.values()[i]
            if s in aliases.values()[i]:
                return True
        return False

    def get_alias(s):
        s = s.lower()
        for i in range(len(aliases)):
            if s in aliases.values()[i]:
                return aliases.keys()[i]

    tournament = challonge.tournaments.show(id)  # retrieves challonge tourney info from api
    t = Tournament()  # creates a new tournament
    t.name = tournament["name"]  # sets the name
    t.type = "challonge"  # set the type (not necessary right now, but for later if we add smash.gg)
    t.date = tournament["started_at"]  # just the date, time is not needed
    t.region = "NEU"  # this needs to be able to be changed using the URL, for later use
    t.url = tournament["full_challonge_url"]  # to save for later
    t.players = []  # will be filled with values
    t.matches = []
    # if we already have this tournament, don't duplicate it, just re-read the matches + players
    if Tournament.objects.filter(url=tournament["full_challonge_url"]).first() is not None:
        t = Tournament.objects.filter(url=tournament["full_challonge_url"]).first()
        t.matches = []
        t.players = []
    # Retrieve the participants for a given tournament.
    participants = challonge.participants.index(tournament["id"])
    for p in participants:
        # create a new player
        pl = Player()
        # set his/her region to our main region TODO: will need to be set using URL argument
        # Also TODO: sometimes the regions are referred to by name. but in database referred to by id (from models.py)
        pl.regions = ["NEU"]
        # if this person goes by another name (why can't people just pick one name?)
        if is_alias(p["display_name"]):
            # replaces all later instances of display_name with the actual name, for simplicity
            p["display_name"] = get_alias(p["display_name"])
        # set the name of this person
        pl.name = p["display_name"]
        # player doesn't have any ratings
        pl.ratings = []
        # or aliases, but this can be changed later
        pl.aliases = []
        # players may already be in the database
        ps = Player.objects.filter(name__iexact=p["display_name"].lower()).first()

        if ps is None:
            # if this player doesn't already exist, create a new one
            pl.save()
            t.players.append(pl.id)
        else:
            # if this player does exist, do nothing but add them to the tournament
            t.players.append(ps.id)

    # finds the player name by the CHALLONGE ID, not actual id
    def find_player_by_id(id):
        return [i for i in participants if i['id'] == id][0]

    # gets the matches for this tournament
    matches = challonge.matches.index(tournament["id"])

    for match in matches:
        # some tourneys are not complete, so there is no winner
        if match['winner_id'] is None:
            continue
        # get the names of the winner and loser (uses display names from aliases section)
        winner_name = find_player_by_id(match['winner_id'])['display_name']
        loser_name = find_player_by_id(match['loser_id'])['display_name']
        # find that player in the database
        winner = Player.objects.filter(name__iexact=winner_name.lower()).first()
        loser = Player.objects.filter(name__iexact=loser_name.lower()).first()
        # create a new match
        m = Match()
        m.winner = winner.id
        m.loser = loser.id
        m.result = match['scores_csv']  # e.g. "2-1" for later use, maybe
        m.excluded = False  # if we want to exclude this match, i.e. sandbagging or mixups
        t.matches.append(m.id)
        m.save()
    t.save()
    # add empty skill ratings to all the empty players
    skill_util.add_default_skill_ratings()
    return t
