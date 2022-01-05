from django.urls import path

from shops import views


urlpatterns = [
    path('search/<str:category>/<str:name>', views.SearchView.as_view()),
    path('currencies', views.CurrenciesView.as_view()),
]
