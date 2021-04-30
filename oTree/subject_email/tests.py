from otree.api import Currency as c, currency_range, expect, Bot
from . import *
import random


class PlayerBot(Bot):
    def play_round(self):
        yield MyPage, dict(
            subject_email="bot@wzb.eu",
        )

