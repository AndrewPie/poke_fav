from django.urls import path

from pokemon.views import PokemonList

app_name = 'pokemon'
urlpatterns = [
    path('list/',PokemonList.as_view(), name = 'list'),
]