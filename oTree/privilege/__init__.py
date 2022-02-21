from curses.ascii import NAK
import pkgutil
from otree.api import *
import random
import math

c = Currency

doc = """

"""


class C(BaseConstants):
    NAME_IN_URL = 'experiment'
    PLAYERS_PER_GROUP = 2
    NUM_ROUNDS = 1


class Subsession(BaseSubsession):
    pass


class Group(BaseGroup):
    payment_choices = models.BooleanField() # variable if group is paid for leadership or beliefs (to eliminate hedging)
    completion_payoff = models.CurrencyField()
    decision_payoff = models.CurrencyField()
    beliefs_payoff = models.CurrencyField()
    made_leadership_choice = models.BooleanField(initial=False) # whether all players in the group made the leadership choice
    leader = models.IntegerField()
    phiP = models.FloatField() # chance that privileged player is high type
    phiU = models.FloatField() # chance that underprivileged player is high type
    qH = models.FloatField() # chance that high type is correct
    qL = models.FloatField() # chance that low type is correct
    pkP = models.FloatField()
    pkU = models.FloatField()
    qL_high = models.BooleanField() # variable for treatment


class Player(BasePlayer):
    ## privilege game
    high = models.BooleanField()  # H type or not (L)
    privilege = models.BooleanField()  # P type or not (U)
    correct = models.BooleanField()  # was the player correct
    kudos = models.BooleanField()  # does the player receive kudos
    q = models.FloatField() # player's actual chance

    leads = models.BooleanField()  # save whether the subject wants to lead
    leadership_correct = models.BooleanField()  # is the leader correct (conditional on being the leader)
    made_leadership_choice = models.BooleanField(initial=False) # whether the player made the leadership choice

    # beliefs about own and partner's types 
    bi = models.FloatField(min=0, max=1)
    bj = models.FloatField(min=0, max=1)

    obi = models.BooleanField()  # does the player receive prize for beliefs about self
    obj = models.BooleanField()  # does the player receive prize for beliefs about partner


    ## survey
    gender = models.StringField(
        choices=[
            ['m', 'male'],
            ['f', 'female'],
            ['o', 'other'],
            ['ns', "I'd rather not say"]
        ],
        label="Gender"
    )
    age = models.IntegerField(min=0, max=100, label="How old are you? (in years)")
    strategy = models.LongStringField(blank=True,
                                      label="Please describe your thought process or your strategy in this experiment. (optional)")
    comments = models.LongStringField(blank=True,
                                      label="Do you have any other comments or questions about this study? (optional)")


# FUNCTIONS
# function to calculate whether a prize is awarded by the binarized scoring rule
def probability_prize_bsr(statement, belief):
    if statement:
        return 1 - (1 - belief) ** 2
    else:
        return 1 - belief ** 2


def draw_prize_bsr(statement, belief):
    draw = random.random()
    if draw < probability_prize_bsr(statement, belief):
        return True
    else:
        return False


# PAGES
def group_by_arrival_time_method(subsession, waiting_players):
    print('in group_by_arrival_time_method')
    PH_players = [p for p in waiting_players if p.participant.privilege and p.participant.qL_high]
    PL_players = [p for p in waiting_players if p.participant.privilege and not p.participant.qL_high]
    
    UH_players = [p for p in waiting_players if not p.participant.privilege and p.participant.qL_high]
    UL_players = [p for p in waiting_players if not p.participant.privilege and not p.participant.qL_high]

    if len(PH_players) >= 1 and len(UH_players) >= 1:
        print('about to create a qL_high group')
        return [PH_players[0], UH_players[0]]
    if len(PL_players) >= 1 and len(UL_players) >= 1:
        print('about to create a qL_low group')
        return [PL_players[0], UL_players[0]]
    print('not enough players yet to create a group')


