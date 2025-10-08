#!/usr/bin/env python3
import requests, json, os
from igdb.wrapper import IGDBWrapper
from gamerater.models import Game
import datetime


client_id = os.environ.get("IGDB_CLIENT_ID")
client_secret = os.environ.get("IGDB_CLIENT_SECRET")

def get_wrapper():
    """Return wrapper to retrieve data from IGDB."""
    headers = {
        "client_id": client_id,
        "client_secret": client_secret,
        "grant_type": "client_credentials",
    }
    r = requests.post("https://id.twitch.tv/oauth2/token", params=headers)
    r.raise_for_status()
    r_json = r.json()
    token = r_json["access_token"]
    return IGDBWrapper(client_id, token)


def igdb(wrapper, endpoint, field):
    """Return json data from a request to IGDB."""
    data = wrapper.api_request(endpoint, field)
    return json.loads(data)


def save_game(wrapper, game_id):
    """Create new model instance of game."""
    game_info = igdb(
        wrapper,
        "games",
        f"fields id, name, cover, first_release_date, genres, updated_at, aggregated_rating, involved_companies, platforms; where id = { game_id };",
    )[0]

    game_name = game_info["name"]
    cover_json = igdb(
        wrapper, "covers", f"fields url; where id = { game_info['cover'] };"
    )
    cover_url = f"https:{cover_json[0]['url']}"
    cover_url = cover_url.replace("t_thumb", "t_cover_big", 1)

    if "first_release_date" in game_info:
        first_release_date = datetime.date.fromtimestamp(
            game_info["first_release_date"]
        )
    else:
        first_release_date = None

    if "genres" in game_info:
        genres = []
        for genre_id in game_info["genres"]:
            genre_json = igdb(
                wrapper, "genres", f"fields name; where id = { genre_id };"
            )[0]
            name = genre_json["name"]
            genres.append(name)
        genre_list = ", ".join(genres)
    else:
        genre_list = None

    updated_at = datetime.datetime.fromtimestamp(game_info["updated_at"])
    updated_at = updated_at.replace(tzinfo=datetime.timezone.utc)

    if "aggregated_rating" in game_info:
        aggregated_rating = game_info["aggregated_rating"]
    else:
        aggregated_rating = None

    if "involved_companies" in game_info:
        developer = ""
        for involved_company in game_info["involved_companies"]:
            inv_comp_json = igdb(
                wrapper,
                "involved_companies",
                f"fields company, developer; where id = { involved_company };",
            )[0]
            is_developer = inv_comp_json["developer"]
            company_id = inv_comp_json["company"]

            if is_developer:
                company_json = igdb(
                    wrapper,
                    "companies",
                    f"fields name; where id = { company_id };",
                )
                developer = company_json[0]["name"]
                break
    else:
        developer = None

    new_game = Game(
        id=game_id,
        name=game_name,
        cover=cover_url,
        first_release_date=first_release_date,
        genres=genre_list,
        updated_at=updated_at,
        aggregated_rating=aggregated_rating,
        developer=developer,
    )
    new_game.save()
    return new_game


wrapper = get_wrapper()
