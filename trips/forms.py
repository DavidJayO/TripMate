from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Expense, ItineraryItem, PackingItem, Trip, TripMembership

# Popular trip-planning destinations. The place metadata drives the holiday
# lookup and destination currency without requiring a separate API lookup.
DESTINATIONS = {
    "Tokyo, Japan": ("JP", "JPY"), "Osaka, Japan": ("JP", "JPY"), "Kyoto, Japan": ("JP", "JPY"),
    "Seoul, South Korea": ("KR", "KRW"), "Busan, South Korea": ("KR", "KRW"),
    "Singapore": ("SG", "SGD"), "Bangkok, Thailand": ("TH", "THB"), "Phuket, Thailand": ("TH", "THB"),
    "Dubai, United Arab Emirates": ("AE", "AED"), "Abu Dhabi, United Arab Emirates": ("AE", "AED"),
    "Hong Kong": ("HK", "HKD"), "Taipei, Taiwan": ("TW", "TWD"), "Beijing, China": ("CN", "CNY"),
    "Shanghai, China": ("CN", "CNY"), "Kuala Lumpur, Malaysia": ("MY", "MYR"), "Bali, Indonesia": ("ID", "IDR"),
    "Hanoi, Vietnam": ("VN", "VND"), "Ho Chi Minh City, Vietnam": ("VN", "VND"), "Manila, Philippines": ("PH", "PHP"),
    "Cebu, Philippines": ("PH", "PHP"), "Sydney, Australia": ("AU", "AUD"), "Melbourne, Australia": ("AU", "AUD"),
    "Auckland, New Zealand": ("NZ", "NZD"), "London, United Kingdom": ("GB", "GBP"), "Paris, France": ("FR", "EUR"),
    "Rome, Italy": ("IT", "EUR"), "Barcelona, Spain": ("ES", "EUR"), "Amsterdam, Netherlands": ("NL", "EUR"),
    "Berlin, Germany": ("DE", "EUR"), "Athens, Greece": ("GR", "EUR"), "Zurich, Switzerland": ("CH", "CHF"),
    "Istanbul, Türkiye": ("TR", "TRY"), "New York, United States": ("US", "USD"), "Los Angeles, United States": ("US", "USD"),
    "Honolulu, United States": ("US", "USD"), "Toronto, Canada": ("CA", "CAD"), "Vancouver, Canada": ("CA", "CAD"),
    "Mexico City, Mexico": ("MX", "MXN"), "Rio de Janeiro, Brazil": ("BR", "BRL"), "Cape Town, South Africa": ("ZA", "ZAR"),
 "Cairo, Egypt": ("EG", "EGP"), "Marrakech, Morocco": ("MA", "MAD"), "Maldives": ("MV", "MVR"),
}

CURRENCIES = [
    ("PHP", "PHP — Philippine peso"), ("USD", "USD — US dollar"), ("EUR", "EUR — Euro"), ("JPY", "JPY — Japanese yen"),
    ("AED", "AED — UAE dirham"), ("GBP", "GBP — British pound"), ("SGD", "SGD — Singapore dollar"), ("AUD", "AUD — Australian dollar"),
    ("CAD", "CAD — Canadian dollar"), ("CNY", "CNY — Chinese yuan"), ("HKD", "HKD — Hong Kong dollar"), ("KRW", "KRW — South Korean won"),
    ("THB", "THB — Thai baht"), ("TWD", "TWD — Taiwan dollar"), ("MYR", "MYR — Malaysian ringgit"), ("IDR", "IDR — Indonesian rupiah"),
    ("VND", "VND — Vietnamese dong"), ("NZD", "NZD — New Zealand dollar"), ("CHF", "CHF — Swiss franc"), ("TRY", "TRY — Turkish lira"),
    ("INR", "INR — Indian rupee"), ("SAR", "SAR — Saudi riyal"), ("EGP", "EGP — Egyptian pound"), ("ZAR", "ZAR — South African rand"),
    ("MXN", "MXN — Mexican peso"), ("BRL", "BRL — Brazilian real"), ("MVR", "MVR — Maldivian rufiyaa"),
]

class DestinationSelect(forms.Select):
    def create_option(self, name, value, label, selected, index, subindex=None, attrs=None):
        option = super().create_option(name, value, label, selected, index, subindex, attrs)
        metadata = DESTINATIONS.get(str(value))
        if metadata:
            option["attrs"]["data-country"], option["attrs"]["data-currency"] = metadata
        return option
class SignUpForm(UserCreationForm):
    email = forms.EmailField(required=True)
    class Meta(UserCreationForm.Meta):
        model = User
        fields = ("username", "email")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs["class"] = "form-control"

