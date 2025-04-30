import datetime
from django.contrib.auth import authenticate, login
from django.db import IntegrityError
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

@login_required
def event_detail(request, id):
    event = get_object_or_404(Event, pk=id)
    #Busca los ratings activos
    visible_ratings = event.rating_set.filter(bl_baja=False, is_current=True)
    
    user_rating = None
    if request.user.is_authenticated:
        user_rating = Rating.objects.filter(user=request.user, event=event, is_current=True, bl_baja=False).first()
    
    return render(request, "app/event_detail.html", {
        "event": event,
        "ratings": visible_ratings,
        "user_rating": user_rating
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

from django.db import IntegrityError
from django.db.transaction import atomic

@login_required
def create_rating(request, event_id):
    event = get_object_or_404(Event, pk=event_id)
    
    if request.method == "POST":
        form = RatingForm(request.POST)
        rating_value = request.POST.get("rating", "0")
        
        if form.is_valid() and 1 <= int(rating_value) <= 5:
            # Desactiva los ratings del usuario
            Rating.objects.filter(
                event=event,
                user=request.user,
                is_current=True
            ).update(is_current=False)
            
            # Crear nueva calificación
            Rating.objects.create(
                event=event,
                user=request.user,
                title=form.cleaned_data['title'],
                text=form.cleaned_data['text'],
                rating=int(rating_value),
                is_current=True,
                bl_baja=False
            )
            messages.success(request, "Calificación guardada correctamente")
            return redirect("event_detail", id=event.id)
        else:
            messages.error(request, "Error en el formulario. Verifica los datos.")
    
    # Muestra formulario
    form = RatingForm()
    return render(request, "app/create_rating.html", {
        "form": form,
        "event": event
    })


@login_required
def update_rating(request, event_id, rating_id):
    event = get_object_or_404(Event, pk=event_id)
    rating = get_object_or_404(Rating, pk=rating_id, user=request.user)
    
    if request.method == "POST":
        form = RatingForm(request.POST, instance=rating)
        rating_value = request.POST.get("rating", str(rating.rating))
        
        if form.is_valid() and 1 <= int(rating_value) <= 5:
            form.save()
            messages.success(request, "Calificación actualizada correctamente")
            return redirect("event_detail", id=event.id)
        else:
            messages.error(request, "Error en el formulario")
    
    form = RatingForm(instance=rating)
    return render(request, "app/update_rating.html", {
        "form": form,
        "event": event,
        "rating": rating
    })

@login_required
def list_ratings(request, event_id):
    event = get_object_or_404(Event, pk=event_id)
    ratings = event.rating_set.filter(bl_baja=False).order_by('-created_at')
    user_rating = ratings.filter(user=request.user).first()
    
    return render(request, "app/list_ratings.html", {
        "event": event,
        "ratings": ratings,
        "user_rating": user_rating
    })
@login_required
def delete_rating(request, event_id, rating_id):
    rating = get_object_or_404(Rating, id=rating_id, event_id=event_id)

    if request.user == rating.user or request.user == rating.event.organizer:
        rating.soft_delete()  #Manejo de la baja logica
        messages.success(request, "Calificación eliminada correctamente.")
    else:
        messages.error(request, "No tienes permiso para eliminar esta calificación.")

    return redirect('event_detail', id=event_id)
