from otree.api import *

c = Currency

doc = """
Your app description
"""


class Constants(BaseConstants):
    name_in_url = 'payment_info'
    players_per_group = None
    num_rounds = 1


class Subsession(BaseSubsession):
    pass


class Group(BaseGroup):
    pass


class Player(BasePlayer):
    pass


# PAGES
class PaymentInfo(Page):
    pass


page_sequence = [PaymentInfo]
