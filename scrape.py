import requests
from typing import List
from bs4 import BeautifulSoup
from dataclasses import dataclass
from enum import Enum

class Outcome(Enum):
    DEFEAT = 0
    VICTORY = 1

class Character(Enum):
    IRONCLAD = 0
    SILENT = 1
    DEFECT = 2


# Datastructures, to be pulled into separate file
@dataclass
class CardLog:
    name: str
    upgraded: bool
    source: str
    floor: int


@dataclass
class RelicLog:
    name: str
    source: str
    floor: int


@dataclass
class Log:
    floors: List[str]
    deck: List[CardLog]
    relics: List[RelicLog]
    outcome: Outcome
    player: str
    score: int
    character: Character
    ascension: int
    upload_date: str
    version: str
    playtime: str
    source: str


def retrieve_entry_from_table(table, name):
    cols = table.find("td", string=name).parent.children
    return [c.text for c in cols][1:]

def card_row_extractor(row):
    return CardLog(
        name=row[0].text,
        upgraded="+" in row[1].text,
        source=row[2].text,
        floor=int(row[3].text) if row[3].text else -1
    )

def relic_row_extractor(row):
    if len(row) != 3:
        return RelicLog(
            name=row[0].text,
            source="unk",
            floor=float('nan')
        )
    return RelicLog(
        name=row[0].text,
        source=row[1].text,
        floor=int(row[2].text)
    )

def parse_table(table, extractor):
    rows = table.find_all("tr")
    items = []
    for row in rows[1:]:
        items.append(extractor(list(row.children)))
    return items

def parse_page(html):
    soup = BeautifulSoup(html, 'html.parser')
    ascension_span = soup.find("span", {"class": "ascension"})
    ascension = 0 if ascension_span is None else int(ascension_span.text.split(" ")[1])
    player, _, character = soup.find("span", {"class": "character"}).text.rsplit(" ", 2)
    outcome = "Victory" in soup.find("span", {"class": "result"}).text
    floors = [str(block) for block in soup.findAll("div", {"class": "floor-block"})]
    summary_tables = soup.find("div", {"class": "summary"}).find_all("table")
    uploaded = retrieve_entry_from_table(summary_tables[0], "Uploaded On")[0]
    playtime = retrieve_entry_from_table(summary_tables[0], "Playtime")[0]
    version = retrieve_entry_from_table(summary_tables[0], "Game Version")[0]
    score = retrieve_entry_from_table(summary_tables[0], "Score")[0]

    deck_list = parse_table(summary_tables[1], card_row_extractor)
    relic_list = parse_table(summary_tables[2], relic_row_extractor)

    return Log(
        floors=floors,
        deck=deck_list,
        relics=relic_list,
        outcome=outcome,
        player=player,
        score=score,
        character=character,
        ascension=ascension,
        upload_date=uploaded,
        version=version,
        playtime=playtime,
        source=html
    )

if __name__ == "__main__":
    with open("example.html", "r") as f:
        html = f.read()

    result = parse_page(html)
