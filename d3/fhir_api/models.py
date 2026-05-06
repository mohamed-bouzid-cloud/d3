from django.db import models
import uuid

# Create your models here.
class Patient(models.Model):
    GENDER_CHOICES = [
        ('male','Male'),
        ('female','Female'),
        ('other','Other'),
        ('unknown','Unknown')
    ]
    identifier = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    family_name = models.CharField(max_length=100)
    given_name = models.CharField(max_length=100)
    birth_date = models.DateField()
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    class Meta:
        indexes = [models.Index(fields=['identifier']),
        models.Index(fields=['family_name','given_name'])]
    def __str__(self):
        return f"{self.family_name} {self.given_name}"

class Observation(models.Model):
    OBS_TYPES=[('blood-pressure','Tension artérielle'),
('heart-rate','Fréquence cardiaque'),
('temperature','Température corporelle'),
('weight','Poids'),
('height','Taille')]
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE)
    observation_type = models.CharField(max_length=100, choices=OBS_TYPES)
    value = models.CharField(max_length=100)
    unit = models.CharField(max_length=100)
    effective_date = models.DateTimeField(auto_now_add=True)
    created_at = models.DateTimeField(auto_now_add=True)
    class Meta:
        indexes = [models.Index(fields=['patient','effective_date']),
        models.Index(fields=['observation_type','effective_date'])]
    def __str__(self): return f"{self.patient} - {self.observation_type}:{self.value} {self.unit}"


# ---------------------------------------------------------------------------
# Practitioner — FHIR R4 Practitioner resource
# A healthcare provider (doctor, nurse, specialist, etc.)
# ---------------------------------------------------------------------------
class Practitioner(models.Model):
    GENDER_CHOICES = [
        ('male',    'Male'),
        ('female',  'Female'),
        ('other',   'Other'),
        ('unknown', 'Unknown'),
    ]
    ROLE_CHOICES = [
        ('doctor',          'Médecin'),
        ('nurse',           'Infirmier(e)'),
        ('pharmacist',      'Pharmacien(ne)'),
        ('physiotherapist', 'Kinésithérapeute'),
        ('specialist',      'Spécialiste'),
        ('other',           'Autre'),
    ]

    identifier  = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    family_name = models.CharField(max_length=100)
    given_name  = models.CharField(max_length=100)
    gender      = models.CharField(max_length=10, choices=GENDER_CHOICES, default='unknown')
    role        = models.CharField(max_length=50, choices=ROLE_CHOICES, default='doctor')
    # RPPS = Répertoire Partagé des Professionnels de Santé (French healthcare ID)
    rpps_number = models.CharField(max_length=11, unique=True, blank=True, null=True)
    specialty   = models.CharField(max_length=150, blank=True)
    phone       = models.CharField(max_length=20, blank=True)
    email       = models.EmailField(blank=True)
    active      = models.BooleanField(default=True)
    created_at  = models.DateTimeField(auto_now_add=True)
    updated_at  = models.DateTimeField(auto_now=True)

    class Meta:
        indexes = [
            models.Index(fields=['family_name', 'given_name']),
            models.Index(fields=['role']),
        ]

    def __str__(self):
        return f"Dr. {self.family_name} {self.given_name} ({self.get_role_display()})"


# ---------------------------------------------------------------------------
# Encounter — FHIR R4 Encounter resource
# A medical visit: one Patient meets one Practitioner
# ---------------------------------------------------------------------------
class Encounter(models.Model):
    STATUS_CHOICES = [
        ('planned',    'Planifiée'),
        ('in-progress','En cours'),
        ('finished',   'Terminée'),
        ('cancelled',  'Annulée'),
        ('unknown',    'Inconnue'),
    ]
    CLASS_CHOICES = [
        ('AMB',  'Ambulatoire'),   # outpatient
        ('IMP',  'Hospitalisation'),  # inpatient
        ('EMER', 'Urgences'),
        ('HH',   'Soins à domicile'),
    ]

    patient        = models.ForeignKey(Patient,      on_delete=models.CASCADE, related_name='encounters')
    practitioner   = models.ForeignKey(Practitioner, on_delete=models.SET_NULL, null=True, blank=True, related_name='encounters')
    status         = models.CharField(max_length=20, choices=STATUS_CHOICES, default='planned')
    encounter_class = models.CharField(max_length=10, choices=CLASS_CHOICES, default='AMB')
    reason         = models.TextField(blank=True, help_text="Raison de la consultation")
    start_date     = models.DateTimeField()
    end_date       = models.DateTimeField(null=True, blank=True)
    created_at     = models.DateTimeField(auto_now_add=True)
    updated_at     = models.DateTimeField(auto_now=True)

    class Meta:
        indexes = [
            models.Index(fields=['patient', 'start_date']),
            models.Index(fields=['practitioner', 'start_date']),
            models.Index(fields=['status']),
        ]

    def __str__(self):
        return f"Encounter {self.id} — {self.patient} / {self.practitioner} [{self.get_status_display()}]"
