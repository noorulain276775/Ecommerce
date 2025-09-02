from django.urls import path
from .views import AdvancedSearchView, SearchSuggestionsView, FilterOptionsView

urlpatterns = [
    path('', AdvancedSearchView.as_view(), name='advanced-search'),
    path('suggestions/', SearchSuggestionsView.as_view(), name='search-suggestions'),
    path('filters/', FilterOptionsView.as_view(), name='filter-options'),
]