class TripForm(forms.ModelForm):
    destination = forms.ChoiceField(
        choices=[("", "Choose a destination")]+[(place, place) for place in DESTINATIONS],
        widget=DestinationSelect(attrs={"class": "form-select", "id": "id_destination"}),
    )
    currency = forms.ChoiceField(choices=CURRENCIES, widget=forms.Select(attrs={"class": "form-select"}), label="Budget currency")
    target_currency = forms.ChoiceField(choices=CURRENCIES, widget=forms.Select(attrs={"class": "form-select", "id": "id_target_currency"}), label="Destination currency")

    class Meta:
        model = Trip
        fields = ("destination", "origin", "start_date", "end_date", "budget", "currency", "target_currency", "country_code", "notes")
        widgets = {
            "origin": forms.TextInput(attrs={"class": "form-control", "placeholder": "Manila", "list": "origin-options", "autocomplete": "off"}),
            "start_date": forms.DateInput(attrs={"type": "date", "class": "form-control"}),
            "end_date": forms.DateInput(attrs={"type": "date", "class": "form-control"}),
            "budget": forms.NumberInput(attrs={"class": "form-control", "min": "0", "step": "0.01", "placeholder": "0.00"}),
            "country_code": forms.TextInput(attrs={"class": "form-control", "readonly": True, "placeholder": "Choose destination"}),
            "notes": forms.Textarea(attrs={"class": "form-control", "rows": 4, "placeholder": "Add a few details to remember…"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        saved_destination = self.instance.destination if self.instance and self.instance.pk else ""
        if saved_destination and saved_destination not in DESTINATIONS:
            self.fields["destination"].choices.insert(1, (saved_destination, f"{saved_destination} (saved destination)"))
        if not self.is_bound and not (self.instance and self.instance.pk):
            self.initial.setdefault("currency", "PHP")
            self.initial.setdefault("target_currency", "PHP")
        self.fields["country_code"].help_text = "Filled automatically from your destination."
    def clean(self):
        cleaned = super().clean()
        start, end = cleaned.get("start_date"), cleaned.get("end_date")
        if start and end and end < start:
            self.add_error("end_date", "End date must be on or after the start date.")
        for field in ("currency", "target_currency", "country_code"):
            if cleaned.get(field):
                cleaned[field] = cleaned[field].upper()
        destination = cleaned.get("destination")
        if destination in DESTINATIONS:
            cleaned["country_code"] = DESTINATIONS[destination][0]
        return cleaned

class ItineraryItemForm(forms.ModelForm):
    class Meta:
        model = ItineraryItem
        fields = ("date", "time", "title", "location", "notes")
        widgets = {
            "date": forms.DateInput(attrs={"type": "date", "class": "form-control"}),
            "time": forms.TimeInput(attrs={"type": "time", "class": "form-control"}),
            "title": forms.TextInput(attrs={"class": "form-control", "placeholder": "Visit the museum"}),
            "location": forms.TextInput(attrs={"class": "form-control", "placeholder": "Optional place or address"}),
            "notes": forms.Textarea(attrs={"class": "form-control", "rows": 3, "placeholder": "Booking details, reminders…"}),
        }

    def __init__(self, *args, trip, **kwargs):
        self.trip = trip
        super().__init__(*args, **kwargs)
        if not self.instance.pk:
            self.fields["date"].initial = trip.start_date

    def clean_date(self):
        day = self.cleaned_data["date"]
        if not self.trip.start_date <= day <= self.trip.end_date:
            raise forms.ValidationError("Choose a date within this trip.")
        return day

class PackingItemForm(forms.ModelForm):
    class Meta:
        model = PackingItem
        fields = ("name",)
        widgets = {"name": forms.TextInput(attrs={"class": "form-control", "placeholder": "Add an item to pack…", "maxlength": "160"})}

class ExpenseForm(forms.ModelForm):
    class Meta:
        model = Expense
        fields = ("title", "category", "amount", "date", "notes")
        widgets = {
            "title": forms.TextInput(attrs={"class": "form-control", "placeholder": "Dinner, train ticket…"}),
            "category": forms.Select(attrs={"class": "form-select"}),
            "amount": forms.NumberInput(attrs={"class": "form-control", "min": "0.01", "step": "0.01", "placeholder": "0.00"}),
            "date": forms.DateInput(attrs={"type": "date", "class": "form-control"}),
            "notes": forms.TextInput(attrs={"class": "form-control", "placeholder": "Optional details"}),
        }

    def __init__(self, *args, trip, **kwargs):
        self.trip = trip
        super().__init__(*args, **kwargs)
        if not self.instance.pk:
            self.fields["date"].initial = trip.start_date

    def clean_date(self):
        day = self.cleaned_data["date"]
        if not self.trip.start_date <= day <= self.trip.end_date:
            raise forms.ValidationError("Choose a date within this trip.")
        return day

    def clean_amount(self):
        amount = self.cleaned_data["amount"]
        if amount <= 0:
            raise forms.ValidationError("Expense amount must be greater than zero.")
        return amount

class ShareTripForm(forms.Form):
    username = forms.CharField(max_length=150, label="TripMate username", widget=forms.TextInput(attrs={"class": "form-control", "placeholder": "Enter an existing username", "autocomplete": "off"}))
    role = forms.ChoiceField(choices=TripMembership.Role.choices, widget=forms.Select(attrs={"class": "form-select"}))

    def __init__(self, *args, trip, **kwargs):
        self.trip = trip
        super().__init__(*args, **kwargs)

    def clean_username(self):
        from django.contrib.auth.models import User
        username = self.cleaned_data["username"].strip()
        try:
            user = User.objects.get(username__iexact=username)
        except User.DoesNotExist:
            raise forms.ValidationError("No TripMate account found with that username.")
        except User.MultipleObjectsReturned:
            raise forms.ValidationError("Enter the username with its exact capitalization.")
        if user.pk == self.trip.owner_id:
            raise forms.ValidationError("The trip owner already has full access.")
        self.shared_user = user
        return username

    def save(self):
        membership, created = TripMembership.objects.update_or_create(
            trip=self.trip, user=self.shared_user,
            defaults={"role": self.cleaned_data["role"]},
        )
        return membership, created
