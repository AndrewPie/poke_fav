import json

import requests
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import Http404, HttpResponse, HttpResponseRedirect
from django.urls import reverse, reverse_lazy
from django.shortcuts import get_object_or_404, redirect, render
from django.views.generic import ListView, CreateView, DeleteView
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.views import View

from pokemon.models import Pokemon, User


def call_poke_api(self, request, p_info=None):
    try:
        if p_info is None:
            response_limit = requests.get("https://pokeapi.co/api/v2/pokemon/").json()
            limit = response_limit["count"]

            payload = {"offset": 0, "limit": limit}

            response = requests.get(
                "https://pokeapi.co/api/v2/pokemon/", params=payload
            )
        else:
            if isinstance(p_info, str):
                p_info = p_info.lower()
            response = requests.get(f"https://pokeapi.co/api/v2/pokemon/{p_info}")
    except requests.exceptions.RequestException as e:
        raise Http404(e)

    data = response.json()
    return data


def pokemon_detail(self, data):
    pokemon_detail = data
    self.request.session["pok_name"] = data["name"]

    pokemon_detail["image"] = data["sprites"]["front_default"]

    pokemon_detail["type_list"] = []
    for el in range(0, len(data["types"])):
        pokemon_detail["type_list"].append(data["types"][el]["type"]["name"])

    pokemon_detail["ability_list"] = []
    for el in range(0, len(data["abilities"])):
        pokemon_detail["ability_list"].append(data["abilities"][el]["ability"]["name"])

    pokemon_detail["pok_stats"] = {}
    for i, k in enumerate(data["stats"]):
        name = data["stats"][i]["stat"]["name"]
        stat = data["stats"][i]["base_stat"]
        pokemon_detail["pok_stats"][name] = stat

    return pokemon_detail


def evolution_chain(p_info):
    evolutions = {}

    response = requests.get(f"https://pokeapi.co/api/v2/pokemon-species/{p_info}")

    if response.ok:
        pok_species = response.json()
        evo_chain = requests.get(pok_species["evolution_chain"]["url"]).json()

        if evo_chain["chain"]["evolves_to"]:
            evolutions["base"] = {
                "p_id": evo_chain["chain"]["species"]["url"].split("/")[-2],
                "name": evo_chain["chain"]["species"]["name"],
            }
            evolutions["first"] = []
            for el in evo_chain["chain"]["evolves_to"]:
                evolutions["first"].append(
                    {
                        "p_id": el["species"]["url"].split("/")[-2],
                        "name": el["species"]["name"],
                    }
                )
                if el["evolves_to"]:
                    evolutions["second"] = []
                    for el2 in el["evolves_to"]:
                        evolutions["second"].append(
                            {
                                "p_id": el2["species"]["url"].split("/")[-2],
                                "name": el2["species"]["name"],
                                "first_id": el["species"]["url"].split("/")[-2],
                            }
                        )
            return evolutions


def check_if_fav(self, p_info):
    current_user = self.request.user
    fav = None
    try:
        if isinstance(p_info, int):
            pokemon = Pokemon.objects.get(p_id=p_info)
        elif isinstance(p_info, str):
            pokemon = Pokemon.objects.get(name=p_info)
    except Pokemon.DoesNotExist:
        pokemon = None

    if pokemon:
        pok_db_id = getattr(pokemon, "id")
        try:
            fav = User.objects.get(id=current_user.id, favourites__id=pok_db_id)
        except User.DoesNotExist:
            pass
    return fav


def sort_list(self):
    if (
        not "sorting_key" in self.request.session
        or not self.request.session["sorting_key"]
    ):
        self.request.session["sorting_key"] = "id"
    s_key = self.request.session["sorting_key"]
    if (
        not "sorting_order" in self.request.session
        or not self.request.session["sorting_order"]
    ):
        self.request.session["sorting_order"] = "ascending"
    s_order = self.request.session["sorting_order"]

    self.request.session["sorting_slug"] = f"{s_key}_{s_order}"

    if s_key == "id":
        sorting_key = lambda k: int(k["url"].split("/")[-2])
    else:
        sorting_key = lambda k: k["name"]

    sorting_order = False if s_order == "ascending" else True

    return {"sorting_key": sorting_key, "sorting_order": sorting_order}


class PokemonList(LoginRequiredMixin, ListView):
    template_name = "pokemon/list.html"
    paginate_by = 10
    context_object_name = "pokemons"

    def setup(self, request, *args, **kwargs):
        if hasattr(self, "get") and not hasattr(self, "head"):
            self.head = self.get
        self.request = request
        self.args = args
        self.kwargs = kwargs

        self.data = call_poke_api(self, request)
        self.queryset = self.data["results"]
        super().setup

    def get_queryset(self):
        queryset = self.queryset
        sorting = sort_list(self)
        sorted_queryset = sorted(
            queryset, key=sorting["sorting_key"], reverse=sorting["sorting_order"]
        )
        return sorted_queryset

    def get(self, request, *args, **kwargs):
        page_number = self.request.GET.get("page", 1)
        self.request.session["page_number"] = page_number
        return super().get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        paginator = Paginator(self.queryset, 10)
        page_range = paginator.get_elided_page_range(
            number=self.request.session["page_number"], on_each_side=2
        )
        context["page_range"] = page_range
        context["sort_method"] = self.request.session["sorting_slug"]
        return context


class PokemonSort(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        self.request.session["sorting_key"] = self.kwargs["key"]
        self.request.session["sorting_order"] = self.kwargs["order"]
        return redirect("pokemon:list")


class PokemonDetail(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        p_info = self.kwargs["p_info"]
        # p_info = self.request.GET.get("p_info", None)
        data = call_poke_api(self, request, p_info)

        context = {}
        context["pokemon"] = pokemon_detail(self, data)
        context["evolutions"] = evolution_chain(p_info)
        context["is_fav"] = check_if_fav(self, p_info)
        return render(request, "pokemon/detail.html", context)


class Favourite(LoginRequiredMixin, View):
    def post(self, request, pk):
        if Pokemon.objects.filter(p_id=pk).exists():
            pokemon = get_object_or_404(Pokemon, p_id=pk)
            pokemon.favourite.add(self.request.user)
        else:
            name = self.request.session["pok_name"]
            p_id = pk
            pokemon = Pokemon.objects.create(name=name, p_id=p_id)
            pokemon.favourite.add(self.request.user)
        return redirect("pokemon:detail", p_info=pk)


class Unfavourite(LoginRequiredMixin, View):
    def post(self, request, pk):
        if Pokemon.objects.filter(p_id=pk).exists():
            pokemon = get_object_or_404(Pokemon, p_id=pk)
            current_user = self.request.user
            user = get_object_or_404(User, id=current_user.id)
            pokemon.favourite.remove(user)
            # if not pokemon.favourite.all():
            #     pokemon.delete()
        return redirect("pokemon:detail", p_info=pk)


class FavouritesList(LoginRequiredMixin, ListView):
    model = Pokemon
    template_name = "pokemon/fav_list.html"
    ordering = ["name"]
    context_object_name = "fav_list"
    paginate_by = 10

    def get_queryset(self):
        queryset = super().get_queryset()
        current_user = self.request.user
        return queryset.filter(favourite=current_user)
