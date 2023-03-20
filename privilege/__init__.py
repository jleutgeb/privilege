from curses.ascii import NAK
import pkgutil
from otree.api import *
import random
import math
import time

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
    completion_payoff = models.CurrencyField() # payoff for completing the study
    decision_payoff = models.CurrencyField()  # payoff for scoring
    beliefs_payoff = models.CurrencyField() # payoff for beliefs
    made_leadership_choice = models.BooleanField(initial=False) # whether all players in the group made the leadership choice
    leader = models.IntegerField() # player ID of leader in group
    phiP = models.FloatField() # chance that privileged player is high type
    phiU = models.FloatField() # chance that underprivileged player is high type
    qH = models.FloatField() # chance that high type is correct
    qL = models.FloatField() # chance that low type is correct
    pkP = models.FloatField() # probability of receiving kudos when type P
    pkU = models.FloatField() # probability of receiving kudos when type U
    qL_high = models.BooleanField() # treatment variable


class Player(BasePlayer):
    ## privilege game
    high = models.BooleanField()  # H type or not (L)
    privilege = models.BooleanField()  # P type or not (U)
    correct = models.BooleanField()  # was the player correct
    kudos = models.BooleanField()  # does the player receive kudos
    q = models.FloatField() # player's actual chance

    leads = models.BooleanField(label="Do you want to play for the group?", choices=[[True, "Yes"], [False, "No"]])  # save whether the subject wants to lead
    leadership_correct = models.BooleanField()  # is the leader correct (conditional on being the leader)
    made_leadership_choice = models.BooleanField(initial=False) # whether the player made the leadership choice yet

    # beliefs about own and partner's types 
    bi = models.FloatField(min=0, max=1) # beliefs about being high type 
    bj = models.FloatField(min=0, max=1) # beliefs about partner being high type
    bi_first = models.BooleanField() # if true bi is first in the table, else bj is first

    obi = models.BooleanField()  # does the player receive prize for beliefs about self
    obj = models.BooleanField()  # does the player receive prize for beliefs about partner

    # no partner shows up
    no_partner = models.BooleanField(initial=False) # if no partner shows up, play against coomputer
    privilege_cp = models.BooleanField() # whether the computer player is type p
    high_cp = models.BooleanField() # whether the computer player is a high type
    q_cp = models.FloatField() # computer player's actual chance
    correct_cp = models.BooleanField() # whether computer player is correct
    kudos_cp = models.BooleanField() # does the computer player receive kudos
    leads_cp = models.BooleanField() # does the computer player lead
    leadership_correct_cp = models.BooleanField()  # is the leader correct (conditional on being the leader)

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
    language = models.StringField(
        choices=['English', 'Other'],
        label='What is your first language?'
    )
    residence = models.StringField(
        choices=['UK', 'Other'],
        label='What is your country of residence?'
    )
    nationality = models.StringField(
        choices=['UK', 'Other'],
        label='What is your nationality?'
    )
    student = models.BooleanField(
        choices=[[True, 'Yes'], [False, 'No']],
        label='Are you a student?'
    )
    employment = models.BooleanField(
        choices=[[True, 'Yes'], [False, 'No']],
        label='Are you currently employed?'
    )
    zip = models.StringField(
        label='Please enter the first two letters of your postcode'
    )
    comments = models.LongStringField(blank=True,
                                      label="Do you have any other comments or questions about this study? (optional)")


# FUNCTIONS
# function to calculate probability of assigning the price
def probability_prize_bsr(statement, belief):
    if statement:
        return 1 - (1 - belief) ** 2
    else:
        return 1 - belief ** 2

# function to calculate whether a prize is awarded by the binarized scoring rule
def draw_prize_bsr(statement, belief):
    draw = random.random()
    if draw < probability_prize_bsr(statement, belief):
        return True
    else:
        return False

# if a player is waiting too long for a partner, let them continue
def waiting_too_long(player):
    return time.time() - player.participant.wait_page_arrival > player.session.config['max_wait_time']


