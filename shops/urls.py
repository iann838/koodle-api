from django.urls import path

from shops import views


urlpatterns = [
    path('currencies', views.CurrenciesView.as_view()),
    path('search/<str:category>/<str:name>', views.SearchView.as_view()),
    path('click/<str:category>/<str:name>', views.ClickMetricView.as_view()),
]
