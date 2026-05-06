import os
import django
import random
from datetime import date, timedelta

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from fhir_api.models import Patient, Observation, Practitioner, Encounter

def seed_data():
    print("Seeding FHIR Sample Data...")

    # 1. Create Practitioners
    p_data = [
        {"family_name": "House", "given_name": "Gregory", "role": "doctor", "specialty": "Diagnostic Medicine"},
        {"family_name": "Wilson", "given_name": "James", "role": "doctor", "specialty": "Oncology"},
        {"family_name": "Cuddy", "given_name": "Lisa", "role": "doctor", "specialty": "Endocrinology"},
    ]
    practitioners = []
    for p in p_data:
        prac, _ = Practitioner.objects.get_or_create(
            family_name=p['family_name'],
            given_name=p['given_name'],
            defaults={
                "role": p['role'],
                "specialty": p['specialty'],
                "gender": "unknown",
                "active": True
            }
        )
        practitioners.append(prac)

    # 2. Create Patients
    patients_data = [
        {"family": "Doe", "given": "John", "gender": "male", "birth": date(1985, 5, 20)},
        {"family": "Smith", "given": "Jane", "gender": "female", "birth": date(1992, 10, 12)},
        {"family": "Brown", "given": "Charlie", "gender": "male", "birth": date(2010, 3, 5)},
        {"family": "Miller", "given": "Alice", "gender": "female", "birth": date(1978, 12, 30)},
        {"family": "Wilson", "given": "Robert", "gender": "male", "birth": date(1960, 1, 15)},
    ]
    
    patients = []
    for p in patients_data:
        pat, _ = Patient.objects.get_or_create(
            family_name=p['family'],
            given_name=p['given'],
            defaults={
                "gender": p['gender'],
                "birth_date": p['birth']
            }
        )
        patients.append(pat)

    # 3. Create Observations (Vitals)
    obs_types = [
        ("blood-pressure", "120", "mmHg"),
        ("heart-rate", "72", "bpm"),
        ("temperature", "37.5", "Cel"),
        ("weight", "75", "kg"),
        ("height", "180", "cm"),
    ]

    for pat in patients:
        # Create 3 random observations for each patient
        sampled_obs = random.sample(obs_types, 3)
        for o in sampled_obs:
            Observation.objects.create(
                patient=pat,
                observation_type=o[0],
                value=str(float(o[1]) + random.uniform(-5, 5)),
                unit=o[2],
                effective_date=date.today() - timedelta(days=random.randint(0, 30))
            )

    # 4. Create Encounters
    for pat in patients:
        Encounter.objects.create(
            patient=pat,
            practitioner=random.choice(practitioners),
            status="finished",
            encounter_class="AMB",
            reason="Routine Checkup",
            start_date=date.today() - timedelta(days=random.randint(1, 10))
        )

    print("Seeding Complete! Refresh the dashboard to see your data.")

if __name__ == "__main__":
    seed_data()
