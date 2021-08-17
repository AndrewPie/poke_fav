import json

import requests
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import Http404, HttpResponse, HttpResponseRedirect
from django.urls import reverse, reverse_lazy
from django.shortcuts import get_object_or_404, redirect, render
from django.views.generic import ListView, CreateView, DeleteView
from django.views import View

from pokemon.models import Pokemon, User


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


def pokemon_detail(self, data):
    pokemon_detail = data
    
    self.request.session['pok_name'] = data['name']
    
    pokemon_detail['image'] = data['sprites']['front_default']
    
    pokemon_detail['type_list'] = []
    for el in range(0, len(data['types'])):
        pokemon_detail['type_list'].append(data['types'][el]['type']['name'])
        
    pokemon_detail['ability_list'] = []
    for el in range(0, len(data['abilities'])):
        pokemon_detail['ability_list'].append(data['abilities'][el]['ability']['name'])

    pokemon_detail['pok_stats'] = {}
    for i, k in enumerate(data['stats']):
        name = data['stats'][i]['stat']['name']
        stat = data['stats'][i]['base_stat']
        pokemon_detail['pok_stats'][name] = stat
        
    return pokemon_detail


def evolution_chain(p_id):
    evolutions = {}
    
    response = requests.get(f'https://pokeapi.co/api/v2/pokemon-species/{p_id}')
    
    if response.ok:
        pok_species = response.json()
        evo_chain = requests.get(pok_species['evolution_chain']['url']).json()
        
        if evo_chain['chain']['evolves_to']:
            evolutions['base'] = {
                'p_id': evo_chain['chain']['species']['url'].split('/')[-2],
                'name': evo_chain['chain']['species']['name']
            }
            evolutions['first'] = []
            for el in evo_chain['chain']['evolves_to']:
                evolutions['first'].append({
                'p_id': el['species']['url'].split('/')[-2],
                'name': el['species']['name']
                })
                if el['evolves_to']:
                    evolutions['second'] = []
                    for el2 in el['evolves_to']:
                        evolutions['second'].append({
                            'p_id': el2['species']['url'].split('/')[-2],
                            'name': el2['species']['name'],
                            'first_id': el['species']['url'].split('/')[-2]
                        })
            return evolutions


def check_if_fav(self, p_id):
    current_user = self.request.user
    fav = None
    try:
        pokemon = Pokemon.objects.get(p_id=p_id)
    except Pokemon.DoesNotExist:
        pokemon = None
    
    if pokemon:
        pok_db_id = getattr(pokemon, 'id')
        try:
            fav =  User.objects.get(id = current_user.id, favourites__id=pok_db_id)
        except User.DoesNotExist:
            pass
    return fav


class PokemonList(LoginRequiredMixin, ListView):
    model = Pokemon
    template_name = 'pokemon/list.html'
    
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
        return context
    
    
class PokemonDetail(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        p_id = self.kwargs['pk']
        data = call_poke_api(self, request, p_id)
        
        context = {}
        context['pokemon'] = pokemon_detail(self, data)
        context['evolutions'] = evolution_chain(p_id)
        context['is_fav'] = check_if_fav(self, p_id)
        return render(request, 'pokemon/detail.html', context)
    

class Favourite(LoginRequiredMixin, View):
    def post(self, request, pk):
        if Pokemon.objects.filter(p_id = pk).exists():
            pokemon = get_object_or_404(Pokemon, p_id = pk)
            pokemon.favourite.add(self.request.user)
        else:
            name = self.request.session['pok_name']
            p_id = pk
            pokemon = Pokemon.objects.create(name=name, p_id=p_id)
            pokemon.favourite.add(self.request.user)
        return redirect('pokemon:detail', pk = pk)


class Unfavourite(LoginRequiredMixin, View):
    def post(self, request, pk):
        if Pokemon.objects.filter(p_id = pk).exists():
            pokemon = get_object_or_404(Pokemon, p_id = pk)
            current_user = self.request.user
            user = get_object_or_404(User, id = current_user.id)
            pokemon.favourite.remove(user)
        return redirect('pokemon:detail', pk = pk)


class FavouritesList(LoginRequiredMixin, ListView):
    model = Pokemon
    template_name = 'pokemon/fav_list.html'
    ordering = ['name']
    context_object_name = 'fav_list'
    
    def get_queryset(self):
        queryset = super().get_queryset()
        current_user = self.request.user
        return queryset.filter(favourite = current_user)