from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect, HttpResponseNotFound
from django.http.response import JsonResponse
from django.shortcuts import render
from django.urls import reverse
from django import forms
from django.conf import settings
from django.core import serializers
from django.core.paginator import Paginator
from django.views.decorators.csrf import csrf_exempt

from .models import *
import requests, json, copy, datetime, urllib, random
from igdb.wrapper import IGDBWrapper
from .igdb_utils import igdb, wrapper, save_game


def index(request):
    """Shows 10 random games on the homepage."""
    num = random.randint(0, 1000)
    print(num)
    results = igdb(
        wrapper,
        "games",
        f"fields id, name, cover, first_release_date; offset { num }; where aggregated_rating > 85;",
    )

    for result in results:
        if "cover" in result:
            cover_json = igdb(
                wrapper, "covers", f"fields url; where id = { result['cover'] };"
            )[0]
            result["cover_url"] = f"https:{ cover_json['url'] }".replace(
                "t_thumb", "t_cover_big", 1
            )
        else:
            result["cover_url"] = None

        if "first_release_date" in result:
            release_date_dt = datetime.date.fromtimestamp(result["first_release_date"])
            result["reldate"] = release_date_dt.strftime("%m-%d-%Y")

    return render(request, "gamerater/index.html", {"results": results})


def logout_view(request):
    """Logs user out."""
    logout(request)
    return HttpResponseRedirect(reverse("gamerater:index"))


def login_view(request):
    """Logs user in."""
    if request.method == "POST":

        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("gamerater:index"))
        else:
            return render(
                request,
                "gamerater/login.html",
                {"message": "Invalid username and/or password."},
            )
    else:
        return render(request, "gamerater/login.html")


def register(request):
    """Registers new user."""
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]

        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(
                request, "gamerater/register.html", {"message": "Passwords must match."}
            )

        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(
                request,
                "gamerater/register.html",
                {"message": "Username already taken."},
            )
        login(request, user)
        return HttpResponseRedirect(reverse("gamerater:index"))
    else:
        return render(request, "gamerater/register.html")


def search(request):
    """Returns results of games from user's query."""
    if request.method == "GET":
        query = request.GET["query"]

        if "page" in request.GET:
            page = int(request.GET["page"])
        else:
            page = 0

        results = igdb(
            wrapper,
            "games",
            f'search "{ query }"; fields id, name, cover, first_release_date; offset { page * 10 };',
        )

        for result in results:
            if "cover" in result:
                cover_json = igdb(
                    wrapper, "covers", f"fields url; where id = { result['cover'] };"
                )[0]
                result["cover_url"] = f"https:{ cover_json['url'] }".replace(
                    "t_thumb", "t_cover_big", 1
                )
            else:
                result["cover_url"] = None

            if "first_release_date" in result:
                release_date_dt = datetime.date.fromtimestamp(
                    result["first_release_date"]
                )
                result["reldate"] = release_date_dt.strftime("%m-%d-%Y")

        return render(
            request,
            "gamerater/results.html",
            {
                "results": results,
                "query": urllib.parse.quote(query),
                "prev": page - 1,
                "next": page + 1,
            },
        )


def game_list(request, username, list_name):
    """Shows a specific user's list of games."""
    user = User.objects.get(username=username)
    # query = Game.objects.filter(gamerelationship__user=user)
    query = GameRelationship.objects.filter(user=user)

    if list_name == "backlog":
        list = query.filter(is_backlog=True)
        print(list)
        list_elab_name = "Backlog"
    elif list_name == "completed":
        list = query.filter(is_completed=True)
        list_elab_name = "Completed"
    elif list_name == "playing":
        list = query.filter(is_playing=True)
        list_elab_name = "Currently Playing"
    else:
        return HttpResponseNotFound("<h1>Page not found.</h1>")

    paginator = Paginator(list, 10)
    page_num = request.GET.get("page")
    rels = paginator.get_page(page_num)

    return render(
        request,
        "gamerater/game_list.html",
        {
            "rels": rels,
            "viewing_user": user,
            "list_elab_name": list_elab_name,
        },
    )


def user_page(request, username):
    """Shows a specific user's profile page with the games in their lists."""
    user = User.objects.get(username=username)
    query = GameRelationship.objects.filter(user=user)

    backlog = query.filter(is_backlog=True)
    completed = query.filter(is_completed=True)
    playing = query.filter(is_playing=True)

    return render(
        request,
        "gamerater/user.html",
        {
            "viewing_user": user,
            "backlog": backlog,
            "completed": completed,
            "playing": playing,
        },
    )


def game(request, game_id):
    """Shows a specific game's page with information from API."""
    try:
        game = Game.objects.get(id=game_id)
    except Game.DoesNotExist:
        game = save_game(wrapper, game_id)

    if request.user.is_authenticated:
        user = request.user
        rel = GameRelationship.objects.get_or_create(user=user, game=game)[0]

    return render(
        request,
        "gamerater/game.html",
        {
            "instance": game,
            "rel": rel,
        },
    )


@csrf_exempt
@login_required
def game_db(request, game_id):
    """Returns JSON data to requests from frontend."""
    try:
        game = Game.objects.get(id=game_id)
    except Game.DoesNotExist:
        game = save_game(wrapper, game_id)

    rel, created = GameRelationship.objects.get_or_create(user=request.user, game=game)

    if request.method == "GET":
        if rel.is_backlog:
            in_user_list = "backlog"
        elif rel.is_playing:
            in_user_list = "playing"
        elif rel.is_completed:
            in_user_list = "completed"
        else:
            in_user_list = "none"

        return JsonResponse(
            {
                "list": in_user_list,
                "journal": rel.journal_entry,
            }
        )

    if request.method == "PUT":
        data = json.loads(request.body)
        if "list-add" in data:
            value = str(data["list-add"])

            if value == "backlog":
                rel.is_backlog = True
                rel.is_playing = False
                rel.is_completed = False
            elif value == "playing":
                rel.is_backlog = False
                rel.is_playing = True
                rel.is_completed = False
            elif value == "completed":
                rel.is_backlog = False
                rel.is_playing = False
                rel.is_completed = True
            elif value == "none":
                rel.is_backlog = False
                rel.is_playing = False
                rel.is_completed = False
        elif "journal" in data:
            entry = data["journal"]
            rel.journal_entry = entry

        rel.save()
        return HttpResponse(status=204)


def users_dir(request):
    """Shows all users registered with website."""
    users = User.objects.all()
    user_list = []
    for user in users:
        rels = GameRelationship.objects.filter(user=user)
        user_data = {
            "name": user.username,
            "backlog_count": len(rels.filter(is_backlog=True)),
            "playing_count": len(rels.filter(is_playing=True)),
            "completed_count": len(rels.filter(is_completed=True)),
        }
        user_list.append(user_data)

    return render(
        request,
        "gamerater/users_dir.html",
        {
            "users": user_list,
        },
    )
