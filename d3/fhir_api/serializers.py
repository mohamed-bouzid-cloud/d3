from rest_framework import serializers
from .models import Patient, Observation, Practitioner, Encounter

# Optional: only used if fhir.resources is installed
try:
    from fhir.resources.patient import Patient as FHIRPatient
    from fhir.resources.observation import Observation as FHIRObservation
    FHIR_RESOURCES_AVAILABLE = True
except ImportError:
    FHIR_RESOURCES_AVAILABLE = False


# ---------------------------------------------------------------------------
# LOINC mapping for Observation types
# ---------------------------------------------------------------------------
LOINC_MAP = {
    'blood-pressure': '85354-9',
    'heart-rate':     '8867-4',
    'temperature':    '8310-5',
    'weight':         '29463-7',
    'height':         '8302-2',
}


# ---------------------------------------------------------------------------
# Patient FHIR Serializer
# ---------------------------------------------------------------------------

class PatientFHIRSerializer(serializers.ModelSerializer):
    """
    Serializes/deserializes Patient instances using the FHIR R4 Patient resource
    structure.  The model uses `identifier` as its UUID primary key.
    """

    class Meta:
        model = Patient
        fields = [
            'identifier',
            'family_name',
            'given_name',
            'gender',
            'birth_date',
        ]

    # ------------------------------------------------------------------
    # Serialization  (instance → FHIR JSON)
    # ------------------------------------------------------------------
    def to_representation(self, instance):
        fhir_data = {
            "resourceType": "Patient",
            "id": str(instance.identifier),
            "meta": {
                "lastUpdated": instance.updated_at.isoformat()
            },
            "identifier": [
                {
                    "system": "https://hopital.fr/identifiers",
                    "value":  str(instance.identifier),
                }
            ],
            "name": [
                {
                    "family": instance.family_name,
                    "given":  [instance.given_name],
                }
            ],
            "gender":    instance.gender,
            "birthDate": instance.birth_date.isoformat(),
        }

        if FHIR_RESOURCES_AVAILABLE:
            try:
                return FHIRPatient(**fhir_data).dict()
            except Exception:
                pass  # Fall back to raw dict on validation errors

        return fhir_data

    # ------------------------------------------------------------------
    # Deserialization  (FHIR JSON → internal data)
    # ------------------------------------------------------------------
    def to_internal_value(self, data):
        # Validate resourceType
        if data.get('resourceType') != 'Patient':
            raise serializers.ValidationError(
                {"resourceType": "Doit être 'Patient'"}
            )

        internal_data = {
            "family_name": (
                data['name'][0]['family']
                if data.get('name') else None
            ),
            "given_name": (
                data['name'][0]['given'][0]
                if data.get('name') and data['name'][0].get('given') else None
            ),
            "gender":     data.get('gender'),
            "birth_date": data.get('birthDate'),
        }

        return super().to_internal_value(internal_data)


# ---------------------------------------------------------------------------
# Observation FHIR Serializer
# ---------------------------------------------------------------------------

