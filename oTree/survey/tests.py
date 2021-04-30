from otree.api import Currency as c, currency_range, expect, Bot
from . import *
import random


class PlayerBot(Bot):
    def play_round(self):
        yield Survey, dict(
            gender=random.choice(['m', 'f', 'o']),
            age=random.randint(0, 100),
            field="I'm a bot",
            semesters=random.randint(0, 100),
            strategy="I'm a bot",
            comments="I'm a bot",
        )

