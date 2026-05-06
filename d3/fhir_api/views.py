from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from django_filters import rest_framework as filters

from .models import Patient, Observation, Practitioner, Encounter
from .serializers import (
    PatientFHIRSerializer,
    ObservationFHIRSerializer,
    PractitionerFHIRSerializer,
    EncounterFHIRSerializer,
)


# ---------------------------------------------------------------------------
# Patient ViewSet
# ---------------------------------------------------------------------------

class PatientViewSet(viewsets.ModelViewSet):
    """
    CRUD endpoints for FHIR Patient resources.

    GET    /api/patients/               → list patients
    POST   /api/patients/               → create patient
    GET    /api/patients/{id}/          → retrieve patient
    PUT    /api/patients/{id}/          → update patient
    PATCH  /api/patients/{id}/          → partial update
    DELETE /api/patients/{id}/          → delete patient
    GET    /api/patients/{id}/observations/ → patient's observations (filterable)
    """

    queryset = Patient.objects.all().order_by('-created_at')
    serializer_class = PatientFHIRSerializer
    permission_classes = [AllowAny]
    filter_backends = [filters.DjangoFilterBackend]
    filterset_fields = ['gender', 'family_name']

    @action(detail=True, methods=['get'], url_path='observations')
    def observations(self, request, pk=None):
        """
        Returns all FHIR Observation resources for a given Patient.
        Supports optional query params:
          - date_from : filter effective_date >= date_from
          - date_to   : filter effective_date <= date_to
        """
        patient = self.get_object()
        obs = Observation.objects.filter(patient=patient).order_by('-effective_date')

        date_from = request.query_params.get('date_from')
        date_to   = request.query_params.get('date_to')

        if date_from:
            obs = obs.filter(effective_date__gte=date_from)
        if date_to:
            obs = obs.filter(effective_date__lte=date_to)

        serializer = ObservationFHIRSerializer(obs, many=True)
        return Response(serializer.data)


# ---------------------------------------------------------------------------
# Observation ViewSet
# ---------------------------------------------------------------------------

class ObservationViewSet(viewsets.ModelViewSet):
    """
    CRUD endpoints for FHIR Observation resources.

    GET    /api/observations/           → list observations
    POST   /api/observations/           → create observation
    GET    /api/observations/{id}/      → retrieve observation
    PUT    /api/observations/{id}/      → update observation
    PATCH  /api/observations/{id}/      → partial update
    DELETE /api/observations/{id}/      → delete observation

    Filterset supports:
      - patient              (exact)
      - observation_type     (exact)
      - effective_date       (exact / gte / lte)
      - value                (gte / lte)
    """

    queryset = (
        Observation.objects
        .select_related('patient')
        .all()
        .order_by('-effective_date')
    )
    serializer_class = ObservationFHIRSerializer
    permission_classes = [AllowAny]
    filter_backends = [filters.DjangoFilterBackend]
    filterset_fields = {
        'patient':          ['exact'],
        'observation_type': ['exact'],
        'effective_date':   ['exact', 'gte', 'lte'],
        'value':            ['gte', 'lte'],
    }


# ---------------------------------------------------------------------------
# Practitioner ViewSet
# ---------------------------------------------------------------------------

class PractitionerViewSet(viewsets.ModelViewSet):
    """
    CRUD endpoints for FHIR Practitioner resources.

    GET  /api/practitioners/         → list
    POST /api/practitioners/         → create
    GET  /api/practitioners/{id}/    → retrieve
    PUT  /api/practitioners/{id}/    → update
    GET  /api/practitioners/{id}/encounters/ → encounters by this practitioner
    """

    queryset = Practitioner.objects.all().order_by('family_name', 'given_name')
    serializer_class = PractitionerFHIRSerializer
    permission_classes = [AllowAny]
    filter_backends = [filters.DjangoFilterBackend]
    filterset_fields = ['gender', 'role', 'active', 'family_name']

    @action(detail=True, methods=['get'], url_path='encounters')
    def encounters(self, request, pk=None):
        """Returns all Encounters handled by this Practitioner."""
        practitioner = self.get_object()
        enc = Encounter.objects.filter(practitioner=practitioner).order_by('-start_date')
        return Response(EncounterFHIRSerializer(enc, many=True).data)


# ---------------------------------------------------------------------------
# Encounter ViewSet
# ---------------------------------------------------------------------------

class EncounterViewSet(viewsets.ModelViewSet):
    """
    CRUD endpoints for FHIR Encounter resources.

    GET  /api/encounters/         → list
    POST /api/encounters/         → create
    GET  /api/encounters/{id}/    → retrieve
    PUT  /api/encounters/{id}/    → update
    DELETE /api/encounters/{id}/  → delete

    Filterset supports:
      - patient        (exact)
      - practitioner   (exact)
      - status         (exact)
      - encounter_class (exact)
      - start_date     (exact / gte / lte)
    """

    queryset = (
        Encounter.objects
        .select_related('patient', 'practitioner')
        .all()
        .order_by('-start_date')
    )
    serializer_class = EncounterFHIRSerializer
    permission_classes = [AllowAny]
    filter_backends = [filters.DjangoFilterBackend]
    filterset_fields = {
        'patient':         ['exact'],
        'practitioner':    ['exact'],
        'status':          ['exact'],
        'encounter_class': ['exact'],
        'start_date':      ['exact', 'gte', 'lte'],
    }
