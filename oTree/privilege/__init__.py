from otree.api import *
import random

c = Currency

doc = """

"""


class C(BaseConstants):
    # name in url governs the link that participants see. instead of using "privilege", use something innocuous
    NAME_IN_URL = 'experiment'

    # two players interact with each other
    PLAYERS_PER_GROUP = 2

    # the game is played only once, no repeats
    NUM_ROUNDS = 1

    # probability of being privileged P, else underprivileged U
    P = 0.25

    # probability of being high ability when P/U
    PHI_P = 0.2
    PHI_U = 0.8

    # probability of hitting the target when high and low ability type
    Q_H = 0.75
    Q_L = 0.25

    # probability of receiving kudos when P/U and correct
    P_KP = 0.99
    P_KU = 0.01

    # payoffs for correct choice
    CHOICE_PAYOFF = cu(5)
    BELIEFS_PAYOFF = cu(2.5)


class Subsession(BaseSubsession):
    pass


class Group(BaseGroup):
    high = models.FloatField()  # leader's probability of hitting the target
    correct = models.BooleanField()  # does the leader hit the target


class Player(BasePlayer):
    ## consent
    consent = models.BooleanField(choices=[[True, 'Yes']])
    
    ## privilege game
    high = models.BooleanField()  # H type or not (L)
    privileged = models.BooleanField()  # P type or not (U)
    ability = models.FloatField()  # player's probability of hitting the target
    correct = models.BooleanField()  # was the player correct
    kudos = models.BooleanField()  # does the player receive kudos

    # beliefs about own and partner's types 
    bi = models.FloatField(min=0, max=1)
    bj = models.FloatField(min=0, max=1)

    obi = models.BooleanField()  # does the player receive prize for beliefs about self
    obj = models.BooleanField()  # does the player receive prize for beliefs about partner

    # save whether the subject wants to lead/follow
    wants_leader = models.BooleanField()  # used to record actual outcome

    # track whether the subject makes the choice in the leadership part of the game
    is_leader = models.BooleanField()

    # variable if player is paid for beliefs (to eliminate hedging)
    payment_choices = models.BooleanField()

    ## survey
    gender = models.StringField(
        choices=[
            ['m', 'male'],
            ['f', 'female'],
            ['o', 'other'],
        ],
        label="Gender"
    )
    age = models.IntegerField(min=0, max=100, label="How old are you?")
    field = models.LongStringField(label="Which field of study?")
    semesters = models.IntegerField(min=0, max=100, label="How many semesters have you been studying?")
    strategy = models.LongStringField(blank=True,
                                      label="Please describe your thought process or your strategy in this experiment.")
    comments = models.LongStringField(blank=True,
                                      label="Do you have any other comments or questions about this experiment?")


# when creating the session, set some variables
def creating_session(subsession):
    # loop through all players in the session
    for player in subsession.get_players():
        # assign privilege
        if random.random() < C.P:
            player.privileged = True
        else:
            player.privileged = False

        # assign ability type
        if player.privileged and random.random() < C.PHI_P:
            player.high = True
        elif not player.privileged and random.random() < C.PHI_U:
            player.high = True
        else:
            player.high = False

        # assign correctness
        if player.high and random.random() < C.Q_H:
            player.correct = True
        elif not player.high and random.random() < C.Q_L:
            player.correct = True
        else:
            player.correct = True

        # assign kudos
        if player.privileged and player.correct and random.random() < C.P_KP:
            player.kudos = True
        elif not player.privileged and player.correct and random.random() < C.P_KU:
            player.kudos = True
        else:
            player.kudos = False

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
class Consent(Page):
    form_model = "player"
    form_fields = ["consent"]


class Instructions(Page):
    # on the instruction page, push some variables to the page: How many winning balls are in each urn, etc.
    @staticmethod
    def vars_for_template(player: Player):
        return dict()


class Decision(Page):
    pass


class Matching(WaitPage):
    group_by_arrival_time = True


class Beliefs(Page):
    # on this page the player reports their beliefs
    form_model = "player"
    form_fields = ["bi", "bj"]


class Leadership(Page):
    # players say whether they want to lead
    form_model = "player"
    form_fields = ["wants_leader"]


class Survey(Page):
    form_model = "player"
    form_fields = ['gender', 'age', 'field', 'semesters', 'strategy', 'comments']

    def is_displayed(player):
        return player.consent


class Completion(Page):
    # send players back to prolific
    form_model = "player"

    def is_displayed(player):
        return player.consent

    @staticmethod              
    def js_vars(player):
        return dict(
            completion_link=player.subsession.session.config['completion_link']
        )

page_sequence = [Consent, Instructions, Decision, Matching, Beliefs, Leadership, Survey, Completion]
