import trueskill

from powerr.models import Player, Rating

def update_trueskill_ratings(region_id, winner=None, loser=None):
    winner_ratings_dict = winner.ratings
    loser_ratings_dict = loser.ratings

    new_winner_rating, new_loser_rating = trueskill.rate_1vs1(
        Rating.objects.filter(id=winner_ratings_dict[region_id]).first().convert_to_trueskill(),
        Rating.objects.filter(id=loser_ratings_dict[region_id]).first().convert_to_trueskill()
    )

    winner_rating = Rating.objects.filter(id=winner.ratings[region_id]).first()
    winner_rating.mu = new_winner_rating.mu
    winner_rating.sigma = new_winner_rating.sigma
    winner_rating.save()

    loser_rating = Rating.objects.filter(id=loser.ratings[region_id]).first()
    loser_rating.mu = new_loser_rating.mu
    loser_rating.sigma = new_loser_rating.sigma
    loser_rating.save()


def add_default_skill_ratings():
    for p in Player.objects.filter(ratings=[]).all():
        p.ratings = []
        r = Rating()
        r.save()
        p.ratings.append(r.id)
        p.save()
