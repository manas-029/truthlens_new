from django.contrib import admin
from .models import Scan, Feedback


@admin.register(Scan)
class ScanAdmin(admin.ModelAdmin):
    list_display = ('id', 'media_type', 'source_type', 'verdict', 'confidence', 'status', 'created_at')
    list_filter = ('media_type', 'verdict', 'status')
    readonly_fields = ('id', 'created_at', 'completed_at')


@admin.register(Feedback)
class FeedbackAdmin(admin.ModelAdmin):
    list_display = ('scan', 'user', 'reviewed', 'created_at')
    list_filter = ('reviewed',)
