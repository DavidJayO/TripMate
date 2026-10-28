from django.contrib import admin
from .models import Expense, ItineraryItem, PackingItem, Trip, TripMembership
@admin.register(Trip)
class TripAdmin(admin.ModelAdmin):
    list_display = ("destination", "owner", "start_date", "end_date", "budget", "currency")
    list_filter = ("start_date", "currency")
    search_fields = ("destination", "owner__username")

@admin.register(ItineraryItem)
class ItineraryItemAdmin(admin.ModelAdmin):
    list_display = ("title", "trip", "date", "time")
    list_filter = ("date",)
    search_fields = ("title", "location", "trip__destination")

@admin.register(PackingItem)
class PackingItemAdmin(admin.ModelAdmin):
    list_display = ("name", "trip", "packed")
    list_filter = ("packed",)
    search_fields = ("name", "trip__destination")

@admin.register(Expense)
class ExpenseAdmin(admin.ModelAdmin):
    list_display = ("title", "trip", "category", "amount", "date")
    list_filter = ("category", "date")
    search_fields = ("title", "trip__destination")

@admin.register(TripMembership)
class TripMembershipAdmin(admin.ModelAdmin):
    list_display = ("trip", "user", "role", "added_at")
    list_filter = ("role",)
    search_fields = ("trip__destination", "user__username")
