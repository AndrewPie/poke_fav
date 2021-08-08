import requests
from django.shortcuts import redirect, render
from django.views.generic import ListView
from pokemon.models import Pokemon

from django.http import HttpResponse

class PokemonList(ListView):
    model = Pokemon
    template_name = "pokemon/list.html"

    def call_pokemon_api(self):
        payload = {'offset': 0, 'limit': 10}
        response = requests.get('https://pokeapi.co/api/v2/pokemon/', params = payload)
        data = response.json()
        return data


    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if not 'offset' in self.request.session or not self.request.session['offset']:
            self.request.session['offset'] = 10
        context['pokemon'] = self.call_pokemon_api
        context['offset'] = self.request.session['offset']
        return context