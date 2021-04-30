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

    # the number of choices that the subject may choose from
    number_of_choices = 3

    # how many are correct when they are type H and L
    number_of_correct_choices_high = 2
    number_of_correct_choices_low = 1

    # probability of being type H.
    # please only use X/10 because probabilities are explained to subjects by draws from an urn with 10 balls
    prob_high_ability = 0.7

    # probability of being privileged P
    # please only use X/10 because probabilities are explained to subjects by draws from an urn with 10 balls
    prob_privileged = 0.7

    # probability of receiving a correct signal
    # please only use X/10 because probabilities are explained to subjects by draws from an pile with 10 cards
    prob_correct_signal = 0.7

    # payoffs for [correct choice, incorrect choice]
    choice_payoff = cu(5)
    beliefs_payoff = cu(2.5)


class Subsession(BaseSubsession):
    pass


class Group(BaseGroup):
    pass


class Player(BasePlayer):
    # variable recording subject's choice
    choice = models.IntegerField(
        choices=[
            [0, "Door 1"],
            [1, "Door 2"],
            [2, "Door 3"],
        ],
        label="Which door do you pick?",
        widget=widgets.RadioSelect
    )

    # was the player correct
    correct = models.BooleanField()

    # is the player type H
    high_ability = models.BooleanField()

    # is the player privileged P
    privileged = models.BooleanField()

    # does the player receive signal h
    high_signal = models.BooleanField()

    # does the player receive kudos k
    kudos = models.BooleanField()

    # does the player's partner receive kudos
    partner_kudos = models.BooleanField()

    # save beliefs about own and partner's types
    beliefs_high_ability = models.FloatField(min=0, max=1)
    beliefs_privileged = models.FloatField(min=0, max=1)
    beliefs_partner_high_ability = models.FloatField(min=0, max=1)
    beliefs_partner_privileged = models.FloatField(min=0, max=1)

    # save random draws for debug purposes
    draw_ability = models.FloatField()
    draw_privilege = models.FloatField()
    draw_signal = models.FloatField()
    draw_correct = models.StringField()

    draw_beliefs_ability = models.FloatField()
    draw_beliefs_privilege = models.FloatField()
    draw_beliefs_partner_ability = models.FloatField()
    draw_beliefs_partner_privilege = models.FloatField()

    # save whether the subject wants to lead/follow
    leads = models.BooleanField(
        choices=[
            [True, "Yes"],
            [False, "No"],
        ],
        label="Do you want to choose from your own doors?",
    )
    follows = models.BooleanField(
        choices=[
            [True, "Yes"],
            [False, "No"],
        ],
        label="Do you want to choose the same door as your partner?",
    )

    # track whether the subject may make a choice in the leadership part of the game
    makes_leadership_choice = models.BooleanField()

    # save what choice is made in the leadership part of the game and whether the choice is correct
    leadership_choice = models.BooleanField(choices=[
        [0, "Door 1"],
        [1, "Door 2"],
        [2, "Door 3"],
    ], label="Which door do you pick?")
    leadership_draw_correct = models.StringField()
    leadership_correct = models.BooleanField()

    # save whether player receives prize for beliefs from binarized scoring rule
    outcome_beliefs_high_ability = models.BooleanField()
    outcome_beliefs_privileged = models.BooleanField()
    outcome_beliefs_partner_high_ability = models.BooleanField()
    outcome_beliefs_partner_privileged = models.BooleanField()

    # variable if player is paid for choices or beliefs (to eliminate hedging)
    payment_choices = models.BooleanField()


# when creating the session, set some variables
def creating_session(subsession):
    # loop through all players in the session
    for player in subsession.get_players():
        # draw from U~[0,1] and assign ability
        player.draw_ability = random.random()
        player.high_ability = False
        if player.draw_ability < Constants.prob_high_ability:
            player.high_ability = True

        # same for privilege
        player.draw_privilege = random.random()
        player.privileged = False
        if player.draw_privilege < Constants.prob_privileged:
            player.privileged = True

        # return a high signal to players if they are of high ability and pass their signal check
        player.high_signal = False
        player.draw_signal = random.random()
        if player.high_ability and player.draw_signal < Constants.prob_correct_signal:
            player.high_signal = True

        # or if they are low ability and do not pass their signal check
        if not player.high_signal and player.draw_signal > Constants.prob_correct_signal:
            player.high_signal = True

        # assign payment for choices or beliefs (50/50 chance)
        player.payment_choices = random.random() > 0.5


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
        return dict(
            high_ability_prob=round(Constants.prob_high_ability * 100),
            high_ability_balls=round(Constants.prob_high_ability * 10),
            low_ability_balls=10-round(Constants.prob_high_ability * 10),

            privileged_prob=round(Constants.prob_privileged * 100),
            privileged_balls=round(Constants.prob_privileged * 10),
            nonprivileged_balls=10-round(Constants.prob_privileged * 10),

            pile_correct_prob=round(Constants.prob_correct_signal * 100),
            pile_correct_cards=round(Constants.prob_correct_signal * 10),
            pile_incorrect_cards=10-round(Constants.prob_correct_signal * 10),

            follower_choice=player.session.config["follower_choice"],
            public=player.session.config["public"],
        )


