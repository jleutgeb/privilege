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
    name = models.stringField(
        label="Please enter your name as it appears on your bank account"
    )
    IBAN = models.stringField(
        label="Please enter your IBAN"
    )
    BIC = models.stringField(
        label="Please enter your BIC"
    )
    subject_email = models.StringField(
        label="Please enter your Email address"
    )


# PAGES
class MyPage(Page):
    form_model = 'player'
    form_fields = ['name', 'IBAN', 'BIC', 'subject_email']

    @staticmethod
    def before_next_page(player: Player, timeout_happened):
        player.participant.label = player.subject_email


page_sequence = [MyPage]
