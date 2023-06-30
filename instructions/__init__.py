from otree.api import *
import math
import time

doc = """
Your app description
"""


class C(BaseConstants):
    NAME_IN_URL = 'instructions'
    PLAYERS_PER_GROUP = None
    NUM_ROUNDS = 1


class Subsession(BaseSubsession):
    pass


class Group(BaseGroup):
    pass


class Player(BasePlayer):
    consent = models.BooleanField(choices=[[True, 'Yes']])
    privilege = models.BooleanField()
    qL_high = models.BooleanField()


# PAGES
class Consent(Page):
    form_model = "player"
    form_fields = ["consent"]


class Outline(Page):
    pass


page_sequence = [Consent, Outline]