class ObservationFHIRSerializer(serializers.ModelSerializer):
    """
    Serializes/deserializes Observation instances using the FHIR R4 Observation
    resource structure.
    """

    # Write-only field: client sends a Patient identifier (UUID) string
    patient_id = serializers.PrimaryKeyRelatedField(
        queryset=Patient.objects.all(),
        source='patient',
        write_only=True,
    )

    class Meta:
        model = Observation
        fields = [
            'id',
            'patient_id',
            'observation_type',
            'value',
            'unit',
            'effective_date',
        ]

    # ------------------------------------------------------------------
    # Serialization  (instance → FHIR JSON)
    # ------------------------------------------------------------------
    def to_representation(self, instance):
        loinc_code = LOINC_MAP.get(instance.observation_type, 'unknown')

        fhir_data = {
            "resourceType": "Observation",
            "id":     str(instance.id),
            "status": "final",
            "code": {
                "coding": [
                    {
                        "system":  "http://loinc.org",
                        "code":    loinc_code,
                        "display": instance.get_observation_type_display(),
                    }
                ]
            },
            "subject": {
                "reference": f"Patient/{instance.patient.identifier}",
                "display":   f"{instance.patient.family_name} {instance.patient.given_name}",
            },
            "effectiveDateTime": instance.effective_date.isoformat(),
            "valueQuantity": {
                "value":  float(instance.value),
                "unit":   instance.unit,
                "system": "http://unitsofmeasure.org",
                "code":   instance.unit,
            },
            "issued": instance.created_at.isoformat(),
        }

        if FHIR_RESOURCES_AVAILABLE:
            try:
                return FHIRObservation(**fhir_data).dict()
            except Exception:
                pass  # Fall back to raw dict on validation errors

        return fhir_data

    # ------------------------------------------------------------------
    # Deserialization  (FHIR JSON → internal data)
    # ------------------------------------------------------------------
    def to_internal_value(self, data):
        if data.get('resourceType') != 'Observation':
            raise serializers.ValidationError(
                {"resourceType": "Doit être 'Observation'"}
            )

        # Extract patient identifier from "Patient/<uuid>" reference
        subject_ref = data.get('subject', {}).get('reference', '')
        patient_id = subject_ref.split('/')[-1] if subject_ref else None

        value_quantity = data.get('valueQuantity', {})

        internal_data = {
            "patient_id":        patient_id,
            "observation_type":  (
                data.get('code', {})
                    .get('coding', [{}])[0]
                    .get('display', '')
            ),
            "value": str(value_quantity.get('value', '')),
            "unit":  value_quantity.get('unit', ''),
            "effective_date": data.get('effectiveDateTime'),
        }

        return super().to_internal_value(internal_data)


# ---------------------------------------------------------------------------
# Practitioner FHIR Serializer
# ---------------------------------------------------------------------------

class PractitionerFHIRSerializer(serializers.ModelSerializer):
    """
    Serializes/deserializes Practitioner instances using FHIR R4 Practitioner
    resource structure.
    """

    class Meta:
        model  = Practitioner
        fields = [
            'identifier', 'family_name', 'given_name',
            'gender', 'role', 'rpps_number',
            'specialty', 'phone', 'email', 'active',
        ]

    # ------------------------------------------------------------------
    # Serialization  (instance → FHIR JSON)
    # ------------------------------------------------------------------
    def to_representation(self, instance):
        return {
            "resourceType": "Practitioner",
            "id": str(instance.identifier),
            "meta": {"lastUpdated": instance.updated_at.isoformat()},
            "active": instance.active,
            "role": instance.role,
            "specialty": instance.specialty,
            "email": instance.email,
            "phone": instance.phone,
            "identifier": [
                {
                    "system": "https://hopital.fr/rpps",
                    "value":  instance.rpps_number or str(instance.identifier),
                }
            ],
            "name": [
                {
                    "family": instance.family_name,
                    "given":  [instance.given_name],
                    "prefix": ["Dr."] if instance.role == "doctor" else [],
                }
            ],
            "gender": instance.gender,
            # FHIR qualification — maps role + specialty
            "qualification": [
                {
                    "code": {
                        "coding": [
                            {
                                "system":  "https://hopital.fr/roles",
                                "code":    instance.role,
                                "display": instance.get_role_display(),
                            }
                        ],
                        "text": instance.specialty or instance.get_role_display(),
                    }
                }
            ],
            "telecom": [
                *( [{"system": "phone", "value": instance.phone, "use": "work"}]
                   if instance.phone else [] ),
                *( [{"system": "email", "value": instance.email, "use": "work"}]
                   if instance.email else [] ),
            ],
        }

    # ------------------------------------------------------------------
    # Deserialization  (FHIR JSON → internal data)
    # ------------------------------------------------------------------
    def to_internal_value(self, data):
        if data.get('resourceType') != 'Practitioner':
            raise serializers.ValidationError(
                {"resourceType": "Doit être 'Practitioner'"}
            )

        name = data.get('name', [{}])[0]
        telecom = data.get('telecom', [])
        phone = next((t['value'] for t in telecom if t.get('system') == 'phone'), '')
        email = next((t['value'] for t in telecom if t.get('system') == 'email'), '')

        qualification = data.get('qualification', [{}])[0]
        role_coding = qualification.get('code', {}).get('coding', [{}])[0]

        internal_data = {
            "family_name": name.get('family'),
            "given_name":  name.get('given', [''])[0],
            "gender":      data.get('gender', 'unknown'),
            "role":        role_coding.get('code', 'other'),
            "specialty":   qualification.get('code', {}).get('text', ''),
            "rpps_number": (data.get('identifier') or [{}])[0].get('value'),
            "phone":       phone,
            "email":       email,
            "active":      data.get('active', True),
        }

        return super().to_internal_value(internal_data)


