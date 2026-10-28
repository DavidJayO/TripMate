from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.core.exceptions import PermissionDenied
from django.db.models import Count, Q, Sum
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST
from .forms import ExpenseForm, ItineraryItemForm, PackingItemForm, ShareTripForm, SignUpForm, TripForm
from .models import Expense, ItineraryItem, PackingItem, Trip, TripMembership
from . import services
from decimal import Decimal

def home(request):
    return render(request, "trips/home.html")

def signup(request):
    if request.user.is_authenticated:
        return redirect("trip_list")
    form = SignUpForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        user = form.save()
        login(request, user)
        messages.success(request, "Your account is ready. Start planning your first trip.")
        return redirect("trip_list")
    return render(request, "registration/signup.html", {"form": form})

@login_required
def trip_list(request):
    trips = Trip.objects.all() if request.user.is_staff else Trip.objects.filter(Q(owner=request.user) | Q(memberships__user=request.user)).distinct()
    return render(request, "trips/trip_list.html", {"trips": trips})

@login_required
def trip_create(request):
    form = TripForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        trip = form.save(commit=False)
        trip.owner = request.user
        trip.save()
        messages.success(request, "Trip created.")
        return redirect("trip_detail", pk=trip.pk)
    return render(request, "trips/trip_form.html", {"form": form, "title": "Plan a trip"})

def _owned_trip(request, pk):
    trip = get_object_or_404(Trip, pk=pk)
    if trip.owner_id != request.user.id and not request.user.is_staff:
        raise PermissionDenied
    return trip

def _accessible_trip(request, pk):
    trip = get_object_or_404(Trip, pk=pk)
    if request.user.is_staff or trip.owner_id == request.user.id:
        return trip
    if not TripMembership.objects.filter(trip=trip, user=request.user).exists():
        raise PermissionDenied
    return trip

def _can_edit_itinerary(request, trip):
    return request.user.is_staff or trip.owner_id == request.user.id or TripMembership.objects.filter(trip=trip, user=request.user, role=TripMembership.Role.EDITOR).exists()

def _require_itinerary_editor(request, trip):
    if not _can_edit_itinerary(request, trip):
        raise PermissionDenied

@login_required
def trip_detail(request, pk):
    trip = _accessible_trip(request, pk)
    items = trip.packing_items.all()
    expenses = trip.expenses.all()
    spent = expenses.aggregate(total=Sum("amount"))["total"] or Decimal("0.00")
    budget_remaining = trip.budget - spent
    budget_percent = min(round(spent / trip.budget * 100), 100) if trip.budget else (100 if spent else 0)
    category_totals = expenses.values("category").annotate(total=Sum("amount")).order_by("category")
    category_labels = dict(Expense.Category.choices)
    categories = [{"label": category_labels[row["category"]], "total": row["total"], "percent": min(round(row["total"] / trip.budget * 100), 100) if trip.budget else (100 if row["total"] else 0)} for row in category_totals]
    context = {"trip": trip, "weather": services.weather(trip.destination), "route": services.route(trip.origin, trip.destination), "converted": services.exchange(trip.budget, trip.currency, trip.target_currency), "holidays": services.holidays(trip.country_code, trip.start_date, trip.end_date), "itinerary": trip.itinerary_items.all(), "packing_items": items, "packing_form": PackingItemForm(), "packed_count": items.filter(packed=True).count(), "packing_count": items.count(), "expenses": expenses, "expense_total": spent, "budget_remaining": budget_remaining, "budget_percent": budget_percent, "expense_categories": categories, "is_trip_owner": request.user.is_staff or trip.owner_id == request.user.id, "can_edit_itinerary": _can_edit_itinerary(request, trip), "members": trip.memberships.select_related("user") if request.user.is_staff or trip.owner_id == request.user.id else []}
    return render(request, "trips/trip_detail.html", context)

@login_required
def expense_create(request, pk):
    trip = _owned_trip(request, pk)
    form = ExpenseForm(request.POST or None, trip=trip)
    if request.method == "POST" and form.is_valid():
        expense = form.save(commit=False)
        expense.trip = trip
        expense.save()
        messages.success(request, "Expense added to your budget breakdown.")
        return redirect("trip_detail", pk=trip.pk)
    return render(request, "trips/expense_form.html", {"trip": trip, "form": form, "title": "Add an expense"})

@login_required
def expense_edit(request, pk, expense_pk):
    trip = _owned_trip(request, pk)
    expense = get_object_or_404(Expense, pk=expense_pk, trip=trip)
    form = ExpenseForm(request.POST or None, instance=expense, trip=trip)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Expense updated.")
        return redirect("trip_detail", pk=trip.pk)
    return render(request, "trips/expense_form.html", {"trip": trip, "form": form, "title": "Edit expense"})

