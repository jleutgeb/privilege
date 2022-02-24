from otree.api import Currency as c, currency_range, expect, Bot
from . import *
import random


class PlayerBot(Bot):
    def play_round(self):
        yield Decision
        yield Submission(Beliefs, dict(bi=random.random(), bj=random.random()), check_html=False)
        yield Leadership, dict(leads=random.choice([True, False]))
        yield Survey, dict(
            gender=random.choice(['m', 'f', 'o', 'ns']),
            age=random.randint(0,99),
            language=random.choice(['English', 'Other']),
            residence=random.choice(['UK', 'Other']),
            nationality=random.choice(['UK', 'Other']),
            student=random.choice([True, False]),
            employment=random.choice([True, False]),
            zip=random.choice(['idk', 'uk', 'zip', 'codes', 'by', 'heart']),
            comments='I am a bot'
            )
        yield Submission(Completion, check_html=False)
