from django.contrib import admin
from .models import Patient, Observation, Practitioner, Encounter


@admin.register(Patient)
class PatientAdmin(admin.ModelAdmin):
    list_display  = ['identifier', 'family_name', 'given_name', 'gender', 'birth_date']
    search_fields = ['family_name', 'given_name']
    list_filter   = ['gender']


@admin.register(Observation)
class ObservationAdmin(admin.ModelAdmin):
    list_display  = ['id', 'patient', 'observation_type', 'value', 'unit', 'effective_date']
    search_fields = ['patient__family_name']
    list_filter   = ['observation_type']


@admin.register(Practitioner)
class PractitionerAdmin(admin.ModelAdmin):
    list_display  = ['identifier', 'family_name', 'given_name', 'role', 'specialty', 'active']
    search_fields = ['family_name', 'given_name', 'rpps_number']
    list_filter   = ['role', 'gender', 'active']


@admin.register(Encounter)
class EncounterAdmin(admin.ModelAdmin):
    list_display  = ['id', 'patient', 'practitioner', 'status', 'encounter_class', 'start_date']
    search_fields = ['patient__family_name', 'practitioner__family_name']
    list_filter   = ['status', 'encounter_class']