class Matching(WaitPage):
    group_by_arrival_time = True
    def after_all_players_arrive(group: Group):
        group.payment_choices = random.random() < 0.5
        group.completion_payoff = group.session.config['completion_payoff']
        group.decision_payoff = group.session.config['decision_payoff']
        group.beliefs_payoff = group.session.config['beliefs_payoff']
        group.qL_high = all([p.participant.qL_high for p in group.get_players()])
        if group.qL_high:
            group.qL = group.session.config['qL_high']
        else:
            group.qL = group.session.config['qL_low']
        group.qH = group.session.config['qH']
        group.phiP = group.session.config['phiP']
        group.phiU = group.session.config['phiU']
        group.pkP = group.session.config['pkP']
        group.pkU = group.session.config['pkU']

        if group.qL_high:
            group.qL = group.session.config['qL_high']
        else:
            group.qL = group.session.config['qL_low']

        for p in group.get_players():
            p.privilege = p.participant.privilege
            if p.privilege:
                p.high = random.random() < p.group.phiP
            else:
                p.high = random.random() < p.group.phiU
            if p.high:
                p.q = p.group.qH
            else:
                p.q = p.group.qL
            p.correct = random.random() < p.q
            p.leadership_correct = random.random() < p.q
            if p.correct and p.privilege and random.random() < p.group.pkP:
                p.kudos = True
            elif p.correct and not p.privilege and random.random() < p.group.pkU:
                p.kudos = True
            else:
                p.kudos = False


class Decision(Page):
    pass


class Beliefs(Page):
    # on this page the player reports their beliefs
    form_model = "player"
    form_fields = ["bi", "bj"]
    @staticmethod
    def vars_for_template(player: Player):
        return dict(
            partner_kudos = player.get_others_in_group()[0].kudos
        )

    @staticmethod
    def before_next_page(player: Player, timeout_happened):
        player.obi = draw_prize_bsr(player.high, player.bi)
        player.obj = draw_prize_bsr(player.get_others_in_group()[0].high, player.bj)
        if not player.group.payment_choices:
            if player.obi:
                player.payoff += player.group.beliefs_payoff
            if player.obj:
                player.payoff += player.group.beliefs_payoff


class Leadership(Page):
    # players say whether they want to lead
    form_model = "player"
    form_fields = ["leads"]
    @staticmethod
    def before_next_page(player: Player, timeout_happened):
        player.made_leadership_choice = True
        group = player.group
        players = group.get_players()
        partner = player.get_others_in_group()[0]
        if partner.made_leadership_choice:
            group.made_leadership_choice = True
            p1 = group.get_player_by_id(1)
            p2 = group.get_player_by_id(2)
            if p1.leads and not p2.leads:
                player.group.leader = 1
            elif not p1.leads and p2.leads:
                player.group.leader = 2
            else:
                player.group.leader = random.randint(1,2)
            leader = group.get_player_by_id(player.group.leader)
            if player.group.payment_choices and leader.leadership_correct:
                for p in players:
                    p.payoff += player.group.decision_payoff


class Survey(Page):
    form_model = "player"
    form_fields = ['gender', 'age', 'strategy', 'comments']
    @staticmethod
    def before_next_page(player: Player, timeout_happened):
        player.payoff += player.group.completion_payoff


class Completion(Page):
    # send players back to prolific
    form_model = "player"

    @staticmethod
    def vars_for_template(player: Player):
        if not player.group.made_leadership_choice:
            leadership_correct = 'NA'
        else:
            leadership_correct = player.group.get_player_by_id(player.group.leader).leadership_correct
        return dict(
            leadership_correct = leadership_correct,
            bi = int(round(player.bi * 100,0)),
            bj = int(round(player.bj * 100,0)),
            partner_high = player.get_others_in_group()[0].high,
            prob_bi = round(probability_prize_bsr(player.high, player.bi), 4) * 100,
            prob_bj = round(probability_prize_bsr(player.get_others_in_group()[0].high, player.bj), 4) * 100,
        )

    @staticmethod              
    def js_vars(player):
        return dict(
            completion_link=player.subsession.session.config['completion_link'],
        )


page_sequence = [Matching, Decision, Beliefs, Leadership, Survey, Completion]
