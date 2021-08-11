from otree.api import *
import random

c = Currency

doc = """

"""


class Constants(BaseConstants):
    # name in url governs the link that participants see. instead of using "privilege", use something innocuous
    name_in_url = 'experiment'

    # two players interact with each other
    players_per_group = 2

    # the game is played only once, no repeats
    num_rounds = 1

    # probability of being privileged P, else underprivileged U
    p = 0.25

    # probability of being high ability when P/U
    phi_P = 0.2
    phi_U = 0.8

    # probability of hitting the target when high and low ability type
    q_H = 0.75
    q_L = 0.25

    # payoffs for [correct choice, incorrect choice]
    choice_payoff = cu(5)
    beliefs_payoff = cu(2.5)


class Subsession(BaseSubsession):
    pass


class Group(BaseGroup):
    correct = models.BooleanField()  # does the leader hit the target


class Player(BasePlayer):
    high = models.BooleanField()  # H type or not (L)
    privileged = models.BooleanField()  # P type or not (U)
    ability = models.FloatField()  # player's probability of hitting the target
    correct = models.BooleanField()  # was the player correct
    kudos = models.BooleanField()  # does the player receive kudos

    # beliefs about own and partner's types conditional on receiving signal kudos or not
    bi_k = models.FloatField(min=0, max=1)
    bi_n = models.FloatField(min=0, max=1)
    bj_k = models.FloatField(min=0, max=1)
    bj_n = models.FloatField(min=0, max=1)

    obi = models.BooleanField()  # does the player receive prize for beliefs about self
    obj = models.BooleanField()  # does the player receive prize for beliefs about partner

    # save whether the subject wants to lead/follow when signals are xy (x for own y for other)
    wants_leader = models.BooleanField()  # used to record actual outcome
    wants_leader_kk = models.BooleanField(
        choices=[
            [True, "Yes"],
            [False, "No"],
        ],
        label="Do you want to lead?",
    )
    wants_leader_kn = models.BooleanField(
        choices=[
            [True, "Yes"],
            [False, "No"],
        ],
        label="Do you want to lead?",
    )
    wants_leader_nk = models.BooleanField(
        choices=[
            [True, "Yes"],
            [False, "No"],
        ],
        label="Do you want to lead?",
    )
    wants_leader_nn = models.BooleanField(
        choices=[
            [True, "Yes"],
            [False, "No"],
        ],
        label="Do you want to lead?",
    )

    # track whether the subject makes the choice in the leadership part of the game
    is_leader = models.BooleanField()

    # variable if player is paid for beliefs (to eliminate hedging)
    payment_choices = models.BooleanField()


# when creating the session, set some variables
def creating_session(subsession):
    # loop through all players in the session
    for player in subsession.get_players():
        # draw from U~[0,1] and assign privilege
        if player.draw_privilege < Constants.p:
            player.privileged = True
        else:
            player.privileged = False

        # draw from U~[0,1] and assign ability type
        if player.privileged and random.random() < Constants.phi_P:
            player.high = True
        elif not player.privileged and random.random() < Constants.phi_U:
            player.high = True
        else:
            player.high = False

        if player.high:
            player.ability = Constants.q_H
        else:
            player.ability = Constants.q_L

        # assign payment for beliefs (50/50 chance)
        player.payment_choices = random.random() < 0.5


# FUNCTIONS
# function to calculate whether a prize is awarded by the binarized scoring rule
def probability_prize_bsr(statement, belief):
    if statement:
        return 1 - (1 - belief) ** 2
    else:
        return 1 - belief ** 2


def draw_prize_bsr(statement, belief, draw):
    if draw < probability_prize_bsr(statement, belief):
        return True
    else:
        return False


# PAGES
class Instructions(Page):
    # on the instruction page, push some variables to the page: How many winning balls are in each urn, etc.
    @staticmethod
    def vars_for_template(player: Player):
        return dict()


class Decision1(Page):
    # after the player clicks next, run the following code
    @staticmethod
    def before_next_page(player: Player, timeout_happened):
        # determine whether the player hit the target
        if random.random() < player.ability:
            player.correct = True
        else:
            player.correct = False

        # give player kudos if they are privileged and their choice was correct
        if player.privileged and player.correct:
            player.kudos = True
        else:
            player.kudos = False


class Beliefs(Page):
    # on this page the player reports their beliefs
    form_model = "player"
    form_fields = ["bi_k", "bi_n", "bj_k", "bj_n"]


class Leadership(Page):
    # players say whether they want to lead
    form_model = "player"
    form_fields = ["wants_leader_kk", "wants_leader_kn", "wants_leader_nk", "wants_leader_nn"]


# wait for all players to make a choice whether to lead
class LeadershipWaitPage(WaitPage):
    @staticmethod
    def after_all_players_arrive(group: Group):
        players = group.get_players()
        for p in players:
            partner = p.get_others_in_group()[0]
            if p.kudos and partner.kudos:
                p.wants_leader = p.wants_leader_kk
            elif p.kudos and not partner.kudos:
                p.wants_leader = p.wants_leader_kn
            elif not p.kudos and partner.kudos:
                p.wants_leader = p.wants_leader_nk
            else:
                p.wants_leader = p.wants_leader_nn

        # get both players' decisions. if they are not the same there is only one volunteer. else throw a coin.
        choices = [p.wants_leader for p in players]
        if choices[0] != choices[1]:
            for p in players:
                p.is_leader = p.leads
        else:
            if random.random() < 0.5:
                players[0].is_leader = True
                players[1].is_leader = False
            else:
                players[0].is_leader = False
                players[1].is_leader = True


