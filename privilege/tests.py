from otree.api import Currency as c, currency_range, expect, Bot
from . import *
import random


class PlayerBot(Bot):
    def play_round(self):
        yield Decision
        
        if self.player.kudos and self.player.privilege:
            prob_player = self.group.phiP * self.group.qH / (self.group.phiP * self.group.qH + (1 - self.group.phiP) * self.group.qL)
        elif self.player.kudos and not self.player.privilege:
            prob_player = self.group.phiU * self.group.qH / (self.group.phiU * self.group.qH + (1 - self.group.phiU) * self.group.qL)
        elif not self.player.kudos and self.player.privilege:
            prob_player = (self.group.phiP * (1 - self.group.qH) + self.group.phiP * self.group.qH * (1 - self.group.pkP)) / (self.group.phiP * (1 - self.group.qH) + self.group.phiP * self.group.qH * (1 - self.group.pkP) + (1 - self.group.phiP) * (1 - self.group.qL) + (1 - self.group.phiP) * self.group.qL * (1 - self.group.pkP))
        elif not self.player.kudos and not self.player.privilege:
            prob_player = (self.group.phiU * (1 - self.group.qH) + self.group.phiU * self.group.qH * (1 - self.group.pkP)) / (self.group.phiU * (1 - self.group.qH) + self.group.phiU * self.group.qH * (1 - self.group.pkP) + (1 - self.group.phiU) * (1 - self.group.qL) + (1 - self.group.phiU) * self.group.qL * (1 - self.group.pkP))

        if self.player.get_others_in_group()[0].kudos and player.privilege:
            prob_partner = self.group.phiP * self.group.qH / (self.group.phiP * self.group.qH + (1 - self.group.phiP) * self.group.qL)
        elif player.kudos_cp and not player.privilege_cp:
            prob_partner = self.group.phiU * self.group.qH / (self.group.phiU * self.group.qH + (1 - self.group.phiU) * self.group.qL)
        elif not player.kudos_cp and player.privilege_cp:
            prob_partner = (self.group.phiP * (1 - self.group.qH) + self.group.phiP * self.group.qH * (1 - self.group.pkP)) / (self.group.phiP * (1 - self.group.qH) + self.group.phiP * self.group.qH * (1 - self.group.pkP) + (1 - self.group.phiP) * (1 - self.group.qL) + (1 - self.group.phiP) * self.group.qL * (1 - self.group.pkP))
        elif not player.kudos_cp and not player.privilege_cp:
            prob_partner = (self.group.phiU * (1 - self.group.qH) + self.group.phiU * self.group.qH * (1 - self.group.pkP)) / (self.group.phiU * (1 - self.group.qH) + self.group.phiU * self.group.qH * (1 - self.group.pkP) + (1 - self.group.phiU) * (1 - self.group.qL) + (1 - self.group.phiU) * self.group.qL * (1 - self.group.pkP))

        player.leads_cp = prob_cp >= prob_player

        yield Submission(Beliefs, dict(bi=random.random(), bj=random.random()), check_html=False)
        yield Leadership, dict(leads=random.choice([True, False]))
        yield Survey, dict(
            gender=random.choice(['m', 'f', 'o', 'ns']),
            age=random.randint(0,99),
            language=random.choice(['English', 'Other']),
            residence=random.choice(['UK', 'Other']),
            nationality=random.choice(['UK', 'Other']),
            student=random.choice([True, False]),
            employment=random.choice([True, False]),
            zip=random.choice(['idk', 'uk', 'zip', 'codes', 'by', 'heart']),
            comments='I am a bot'
            )
        yield Submission(Completion, check_html=False)
