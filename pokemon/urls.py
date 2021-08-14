from django.urls import path

from pokemon.views import PokemonList, PokemonDetail

app_name = 'pokemon'
urlpatterns = [
    path('list/', PokemonList.as_view(), name = 'list'),
    path('<int:pk>/', PokemonDetail.as_view(), name = 'detail'),
]