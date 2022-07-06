"""
Functions that performs part of the computation of another function, usually from interactions.py
because the functionality is needed in multiple places.
"""

from datetime import datetime
from requests import get
from decouple import config
from api.models import Summoner, Match

API_KEY = config("API")


def create_user_db(summoner_name):
    """Create user in database"""
    Summoner.objects.create(
        summoner=summoner_name,
        stats={
            "kills": {"total": 0, "per_min": 0, "per_match": 0},
            "deaths": {"total": 0, "per_min": 0, "per_match": 0},
            "assists": {"total": 0, "per_min": 0, "per_match": 0},
            "minions": {"total": 0, "per_min": 0, "per_match": 0},
            "vision": {"total": 0, "per_min": 0, "per_match": 0},
        },
        roles={
            "TOP": {"NUM": 0, "WIN_RATE": 0, "WINS": 0, "LOSSES": 0},
            "JUNGLE": {"NUM": 0, "WIN_RATE": 0, "WINS": 0, "LOSSES": 0},
            "MIDDLE": {"NUM": 0, "WIN_RATE": 0, "WINS": 0, "LOSSES": 0},
            "BOTTOM": {"NUM": 0, "WIN_RATE": 0, "WINS": 0, "LOSSES": 0},
            "UTILITY": {"NUM": 0, "WIN_RATE": 0, "WINS": 0, "LOSSES": 0},
        },
    )


def add_matches_to_db(matchlist, summoner_name):
    """Add matches to database"""
    add_match_bulk_list = []
    for match in matchlist:
        # if match id with summoner name not found, create object in database
        if Match.objects.filter(match_id=match, summoner=summoner_name).exists():
            break
        add_match_bulk_list.append(Match(match_id=match, summoner=summoner_name))
    Match.objects.bulk_create(add_match_bulk_list)


def find_summaries_not_in_db(matchlist, summoner_name):
    """List of match ids which summaries are not in database"""
    summary_not_in_database = []
    for match in matchlist:
        # If match summary not in database, create object in database
        if Match.objects.filter(
            match_id=match, summoner=summoner_name, summary_json__exact={}
        ).exists():
            summary_not_in_database.append(match)
            # Limit to 7 for lazy load pagination
            if len(summary_not_in_database) == 7:
                break
    return summary_not_in_database


def save_summaries_to_db(match_summary_list, summoner_name):
    """Save match summaries to database"""
    bulk_save_summary_list = []
    for match in match_summary_list:
        match_object = Match.objects.get(
            match_id=match["metadata"]["matchId"], summoner=summoner_name
        )
        match_object.summary_json = match
        bulk_save_summary_list.append(match_object)
    Match.objects.bulk_update(bulk_save_summary_list, ["summary_json"])


def get_date_by_timestamp(match_timestamp):
    """match date from unix timestamp

    Args:
        match_timestamp (int): Unix timestamp for when the match is created on the match server

    Returns:
        str: date when match was created, e.g 2021-11-24
    """

    return str((datetime.fromtimestamp(match_timestamp / 1000.0)).date())


def get_region_by_platform(platform):
    """
    The AMERICAS routing value serves NA, BR, LAN, LAS, and OCE.
    The ASIA routing value serves KR and JP.
    The EUROPE routing value serves EUNE, EUW, TR, and RU.
    """
    if platform in ("NA1", "BR1", "LA1", "LA2", "OC1"):
        region = "AMERICAS"

    elif platform in ("EUN1", "EUW1", "TR1", "RU"):
        region = "EUROPE"

    elif platform in ("KR", "JP1"):
        region = "ASIA"

    return region


def get_match_mode(queue_id):
    """Get match mode by the queue_id"""
    match queue_id:
        case 400:
            return "Normal Draft"
        case 420:
            return "Ranked Solo"
        case 430:
            return "Normal Blind"
        case _:
            return "Special"


def get_summoner_spell(summoner_key):
    """Get summoner spell by the summoner_key"""
    match summoner_key:
        case 1:
            return "summoner_boost"
        case 3:
            return "summoner_exhaust"
        case 4:
            return "summoner_flash"
        case 6:
            return "summoner_haste"
        case 7:
            return "summoner_heal"
        case 11:
            return "summoner_smite"
        case 12:
            return "summoner_teleport"
        case 13:
            return "summonermana"
        case 14:
            return "summonerignite"
        case 21:
            return "summonerbarrier"
        case 32:
            return "summoner_mark"
        case _:
            return "summoner_empty"


def get_rune_primary(rune_id):
    url = "https://raw.communitydragon.org/latest/plugins/rcp-be-lol-game-data/global/default/v1/perks.json"
    data_json = get(url).json()
    rune_dict = next((item for item in data_json if item["id"] == rune_id), None)
    return rune_dict["iconPath"].split("Styles/", 1)[1]


def get_rune_secondary(rune_id):
    """Get rune by the rune_id"""
    match rune_id:
        case 8000:
            return "7201_precision"
        case 8100:
            return "7200_domination"
        case 8200:
            return "7202_sorcery"
        case 8300:
            return "7203_whimsy"
        case _:
            return "7204_resolve"
