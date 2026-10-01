from django.contrib import admin

from collector.models import Request, RequestBody


class RequestBodyInline(admin.StackedInline):
    model = RequestBody
    can_delete = False


@admin.register(Request)
class RequestAdmin(admin.ModelAdmin):
    list_display = ("id", "env", "request_id", "user_id", "created_at")
    list_filter = ("env",)
    search_fields = ("request_id", "user_id")
    date_hierarchy = "created_at"
    inlines = [RequestBodyInline]