# ---------------------------------------------------------------------------
# Encounter FHIR Serializer
# ---------------------------------------------------------------------------

class EncounterFHIRSerializer(serializers.ModelSerializer):
    """
    Serializes/deserializes Encounter instances using FHIR R4 Encounter
    resource structure.
    """

    patient_id     = serializers.PrimaryKeyRelatedField(
        queryset=Patient.objects.all(),
        source='patient',
        write_only=True,
    )
    practitioner_id = serializers.PrimaryKeyRelatedField(
        queryset=Practitioner.objects.all(),
        source='practitioner',
        write_only=True,
        required=False,
        allow_null=True,
    )

    class Meta:
        model  = Encounter
        fields = [
            'id', 'patient_id', 'practitioner_id',
            'status', 'encounter_class', 'reason',
            'start_date', 'end_date',
        ]

    # ------------------------------------------------------------------
    # Serialization  (instance → FHIR JSON)
    # ------------------------------------------------------------------
    def to_representation(self, instance):
        fhir = {
            "resourceType": "Encounter",
            "id":     str(instance.id),
            "meta":   {"lastUpdated": instance.updated_at.isoformat()},
            "status": instance.status,
            # FHIR class uses a Coding object
            "class": {
                "system":  "http://terminology.hl7.org/CodeSystem/v3-ActCode",
                "code":    instance.encounter_class,
                "display": instance.get_encounter_class_display(),
            },
            "subject": {
                "reference": f"Patient/{instance.patient.identifier}",
                "display":   str(instance.patient),
            },
            "period": {
                "start": instance.start_date.isoformat(),
                **({"end": instance.end_date.isoformat()} if instance.end_date else {}),
            },
        }

        # Add reason if present
        if instance.reason:
            fhir["reasonCode"] = [{"text": instance.reason}]

        # Add practitioner participant if present
        if instance.practitioner:
            fhir["participant"] = [
                {
                    "individual": {
                        "reference": f"Practitioner/{instance.practitioner.identifier}",
                        "display":   str(instance.practitioner),
                    }
                }
            ]

        return fhir

    # ------------------------------------------------------------------
    # Deserialization  (FHIR JSON → internal data)
    # ------------------------------------------------------------------
    def to_internal_value(self, data):
        if data.get('resourceType') != 'Encounter':
            raise serializers.ValidationError(
                {"resourceType": "Doit être 'Encounter'"}
            )

        subject_ref = data.get('subject', {}).get('reference', '')
        patient_id  = subject_ref.split('/')[-1] if subject_ref else None

        participant = (data.get('participant') or [{}])[0]
        prac_ref    = participant.get('individual', {}).get('reference', '')
        prac_id     = prac_ref.split('/')[-1] if prac_ref else None

        period = data.get('period', {})

        internal_data = {
            "patient_id":      patient_id,
            "practitioner_id": prac_id,
            "status":          data.get('status', 'planned'),
            "encounter_class": data.get('class', {}).get('code', 'AMB'),
            "reason":          (data.get('reasonCode') or [{}])[0].get('text', ''),
            "start_date":      period.get('start'),
            "end_date":        period.get('end'),
        }

        return super().to_internal_value(internal_data)
