import datetime
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from .forms import RatingForm
from django.contrib import messages
from .models import Rating, Event
from .models import Event, User


def register(request):
    if request.method == "POST":
        email = request.POST.get("email")
        username = request.POST.get("username")
        is_organizer = request.POST.get("is-organizer") is not None
        password = request.POST.get("password")
        password_confirm = request.POST.get("password-confirm")

        errors = User.validate_new_user(email, username, password, password_confirm)

        if len(errors) > 0:
            return render(
                request,
                "accounts/register.html",
                {
                    "errors": errors,
                    "data": request.POST,
                },
            )
        else:
            user = User.objects.create_user(
                email=email, username=username, password=password, is_organizer=is_organizer
            )
            login(request, user)
            return redirect("events")

    return render(request, "accounts/register.html", {})


def login_view(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")

        user = authenticate(request, username=username, password=password)

        if user is None:
            return render(
                request, "accounts/login.html", {"error": "Usuario o contraseña incorrectos"}
            )

        login(request, user)
        return redirect("events")

    return render(request, "accounts/login.html")


def home(request):
    return render(request, "home.html")


@login_required
def events(request):
    events = Event.objects.all().order_by("scheduled_at")
    return render(
        request,
        "app/events.html",
        {"events": events, "user_is_organizer": request.user.is_organizer},
    )


from .forms import RatingForm

def event_detail(request, id):
    event = get_object_or_404(Event, pk=id)
    user_rating = None
    ratings = event.rating_set.filter(bl_baja=False)

    if request.user.is_authenticated:
        user_rating = Rating.objects.filter(event=event, user=request.user, bl_baja=False).first()

    user_is_organizer = request.user == event.organizer
    form = None

    if request.user.is_authenticated:
        if request.method == "POST":
            rating_value = request.POST.get("rating")
            title = request.POST.get("title")
            text = request.POST.get("text")


            existing_rating = Rating.objects.filter(event=event, user=request.user).first()

            if existing_rating:
                form = RatingForm(request.POST, instance=existing_rating)
            else:
                form = RatingForm(request.POST)

            if form.is_valid() and rating_value:
                rating = form.save(commit=False)
                rating.event = event
                rating.user = request.user
                rating.rating = int(rating_value)
                rating.bl_baja = False
                rating.save()

                messages.success(request, "Tu calificación se ha guardado.")
                return redirect("event_detail", id=event.id)
            else:
                messages.error(request, "Por favor, completá todos los campos.")
        else:
            form = RatingForm(instance=user_rating)

    #Conteo de calificaciones activas
    active_ratings_count = ratings.count()

    return render(request, "app/event_detail.html", {
        "event": event,
        "ratings": ratings,
        "user_rating": user_rating,
        "form": form,
        "user_is_organizer": user_is_organizer,
        "active_ratings_count": active_ratings_count,
    })


@login_required
def event_delete(request, id):
    user = request.user
    if not user.is_organizer:
        return redirect("events")

    if request.method == "POST":
        event = get_object_or_404(Event, pk=id)
        event.delete()
        return redirect("events")

    return redirect("events")


@login_required
def event_form(request, id=None):
    user = request.user

    if not user.is_organizer:
        return redirect("events")

    if request.method == "POST":
        title = request.POST.get("title")
        description = request.POST.get("description")
        date = request.POST.get("date")
        time = request.POST.get("time")

        [year, month, day] = date.split("-")
        [hour, minutes] = time.split(":")

        scheduled_at = timezone.make_aware(
            datetime.datetime(int(year), int(month), int(day), int(hour), int(minutes))
        )

        if id is None:
            Event.new(title, description, scheduled_at, request.user)
        else:
            event = get_object_or_404(Event, pk=id)
            event.update(title, description, scheduled_at, request.user)

        return redirect("events")

    event = {}
    if id is not None:
        event = get_object_or_404(Event, pk=id)

    return render(
        request,
        "app/event_form.html",
        {"event": event, "user_is_organizer": request.user.is_organizer},
    )

def add_or_edit_rating(request, event_id):
    event = get_object_or_404(Event, id=event_id)
    rating_instance = Rating.objects.filter(event=event, user=request.user, bl_baja=False).first()
    if request.method == "POST":
        form = RatingForm(request.POST, instance=rating_instance)
        rating_value = request.POST.get("rating")

        if form.is_valid() and rating_value:
            rating = form.save(commit=False)
            rating.event = event
            rating.user = request.user
            rating.rating = int(rating_value)

            rating.save()
            messages.success(request, "Tu calificación se ha guardado.")
            return redirect("event_detail", id=event.id)
        else:
            messages.error(request, "Por favor, completa todos los campos.")
    else:
        form = RatingForm(instance=rating_instance)

    return render(request, "app/add_rating.html", {
        "form": form,
        "event": event,
        "rating_instance": rating_instance,
    })
@login_required
def delete_rating(request, event_id, rating_id=None):
    event = get_object_or_404(Event, id=event_id)

    if rating_id:
        rating_instance = get_object_or_404(Rating, id=rating_id, event=event)
    else:
        rating_instance = Rating.objects.filter(event=event, user=request.user, bl_baja=False).first()

    if (
        rating_instance is None
        or (
            rating_instance.user != request.user
            and request.user != event.organizer
        )
    ):
        messages.error(request, "No tenés permiso para eliminar esta calificación.")
        return redirect("event_detail", id=event.id)

    rating_instance.bl_baja = True
    rating_instance.save()

    messages.success(request, "La calificación ha sido eliminada.")
    return redirect("event_detail", id=event.id)