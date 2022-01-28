from django.contrib import admin

from .models import Metric


@admin.register(Metric)
class MetricAdmin(admin.ModelAdmin):
    model = Metric
    list_display = ("type", "category", "name", "count", "period", "period_start")
    list_filter = ("type", "period", "category")
    search_fields = ("name",)
    ordering = ("-period_start",)