# PAGES
# this function specifies that when grouping players, they should come from different waiting bins
def group_by_arrival_time_method(subsession, waiting_players):
    # print('in group_by_arrival_time_method')
    # put players into waiting bins by privilege and treatment
    PH_players = [p for p in waiting_players if p.participant.privilege and p.participant.qL_high]
    PL_players = [p for p in waiting_players if p.participant.privilege and not p.participant.qL_high]
    
    UH_players = [p for p in waiting_players if not p.participant.privilege and p.participant.qL_high]
    UL_players = [p for p in waiting_players if not p.participant.privilege and not p.participant.qL_high]

    # if there is a partner available, create a group
    if len(PH_players) >= 1 and len(UH_players) >= 1:
        # print('about to create a qL_high group')
        return [PH_players[0], UH_players[0]]
    if len(PL_players) >= 1 and len(UL_players) >= 1:
        # print('about to create a qL_low group')
        return [PL_players[0], UL_players[0]]
    # print('not enough players yet to create a group')
    # if a player is waiting too long, let them play against a computer player
    for player in waiting_players:
        if waiting_too_long(player):
            player.no_partner = True
            return [player]


class Matching(WaitPage):
    group_by_arrival_time = True
    def after_all_players_arrive(group: Group):
        group.payment_choices = random.random() < 0.5 # randomly draw whether choices are paid (else beliefs)
        # gather group variables from the config/players
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
            p.bi_first = random.random() < 0.5 # randomize order in which beliefs are elicited
            # assign high/low types and their chance
            p.privilege = p.participant.privilege
            if p.privilege:
                p.high = random.random() < p.group.phiP
            else:
                p.high = random.random() < p.group.phiU
            if p.high:
                p.q = p.group.qH
            else:
                p.q = p.group.qL
            p.correct = random.random() < p.q # draw whether the player is correct
            p.leadership_correct = random.random() < p.q # draw whether the player would be correct if they become the leader (unkown to players at this point)
            # assign kudos
            if p.correct and p.privilege and random.random() < p.group.pkP:
                p.kudos = True
            elif p.correct and not p.privilege and random.random() < p.group.pkU:
                p.kudos = True
            else:
                p.kudos = False

            # same but when partner is a computer player
            if p.no_partner:
                p.privilege_cp = not p.privilege
                if p.privilege_cp:
                    p.high_cp = random.random() < p.group.phiP
                else:
                    p.high_cp = random.random() < p.group.phiU
                if p.high_cp:
                    p.q_cp = p.group.qH
                else:
                    p.q_cp = p.group.qL
                p.correct_cp = random.random() < p.q_cp
                p.leadership_correct_cp = random.random() < p.q_cp
                if p.correct_cp and p.privilege_cp and random.random() < p.group.pkP:
                    p.kudos_cp = True
                elif p.correct_cp and not p.privilege_cp and random.random() < p.group.pkU:
                    p.kudos_cp = True
                else:
                    p.kudos_cp = False


# this page is just here so subjects can click a button
class Decision(Page):
    pass


