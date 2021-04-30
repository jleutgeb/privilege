from otree.api import *

c = Currency

doc = """
Simple Consent App
Players may only continue after clicking the consent button. 
"""


class Constants(BaseConstants):
    name_in_url = 'consent'
    players_per_group = None
    num_rounds = 1


class Subsession(BaseSubsession):
    pass


class Group(BaseGroup):
    pass


class Player(BasePlayer):
    consent = models.BooleanField(choices=[[True, 'Ja']])


# PAGES
class Consent(Page):
    form_model = "player"
    form_fields = ["consent"]


page_sequence = [Consent]
