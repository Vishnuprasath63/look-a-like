from django.contrib import admin
from .models import Celebrity, MatchResult


@admin.register(Celebrity)
class CelebrityAdmin(admin.ModelAdmin):
    list_display = ('name', 'category')
    list_filter = ('category',)
    search_fields = ('name',)


@admin.register(MatchResult)
class MatchResultAdmin(admin.ModelAdmin):
    list_display = ('user', 'top_match_name', 'top_match_score', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('user__username', 'top_match_name')
