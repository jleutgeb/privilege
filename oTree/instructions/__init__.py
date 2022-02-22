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


def creating_session(subsession):
    players = subsession.get_players()
    i = 0
    for p in players:
        p.privilege = i % 2 == 0
        p.participant.privilege = p.privilege
        if subsession.session.config['treatment'] == 'qL_high':
            p.qL_high = True
        elif subsession.session.config['treatment'] == 'qL_low':
            p.qL_high = False
        elif subsession.session.config['treatment'] == 'both':
            p.qL_high = math.ceil((i+1)/2) % 2 == 0
        p.participant.qL_high = p.qL_high
        i += 1


# PAGES
class Consent(Page):
    form_model = "player"
    form_fields = ["consent"]


class Instructions(Page):
    @staticmethod
    def vars_for_template(player: Player):
        return(
            dict(
                completion_payoff = cu(player.session.config['completion_payoff']),
                decision_payoff = cu(player.session.config['decision_payoff']),
                beliefs_payoff = cu(player.session.config['beliefs_payoff']),
            )
        )
    @staticmethod
    def before_next_page(player: Player, timeout_happened):
        player.participant.wait_page_arrival = time.time()

page_sequence = [Consent, Instructions]