class Beliefs(Page):
    # on this page the player reports their beliefs
    form_model = "player"
    form_fields = ["bi", "bj"]
    @staticmethod
    def vars_for_template(player: Player):
        if not player.no_partner:
            partner_kudos = player.get_others_in_group()[0].kudos
        else:
            partner_kudos = player.kudos_cp
        return dict(
            partner_kudos = partner_kudos
        )

    @staticmethod
    def js_vars(player: Player):
        return dict(
            bi_first = player.bi_first
        )

    @staticmethod
    def before_next_page(player: Player, timeout_happened):
        player.obi = draw_prize_bsr(player.high, player.bi)
        if not player.no_partner:
            partner_high = player.get_others_in_group()[0].high
        else:
            partner_high = player.high_cp
        player.obj = draw_prize_bsr(partner_high, player.bj)
        # if choices are not paid, subjects receive payoffs for the accuracy of their beliefs
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
    def vars_for_template(player: Player):
        if not player.no_partner:
            partner_kudos = player.get_others_in_group()[0].kudos
        else:
            partner_kudos = player.kudos_cp
        return dict(
            partner_kudos = partner_kudos
        )
    
    @staticmethod
    def before_next_page(player: Player, timeout_happened):
        player.made_leadership_choice = True
        group = player.group
        players = group.get_players()
        # only execute the code to assign payoffs if both players in the group made the decision whether to lead
        if not player.no_partner and player.get_others_in_group()[0].made_leadership_choice:
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
            # if the leader is correct and choices are paid, both receive the payoff
            if player.group.payment_choices and leader.leadership_correct:
                for p in players:
                    p.payoff += player.group.decision_payoff
                    
        # if there is no partner, the computer partner must make a choice whether to lead. use simple bayesian updating.
        elif player.no_partner:
            group.made_leadership_choice = True
            # calculate prob of being high type from the perspective of computer player
            if player.kudos and player.privilege:
                prob_player = group.phiP * group.qH / (group.phiP * group.qH + (1 - group.phiP) * group.qL)
            elif player.kudos and not player.privilege:
                prob_player = group.phiU * group.qH / (group.phiU * group.qH + (1 - group.phiU) * group.qL)
            elif not player.kudos and player.privilege:
                prob_player = (group.phiP * (1 - group.qH) + group.phiP * group.qH * (1 - group.pkP)) / (group.phiP * (1 - group.qH) + group.phiP * group.qH * (1 - group.pkP) + (1 - group.phiP) * (1 - group.qL) + (1 - group.phiP) * group.qL * (1 - group.pkP))
            elif not player.kudos and not player.privilege:
                prob_player = (group.phiU * (1 - group.qH) + group.phiU * group.qH * (1 - group.pkP)) / (group.phiU * (1 - group.qH) + group.phiU * group.qH * (1 - group.pkP) + (1 - group.phiU) * (1 - group.qL) + (1 - group.phiU) * group.qL * (1 - group.pkP))

            if player.kudos_cp and player.privilege_cp:
                prob_cp = group.phiP * group.qH / (group.phiP * group.qH + (1 - group.phiP) * group.qL)
            elif player.kudos_cp and not player.privilege_cp:
                prob_cp = group.phiU * group.qH / (group.phiU * group.qH + (1 - group.phiU) * group.qL)
            elif not player.kudos_cp and player.privilege_cp:
                prob_cp = (group.phiP * (1 - group.qH) + group.phiP * group.qH * (1 - group.pkP)) / (group.phiP * (1 - group.qH) + group.phiP * group.qH * (1 - group.pkP) + (1 - group.phiP) * (1 - group.qL) + (1 - group.phiP) * group.qL * (1 - group.pkP))
            elif not player.kudos_cp and not player.privilege_cp:
                prob_cp = (group.phiU * (1 - group.qH) + group.phiU * group.qH * (1 - group.pkP)) / (group.phiU * (1 - group.qH) + group.phiU * group.qH * (1 - group.pkP) + (1 - group.phiU) * (1 - group.qL) + (1 - group.phiU) * group.qL * (1 - group.pkP))

            player.leads_cp = prob_cp >= prob_player
            if player.leads and not player.leads_cp:
                player.group.leader = 1
            elif not p1.leads and p2.leads:
                player.group.leader = 0
            else:
                player.group.leader = random.randint(0,1)
            if player.group.leader == 1:
                leadership_correct = player.leadership_correct
            else:
                leadership_correct = player.leadership_correct_cp
            if player.group.payment_choices and leadership_correct:
                for p in players:
                    p.payoff += player.group.decision_payoff


class Survey(Page):
    form_model = "player"
    form_fields = ['gender', 'age', 'language', 'residence', 'nationality', 'student', 'employment', 'zip', 'comments']


class Completion(Page):
    # send players back to prolific
    form_model = "player"

    @staticmethod
    def vars_for_template(player: Player):
        if not player.no_partner and player.group.made_leadership_choice:
            leadership_correct = player.group.get_player_by_id(player.group.leader).leadership_correct
        elif player.no_partner and player.group.made_leadership_choice and player.group.leader == 1:
            leadership_correct = player.leadership_correct
        elif player.no_partner and player.group.made_leadership_choice and player.group.leader == 0:
            leadership_correct = player.leadership_correct_cp
        else:
            leadership_correct = 'NA'
        if not player.no_partner:
            prob_bj = round(probability_prize_bsr(player.get_others_in_group()[0].high, player.bj)* 100, 2) 
            partner_high = player.get_others_in_group()[0].high
        else:
            prob_bj = round(probability_prize_bsr(player.high_cp, player.bj)* 100, 2) 
            partner_high = player.high_cp
        return dict(
            leadership_correct = leadership_correct,
            bi = int(round(player.bi * 100,0)),
            bj = int(round(player.bj * 100,0)),
            partner_high = partner_high,
            prob_bi = round(probability_prize_bsr(player.high, player.bi) * 100, 2),
            prob_bj = prob_bj
        )

    @staticmethod              
    def js_vars(player):
        return dict(
            completion_link=player.subsession.session.config['completion_link'],
        )


page_sequence = [Matching, Decision, Beliefs, Leadership, Survey, Completion]
