from pathlib import Path
import pickle
from bs4 import BeautifulSoup
from dataclasses import dataclass
from typing import List
import re


@dataclass
class Pack:
    pick: str
    available: List[str]


@dataclass
class Health:
    total: int
    current: int
    delta: int


class Floor:

    def __init__(self, floor_html, deck):
        self.source = floor_html
        soup = BeautifulSoup(floor_html, 'html.parser')
        current = soup.find("span")
        self.packs = []
        self.added = []
        self.removed = []
        self.health = None
        self.delta_money = 0
        while current is not None:
            self.update_with_line(current.text, current)
            current = current.find_next_sibling()

    def update_with_line(self, text, span):
        print(text)
        if not text:
            return

        # This can only be detected by span class
        if span.has_attr("class") and span["class"][0] == "cards":
            options = [s.text for s in span.children]
            self.update_pick(*options)
            return

        patterns_with_updates = [
            (re.compile("^Floor (\d)*: (.*$)"), self.update_floor),
            #obtain_pattern = "^Obtained (.*$)"
            #upgrade_pattern = "^Upgraded (.*$)"
            (re.compile("^Purchased (.*$)"), self.update_purchase),
            (re.compile("^Skipped Cards: (.*), (.*), (.*)$"), self.update_skip),
            (re.compile("^Gained (\d*) gold$"), self.update_gold),
            (re.compile("^Spent (\d*) gold$"), self.update_gold),
            (re.compile("^Lost (\d*) gold$"), self.update_gold),
            (re.compile("^(\d*)/(\d*) HP$"), self.update_health),
            (re.compile("^([+\-]\d*)$"), self.update_health_delta)
            #defeat_pattern = "^Defeated (.*) in (\d)* turns \((\d)* damage\)$"
            #rekt_pattern = "^Rekt by (.*) in (\d)* turns \((\d)* damage\)$"
            #choice_pattern = "^Choice: (.*)$"
        ]
        for pattern, update_func in patterns_with_updates:
            m = pattern.match(text)
            if m is not None:
                update_func(*m.groups())

    def update_floor(self, number, name):
        self.number = number
        self.type = name

    def update_pick(self, choice, second, third):
        self.packs.append(Pack(
            pick=choice,
            available=[choice, second, third]
        ))
        self.added.append(choice)

    def update_gold(self, amount):
        self.delta_money = int(amount)

    def update_skip(self, first, second, third):
        self.packs.append(Pack(
            pick=None,
            available=[first, second, third]
        ))
        #TODO: singing bowl??

    def update_purchase(self, card):
        # TODO: i'll have to have a list of what is or is not a card
        self.added.append(card)

    def update_health(self, current, total):
        self.health = Health(total=int(total), current=int(current), delta=None)

    def update_health_delta(self, delta):
        self.health.delta = int(delta)

    def __str__(self):
        return f"Floor: {self.number}({self.type}). {self.packs}. Gold change: {self.delta_money}. HP: {self.health}"


runs_path = Path("data") / Path(user)
target_run = next(runs_path.iterdir())
with target_run.open("rb") as f:
    run_log = pickle.load(f)

soup = BeautifulSoup(run_log.floors[1], 'html.parser')
floor = Floor(run_log.floors[1], None)
