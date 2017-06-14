import trueskill


def update_trueskill_ratings(region_id, winner=None, loser=None):

    winner_ratings_dict = winner.ratings
    loser_ratings_dict = loser.ratings

    new_winner_rating, new_loser_rating = trueskill.rate_1vs1(
            winner_ratings_dict[region_id].trueskill_rating(),
            loser_ratings_dict[region_id].trueskill_rating()
    )
