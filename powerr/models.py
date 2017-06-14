import uuid

import trueskill
from django.contrib.postgres.fields import ArrayField
from django.db import models


class Player(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.TextField()
    ratings = ArrayField(models.TextField())
    regions = ArrayField(models.TextField())
    aliases = ArrayField(models.TextField())

    def has_alias(self, alias):
        return alias in self.aliases


class Tournament(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.TextField()
    type = models.CharField(max_length=30)
    date = models.DateField()
    region = models.TextField()
    url = models.TextField()
    matches = ArrayField(models.TextField())
    players = ArrayField(models.TextField())


class Match(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    winner = models.TextField()
    loser = models.TextField()
    excluded = models.BooleanField()
    result = models.TextField()

    def __str__(self):
        return "%s > %s" % (self.winner, self.loser)

    def has_players(self, p1, p2):
        return (self.winner == p1 and self.loser == p2) or \
               (self.winner == p2 and self.loser == p1)

    def has_player(self, id):
        return self.winner == id or self.loser == id

    def did_player_win(self, player_id):
        return self.winner == player_id

    def get_opposing_player_id(self, id):
        if self.winner == id:
            return self.loser
        elif self.loser == id:
            return self.winner
        else:
            return None

    def to_json(self):
        return self.id


class Rating(models.Model):
    mu = models.FloatField(default=25.)
    sigma = models.FloatField(default=25. / 3)

    def convert_to_trueskill(self):
        return trueskill.Rating(mu=self.mu, sigma=self.sigma)

    @classmethod
    def convert_from_trueskill(cls, true):
        return Rating(mu=true.mu, sigma=true.sigma)
