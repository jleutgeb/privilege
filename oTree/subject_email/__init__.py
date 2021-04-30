from otree.api import *

c = Currency

doc = """
Your app description
"""


class Constants(BaseConstants):
    name_in_url = 'subject_email'
    players_per_group = None
    num_rounds = 1


class Subsession(BaseSubsession):
    pass


class Group(BaseGroup):
    pass


class Player(BasePlayer):
    subject_email = models.StringField(
        label="Please enter your Email address"
    )


# PAGES
class MyPage(Page):
    form_model = 'player'
    form_fields = ['subject_email']

    @staticmethod
    def before_next_page(player: Player, timeout_happened):
        player.participant.label = player.subject_email


page_sequence = [MyPage]