class Decision2(Page):
    # only displayed to players that lead
    @staticmethod
    def is_displayed(player: Player):
        return player.is_leader

    @staticmethod
    def before_next_page(player: Player, timeout_happened):
        # determine whether the leader hit the target
        if random.random() < player.ability:
            player.group.correct = True
        else:
            player.group.correct = False


# wait for other player to make choice
class FeedbackWaitPage(WaitPage):
    @staticmethod
    def after_all_players_arrive(group: Group):
        players = group.get_players()
        for p in players:
            # after all players in the group arrive on this page, copy values from leader for followers
            if not p.makes_leadership_choice:
                p.leadership_correct = p.get_others_in_group()[0].leadership_correct
                p.leadership_draw_correct = p.get_others_in_group()[0].leadership_draw_correct
                p.leadership_choice = p.get_others_in_group()[0].leadership_choice

            # draw random numbers from U[0,1] for binarized scoring rule
            p.draw_beliefs_partner_ability = random.random()
            p.draw_beliefs_ability = random.random()
            p.draw_beliefs_partner_privilege = random.random()
            p.draw_beliefs_privilege = random.random()

            # afterwards, sum up payoffs for choices and beliefs
            p.payoff = 0

            # if the subject is paid for their choices, it's easy. simply add the payoff if they chose a winning door
            if p.payment_choices:
                if p.correct:
                    p.payoff += Constants.choice_payoff
                if p.leadership_correct:
                    p.payoff += Constants.choice_payoff
            # if the subject is paid for beliefs, use the binarized scoring rule.
            # push statement, beliefs and random draw to function
            # if the subject wins, add payoff
            else:
                if draw_prize_bsr(p.high_ability, p.beliefs_high_ability, p.draw_beliefs_ability):
                    p.payoff += Constants.beliefs_payoff
                    p.outcome_beliefs_high_ability = True
                else:
                    p.outcome_beliefs_high_ability = False

                if draw_prize_bsr(p.privileged, p.beliefs_privileged, p.draw_beliefs_privilege):
                    p.payoff += Constants.beliefs_payoff
                    p.outcome_beliefs_privileged = True
                else:
                    p.outcome_beliefs_privileged = False

                if draw_prize_bsr(p.get_others_in_group()[0].high_ability, p.draw_beliefs_partner_ability, p.draw_beliefs_partner_ability):
                    p.payoff += Constants.beliefs_payoff
                    p.outcome_beliefs_partner_high_ability = True
                else:
                    p.outcome_beliefs_partner_high_ability = False

                if draw_prize_bsr(p.get_others_in_group()[0].privileged, p.draw_beliefs_partner_privilege, p.beliefs_partner_privileged):
                    p.payoff += Constants.beliefs_payoff
                    p.outcome_beliefs_partner_privileged = True
                else:
                    p.outcome_beliefs_partner_privileged = False


class Feedback(Page):
    @staticmethod
    def vars_for_template(player: Player):
        # push probabilities for each prize to page
        chance_high_ability = probability_prize_bsr(player.high_ability, player.beliefs_high_ability)
        chance_privileged = probability_prize_bsr(player.privileged, player.beliefs_privileged)
        chance_partner_high_ability = probability_prize_bsr(player.get_others_in_group()[0].high_ability,
                                                            player.beliefs_partner_high_ability)
        chance_partner_privileged = probability_prize_bsr(player.get_others_in_group()[0].privileged,
                                                          player.beliefs_partner_privileged)

        partner_kudos = []
        partner_kudos = player.get_others_in_group()[0].kudos

        return dict(
            # other player's type
            partner_high_ability=player.get_others_in_group()[0].high_ability,
            partner_privileged=player.get_others_in_group()[0].privileged,

            # stated beliefs
            beliefs_high_ability=str(round(player.beliefs_high_ability*100)) + "%",
            beliefs_privileged=str(round(player.beliefs_privileged * 100)) + "%",
            beliefs_partner_high_ability=str(round(player.beliefs_partner_high_ability * 100)) + "%",
            beliefs_partner_privileged=str(round(player.beliefs_partner_privileged * 100)) + "%",

            # chance for belief payoffs
            chance_high_ability=str(round(chance_high_ability*100)) + "%",
            chance_privileged=str(round(chance_privileged*100)) + "%",
            chance_partner_high_ability=str(round(chance_partner_high_ability*100)) + "%",
            chance_partner_privileged=str(round(chance_partner_privileged*100)) + "%",
            outcome_high_ability=draw_prize_bsr(player.high_ability, player.beliefs_high_ability, player.draw_beliefs_ability),
            outcome_privileged=draw_prize_bsr(player.privileged, player.beliefs_privileged, player.draw_beliefs_privilege),
            outcome_partner_high_ability=draw_prize_bsr(player.privileged, player.beliefs_privileged, player.draw_beliefs_privilege),
            outcome_partner_privileged=player.draw_beliefs_partner_privilege > (1 - player.beliefs_partner_privileged) ** 2,
            partner_kudos=partner_kudos,
            public=player.session.config["public"],
        )


page_sequence = [Instructions, Decision1, Beliefs, Leadership, LeadershipWaitPage,
                 Decision2, FeedbackWaitPage, Feedback]
