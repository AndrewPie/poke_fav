import requests
import json
from django.shortcuts import redirect, render
from django.views.generic import ListView
from django.contrib.auth.mixins import LoginRequiredMixin
from pokemon.models import Pokemon

# from django.http import HttpResponse, HttpResponseRedirect


def call_poke_api(self, request, *args, **kwargs):
    if not 'offset' in self.request.session or not self.request.session['offset']:
            self.request.session['offset'] = 0

    payload = {
            'offset': self.request.session['offset'], 
            'limit': 10
            }
    response = requests.get('https://pokeapi.co/api/v2/pokemon/', params = payload)
    data = response.json()
    return data


class PokemonList(LoginRequiredMixin, ListView):
    model = Pokemon
    template_name = "pokemon/list.html"
    
    def setup(self, request, *args, **kwargs):
        if hasattr(self, 'get') and not hasattr(self, 'head'):
            self.head = self.get
        self.request = request
        self.args = args
        self.kwargs = kwargs
        
        self.data = call_poke_api(self, request)
        super().setup

    def post(self, request):
        if 'first' in request.POST:
            self.request.session['offset'] = 0
        elif 'next' in request.POST:
            self.request.session['offset'] += 10
        elif 'previous' in request.POST:
            self.request.session['offset'] -= 10
        elif 'last' in request.POST:
            last_page = (self.data['count']//10)*10
            self.request.session['offset'] = last_page
        # return HttpResponseRedirect(reverse('pokemon:list'))
        # return HttpResponseRedirect('')
        return redirect('pokemon:list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['pokemon'] = self.data
        # print(self.request.session['offset'])
        return context