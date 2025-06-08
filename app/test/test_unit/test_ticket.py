import unittest
from unittest import TestCase
from unittest.mock import patch, MagicMock
from app.models import *
from app.views import *
from django.core.exceptions import ValidationError
from django.test import TestCase
from app.models import User, Venue, Event, Ticket
from app.views import ticket_excede_capacidad_maxima
from django.utils import timezone

class TicketUsuarioLimiteTest(TestCase):

    def setUp(self):
        self.user = User.objects.create(username='test_user')
        self.venue = Venue.objects.create(name='Teatro', capacity=100)
        self.event = Event.objects.create(
            title='Evento',
            description='Descripción del evento',
            scheduled_at=timezone.now(),
            organizer=self.user,
            venue=self.venue
        )

    def test_usuario_hasta_4_tickets(self):
        # Total = 2 + 2 = 4
        Ticket.objects.create(user=self.user, event=self.event, quantity=2, buy_date=timezone.now())
        Ticket.objects.create(user=self.user, event=self.event, quantity=2, buy_date=timezone.now())

        resultado = Ticket.ticket_excede_limite_usuario(
            user_id=self.user.id,
            event_id=self.event.id,
            nueva_cantidad=0
        )
        self.assertFalse(resultado)

    def test_limite_4_tickets(self):
        t1 = Ticket.objects.create(user=self.user, event=self.event, quantity=3, buy_date=timezone.now())
        Ticket.objects.create(user=self.user, event=self.event, quantity=1, buy_date=timezone.now())

        # Sumar 2, el total ahora sería 2 (nuevo) + 1 = 3, esta OK
        resultado = Ticket.ticket_excede_limite_usuario(
            user_id=self.user.id,
            event_id=self.event.id,
            nueva_cantidad=2,
            ticket_id=t1.id
        )
        self.assertFalse(resultado)

        # Sumar 4, excede
        resultado = Ticket.ticket_excede_limite_usuario(
            user_id=self.user.id,
            event_id=self.event.id,
            nueva_cantidad=4,
            ticket_id=t1.id
        )
        self.assertTrue(resultado)

    def test_editar_superando_limite(self):
        t1 = Ticket.objects.create(user=self.user, event=self.event, quantity=2, buy_date=timezone.now())
        Ticket.objects.create(user=self.user, event=self.event, quantity=2, buy_date=timezone.now())

        # Modificar t1 a 3, el total sería 3 + 2 = 5, entonces excede
        resultado = Ticket.ticket_excede_limite_usuario(
            user_id=self.user.id,
            event_id=self.event.id,
            nueva_cantidad=3,
            ticket_id=t1.id
        )
        self.assertTrue(resultado)

    def test_editar_dentro_del_limite(self):
        t1 = Ticket.objects.create(user=self.user, event=self.event, quantity=2, buy_date=timezone.now())
        Ticket.objects.create(user=self.user, event=self.event, quantity=1, buy_date=timezone.now())

        # Modificar t1 a 3, el total sería 3 + 1 = 4, por lo tanto es válido
        resultado = Ticket.ticket_excede_limite_usuario(
            user_id=self.user.id,
            event_id=self.event.id,
            nueva_cantidad=3,
            ticket_id=t1.id
        )
        self.assertFalse(resultado, "No debería exceder el límite de tickets")



    @patch('app.models.Ticket.objects.filter')
    def test_no_excede_capacidad(self, mock_filter):
        # Crear un mock para el objeto Event con venue.capacity
        mock_venue = MagicMock(capacity=100)
        mock_event = MagicMock(venue=mock_venue)

        # Mockear el aggregate para devolver 90 tickets vendidos
        # Ahora por mas que nadie haya comprado tickets, habra 90 espacios ocupados
        mock_queryset = MagicMock()
        mock_queryset.aggregate.return_value = {'total': 90}
        mock_filter.return_value = mock_queryset

        # Compro 10 tickets mas, llenando por completo el espacio
        resultado = ticket_excede_capacidad_maxima(mock_event, 10)
        self.assertFalse(resultado) # Deberia devolver false, ya que no sobrepasamos el limite

    @patch('app.models.Ticket.objects.filter')
    def test_excede_capacidad(self, mock_filter):
        mock_venue = MagicMock(capacity=100)
        mock_event = MagicMock(venue=mock_venue)

        mock_queryset = MagicMock()
        mock_queryset.aggregate.return_value = {'total': 100}
        mock_filter.return_value = mock_queryset

        # El espacio ya esta lleno, voy a intentar comprar un ticket solo
        resultado = ticket_excede_capacidad_maxima(mock_event, 1)
        self.assertTrue(resultado) # Deberia devolver true, ya que sobrepasamos el limite
        if __name__ == '__main__':
            unittest.main()
