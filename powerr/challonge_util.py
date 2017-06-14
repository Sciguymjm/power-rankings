import creds
import challonge
import trueskill
challonge.set_credentials("Sciguymjm", creds.CHALLONGE_API_KEY)
tournament = challonge.tournaments.show("lar2wc6l", include_participants=True)

print(tournament["id"]) # 3272
print(tournament["name"]) # My Awesome Tournament

# Retrieve the participants for a given tournament.
participants = challonge.participants.index(tournament["id"])
print(len(participants)) # 13
for p in participants:
    print p['display_name']

matches = challonge.matches.index(tournament["id"])
print matches[0]

def update_trueskill_ratings(region_id, winner=None, loser=None):
    winner_ratings_dict = winner.ratings
    loser_ratings_dict = loser.ratings

    new_winner_rating, new_loser_rating = trueskill.rate_1vs1(
            winner_ratings_dict[region_id].trueskill_rating(),
            loser_ratings_dict[region_id].trueskill_rating()
    )
