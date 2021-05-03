from otree.api import *

c = Currency

doc = """
Your app description
"""


class Constants(BaseConstants):
    name_in_url = 'survey'
    players_per_group = None
    num_rounds = 1
    survey_payoff = c(5)


class Subsession(BaseSubsession):
    pass


class Group(BaseGroup):
    pass


class Player(BasePlayer):
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


# PAGES
class Survey(Page):
    form_model = "player"
    form_fields = ['gender', 'age', 'field', 'semesters', 'strategy', 'comments']

    @staticmethod
    def before_next_page(player: Player, timeout_happened):
        player.payoff = Constants.survey_payoff


page_sequence = [Survey]
