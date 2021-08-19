from django import template
import requests
from django.http import Http404

register = template.Library()

@register.filter
def index(sequence, position):
    return sequence[position]


@register.filter
def pokemon_id(api_url):
    poke_id = api_url.split('/')[-2]
    return poke_id


@register.filter
def types(api_url):
    poke_id = pokemon_id(api_url)
    try:
        response = requests.get(f'https://pokeapi.co/api/v2/pokemon/{poke_id}')
    except requests.exceptions.RequestException as e:
        raise Http404(e)
    
    data = response.json()
    
    type_list = []
    for el in range(0, len(data['types'])):
        type_list.append(data['types'][el]['type']['name'])
    return type_list