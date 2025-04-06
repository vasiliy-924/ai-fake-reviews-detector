from django.contrib import admin

from .models import AnalysisResult, DebugLog, ParserConfig, Review

admin.site.register(Review)
admin.site.register(AnalysisResult)


@admin.register(ParserConfig)
class ParserConfigAdmin(admin.ModelAdmin):
    list_display = ("url", "is_active", "schedule")


@admin.register(DebugLog)
class DebugLogAdmin(admin.ModelAdmin):
    list_display = ("created_at", "success")
    readonly_fields = ("html_content", "error_message")