class Decision1(Page):
    # the player can make a choice for their variable choice here
    form_model = "player"
    form_fields = ["choice"]

    # after the player clicks next, run the following code
    @staticmethod
    def before_next_page(player: Player, timeout_happened):
        # determine the number of correct choices
        number_of_correct_choices = Constants.number_of_correct_choices_low
        if player.high_ability:
            number_of_correct_choices = Constants.number_of_correct_choices_high

        # initialize variable if player is correct as False
        player.correct = False

        # randomly draw some choices that are correct and save it in the participant variables for later use
        draw_correct = random.sample(range(Constants.number_of_choices), number_of_correct_choices)
        player.participant.draw_correct = draw_correct

        # join them into a single string and save the correct choices (for debug purposes)
        draw_correct_string = [str(element) for element in draw_correct]
        draw_correct_single_string = ",".join(draw_correct_string)
        player.draw_correct = draw_correct_single_string

        # check if player's choice is in correct draw
        if player.choice in draw_correct:
            player.correct = True

        # give player kudos if they are privileged and their choice was correct
        player.kudos = False
        if player.privileged and player.choice:
            player.kudos = True


# wait for other player in group to make a choice too
class InfoWaitPage(WaitPage):
    pass


class Info(Page):
    # on this page the player reports their beliefs
    form_model = "player"
    form_fields = ["beliefs_high_ability", "beliefs_privileged", "beliefs_partner_high_ability",
                   "beliefs_partner_privileged"]

    # push some variables to the html page
    @staticmethod
    def vars_for_template(player: Player):
        # initialize partner's kudos as an empty value: if we are not in public treatment, we do not want to push any
        # information to the page
        partner_kudos = []
        if player.session.config["public"]:
            partner_kudos = player.get_others_in_group()[0].kudos
        return dict(
            public=player.session.config["public"],
            partner_kudos=partner_kudos,
            prob_correct_signal=round(Constants.prob_correct_signal*100)
            )


class FirstMover(Page):
    form_model = "player"
    form_fields = ["leads"]

    # only player with ID = 1 in group gets to make a choice
    @staticmethod
    def is_displayed(player: Player):
        return player.id_in_group == 1

    @staticmethod
    def before_next_page(player: Player, timeout_happened):
        # if player 1 leads, also set their makes_choice to True
        # set player 2's makes_choice to False (if we are in the follower treatment, player 2 may revise later)
        if player.leads:
            player.makes_leadership_choice = True
            player.get_others_in_group()[0].makes_leadership_choice = False
        # if player 2 does not lead, other way round
        else:
            player.makes_leadership_choice = False
            player.get_others_in_group()[0].makes_leadership_choice = True

    # push some variables to the html page
    @staticmethod
    def vars_for_template(player: Player):
        # initialize partner's kudos as an empty value: if we are not in public treatment, we do not want to push any
        # information to the page
        partner_kudos = []
        if player.session.config["public"]:
            partner_kudos = player.get_others_in_group()[0].kudos
        return dict(
            public=player.session.config["public"],
            partner_kudos=partner_kudos,
            follower_choice=player.session.config["follower_choice"],
            )


# wait for player 1 to make a choice whether to lead
class FirstMoverWaitPage(WaitPage):
    pass


class SecondMover(Page):
    form_model = "player"
    form_fields = ["follows"]

    # only player 2 in group gets to see this page
    # only if we are in the follower_choice treatment and player 1 chose to lead though
    @staticmethod
    def is_displayed(player: Player):
        return player.id_in_group == 2 and player.session.config["follower_choice"] and \
               player.get_others_in_group()[0].leads

    @staticmethod
    def before_next_page(player: Player, timeout_happened):
        if player.follows:
            player.makes_leadership_choice = False
        else:
            player.makes_leadership_choice = True

    @staticmethod
    def vars_for_template(player: Player):
        partner_kudos = []
        if player.session.config["public"]:
            partner_kudos = player.get_others_in_group()[0].kudos
        return dict(
            public=player.session.config["public"],
            partner_kudos=partner_kudos,
            )


# wait for player 2 to make a choice
class SecondMoverWaitPage(WaitPage):
    pass


class Decision2(Page):
    form_model = "player"
    form_fields = ["leadership_choice"]

    # only displayed to players that lead
    # player 2 only makes a choice if player 1 does not lead or 2 does not follow (may only be true in follower_choice)
    @staticmethod
    def is_displayed(player: Player):
        return player.makes_leadership_choice

    @staticmethod
    def before_next_page(player: Player, timeout_happened):
        # determine the number of correct choices
        number_of_correct_choices = Constants.number_of_correct_choices_low
        if player.high_ability:
            number_of_correct_choices = Constants.number_of_correct_choices_high

        # initialize variable if player is correct as False
        player.leadership_correct = False

        # randomly draw some choices that are correct and store it for later
        draw_correct = random.sample(range(Constants.number_of_choices), number_of_correct_choices)
        player.participant.draw_leadership_correct = draw_correct

        # join them into a single string and save the correct choices (for debug purposes)
        draw_correct_string = [str(element) for element in draw_correct]
        draw_correct_single_string = ",".join(draw_correct_string)
        player.leadership_draw_correct = draw_correct_single_string

        # check if player's choice is in correct draw
        if player.leadership_choice in draw_correct:
            player.leadership_correct = True

    @staticmethod
    def vars_for_template(player: Player):
        partner_kudos = []
        if player.session.config["public"]:
            partner_kudos = player.get_others_in_group()[0].kudos
        return dict(
            public=player.session.config["public"],
            partner_kudos=partner_kudos,
            partner_makes_choice=player.get_others_in_group()[0].makes_leadership_choice
            )


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


page_sequence = [Instructions, Decision1, InfoWaitPage, Info, FirstMover, FirstMoverWaitPage, SecondMover,
                 SecondMoverWaitPage, Decision2, FeedbackWaitPage, Feedback]