@login_required
@require_POST
def expense_delete(request, pk, expense_pk):
    trip = _owned_trip(request, pk)
    get_object_or_404(Expense, pk=expense_pk, trip=trip).delete()
    messages.success(request, "Expense removed.")
    return redirect("trip_detail", pk=trip.pk)

@login_required
def itinerary_item_create(request, pk):
    trip = _accessible_trip(request, pk)
    _require_itinerary_editor(request, trip)
    form = ItineraryItemForm(request.POST or None, trip=trip)
    if request.method == "POST" and form.is_valid():
        item = form.save(commit=False)
        item.trip = trip
        item.save()
        messages.success(request, "Activity added to your itinerary.")
        return redirect("trip_detail", pk=trip.pk)
    return render(request, "trips/itinerary_form.html", {"trip": trip, "form": form, "title": "Add an activity"})

@login_required
def itinerary_item_edit(request, pk, item_pk):
    trip = _accessible_trip(request, pk)
    _require_itinerary_editor(request, trip)
    item = get_object_or_404(ItineraryItem, pk=item_pk, trip=trip)
    form = ItineraryItemForm(request.POST or None, instance=item, trip=trip)
    if request.method == "POST" and form.is_valid():
        item = form.save(commit=False)
        item.save()
        messages.success(request, "Activity updated.")
        return redirect("trip_detail", pk=trip.pk)
    return render(request, "trips/itinerary_form.html", {"trip": trip, "form": form, "title": "Edit activity"})

@login_required
@require_POST
def itinerary_item_delete(request, pk, item_pk):
    trip = _accessible_trip(request, pk)
    _require_itinerary_editor(request, trip)
    get_object_or_404(ItineraryItem, pk=item_pk, trip=trip).delete()
    messages.success(request, "Activity removed from your itinerary.")
    return redirect("trip_detail", pk=trip.pk)

@login_required
@require_POST
def packing_item_create(request, pk):
    trip = _owned_trip(request, pk)
    form = PackingItemForm(request.POST)
    if form.is_valid():
        item = form.save(commit=False)
        item.trip = trip
        item.save()
        messages.success(request, "Item added to your packing list.")
    else:
        messages.error(request, "Enter an item to add to your packing list.")
    return redirect("trip_detail", pk=trip.pk)

@login_required
@require_POST
def packing_item_toggle(request, pk, item_pk):
    trip = _owned_trip(request, pk)
    item = get_object_or_404(PackingItem, pk=item_pk, trip=trip)
    item.packed = not item.packed
    item.save(update_fields=["packed"])
    return redirect("trip_detail", pk=trip.pk)

@login_required
@require_POST
def packing_item_delete(request, pk, item_pk):
    trip = _owned_trip(request, pk)
    get_object_or_404(PackingItem, pk=item_pk, trip=trip).delete()
    return redirect("trip_detail", pk=trip.pk)

@login_required
def trip_sharing(request, pk):
    trip = _owned_trip(request, pk)
    form = ShareTripForm(request.POST or None, trip=trip)
    if request.method == "POST" and form.is_valid():
        membership, created = form.save()
        messages.success(request, f"{membership.user.username} can now access this trip.")
        return redirect("trip_sharing", pk=trip.pk)
    return render(request, "trips/trip_sharing.html", {"trip": trip, "form": form, "members": trip.memberships.select_related("user")})

@login_required
@require_POST
def trip_unshare(request, pk, member_pk):
    trip = _owned_trip(request, pk)
    get_object_or_404(TripMembership, pk=member_pk, trip=trip).delete()
    messages.success(request, "Trip access removed.")
    return redirect("trip_sharing", pk=trip.pk)

@login_required
def trip_edit(request, pk):
    trip = _owned_trip(request, pk)
    form = TripForm(request.POST or None, instance=trip)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Trip updated.")
        return redirect("trip_detail", pk=trip.pk)
    return render(request, "trips/trip_form.html", {"form": form, "title": "Edit trip"})

@login_required
@require_POST
def trip_delete(request, pk):
    trip = _owned_trip(request, pk)
    trip.delete()
    messages.success(request, "Trip deleted.")
    return redirect("trip_list")

@login_required
def dashboard(request):
    if not request.user.is_staff:
        raise PermissionDenied
    context = {"user_count": User.objects.count(), "trip_count": Trip.objects.count(), "users": User.objects.annotate(trip_count=Count("trips")).order_by("-date_joined")[:10], "recent_trips": Trip.objects.select_related("owner").order_by("-created_at")[:10]}
    return render(request, "trips/dashboard.html", context)
