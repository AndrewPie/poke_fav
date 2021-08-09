import requests
from django.shortcuts import redirect, render
from django.views.generic import ListView
from django.contrib.auth.mixins import LoginRequiredMixin
from pokemon.models import Pokemon

# from django.http import HttpResponse, HttpResponseRedirect
# from django.urls import reverse

class PokemonList(LoginRequiredMixin, ListView):
    model = Pokemon
    template_name = "pokemon/list.html"
    
    def post(self,request):
        if 'first' in request.POST:
            self.request.session['offset'] = 0
        elif 'next' in request.POST:
            self.request.session['offset'] += 10
        elif 'previous' in request.POST:
            self.request.session['offset'] -= 10
        elif 'last' in request.POST:
            self.request.session['offset'] = 1110
# TODO: "last" must be dynamically changed depending on api "count" value
        # return HttpResponseRedirect(reverse('pokemon:list'))
        # return HttpResponseRedirect('')
        return redirect('pokemon:list')


    def call_pokemon_api(self):
        payload = {
            'offset': self.request.session['offset'], 'limit': 10
            }
        response = requests.get('https://pokeapi.co/api/v2/pokemon/', params = payload)
        data = response.json()
        return data


    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if not 'offset' in self.request.session or not self.request.session['offset']:
            self.request.session['offset'] = 0
        context['pokemon'] = self.call_pokemon_api
        context['offset'] = self.request.session['offset']
        return context