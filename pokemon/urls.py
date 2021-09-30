from django.urls import path

from pokemon.views import (
    PokemonList,
    PokemonSort,
    PokemonDetail,
    Favourite,
    Unfavourite,
    FavouritesList,
)

app_name = "pokemon"
urlpatterns = [
    path("list/", PokemonList.as_view(), name="list"),
    path("list/<str:key>/<str:order>", PokemonSort.as_view(), name="sort"),
    path("detail/<slug:p_info>/", PokemonDetail.as_view(), name="detail"),
    path("<int:pk>/favourite", Favourite.as_view(), name="favourite"),
    path("<int:pk>/unfavourite", Unfavourite.as_view(), name="unfavourite"),
    path("favourites/", FavouritesList.as_view(), name="fav"),
]
