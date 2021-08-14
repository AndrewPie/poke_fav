import json

import requests
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import Http404, HttpResponse, HttpResponseRedirect
from django.shortcuts import redirect, render
from django.views.generic import ListView
from django.views import View

from pokemon.models import Pokemon


def call_poke_api(self, request, p_id: int = None):
    if not 'offset' in self.request.session or not self.request.session['offset']:
            self.request.session['offset'] = 0

    payload = {
            'offset': self.request.session['offset'], 
            'limit': 10
            }
    
    try:
        if p_id is None:
            response = requests.get('https://pokeapi.co/api/v2/pokemon/', params = payload)
        else:
            response = requests.get(f'https://pokeapi.co/api/v2/pokemon/{p_id}')
    except requests.exceptions.RequestException as e:
        raise Http404(e)

    data = response.json()
    return data

def detail_list(data):
    urls = [el['url'] for el in data['results']]
    poke_id = [url.split('/')[-2] for url in urls]
    types = []
    
    for url in urls:
        response = requests.get(url).json()
        types.append([])
        if len(response['types']) == 1:
            types[urls.index(url)].append(response['types'][0]['type']['name'])
        elif len(response['types']) > 1:
            for el in range(0, len(response['types'])):
                types[urls.index(url)].append(response['types'][el]['type']['name'])
                
    detail = {}
    detail['id'] = poke_id
    detail['types'] = types
    return detail


def pokemon_detail(data):
    pokemon_detail = {}
    pokemon_detail['image'] = data['sprites']['front_default']
    pokemon_detail['name'] = data['name']
    pokemon_detail['id'] = data['id']
    pokemon_detail['weight'] = data['weight']
    return pokemon_detail


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
        self.detail = detail_list(self.data)
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
        context['detail'] = self.detail
        # print(self.request.session['offset'])
        return context


class PokemonDetail(LoginRequiredMixin, View):
    def setup(self, request, *args, **kwargs):
        if hasattr(self, 'get') and not hasattr(self, 'head'):
            self.head = self.get
        self.request = request
        self.args = args
        self.kwargs = kwargs

        self.p_id = self.kwargs['pk']
        print (self.p_id)
        self.data = call_poke_api(self, request, self.p_id)
        self.pokemon_detail = pokemon_detail(self.data)
        super().setup
        
    def get(self, request, *args, **kwargs):
        context = {}
        context['pokemon'] = self.pokemon_detail
        return render(request, 'pokemon/detail.html', context)