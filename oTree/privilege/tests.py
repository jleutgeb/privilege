from otree.api import Currency as c, currency_range, expect, Bot
from . import *
import random


class PlayerBot(Bot):
    def play_round(self):
        yield Instructions
        yield Decision1, dict(
            choice=random.choice(range(0, Constants.number_of_choices)),
        )
        yield Info, dict(
            beliefs_high_ability=random.random(),
            beliefs_privileged=random.random(),
            beliefs_partner_high_ability=random.random(),
            beliefs_partner_privileged=random.random(),
        )
        if self.player.id_in_group == 1:
            yield FirstMover, dict(leads=random.choice([True, False]))
        if self.player.id_in_group == 2 and self.player.session.config["follower_choice"] and \
                self.player.get_others_in_group()[0].leads:
            yield SecondMover, dict(follows=random.choice([True, False]))
        if self.player.makes_leadership_choice:
            yield Decision2, dict(leadership_choice=random.choice([True, False]))
        yield Feedback

