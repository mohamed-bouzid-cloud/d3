"""
FHIR Resource Validators
------------------------
Standalone helpers for strict FHIR R4 validation using the fhir.resources
library.  Call `validate_fhir_resource` from serializer `validate()` methods
or views when you need model-level FHIR conformance checking.
"""

from rest_framework.exceptions import ValidationError

try:
    from fhir.resources.patient import Patient as FHIRPatient
    from fhir.resources.observation import Observation as FHIRObservation
    FHIR_RESOURCES_AVAILABLE = True
except ImportError:
    FHIR_RESOURCES_AVAILABLE = False


# ---------------------------------------------------------------------------
# Supported resource types
# ---------------------------------------------------------------------------
_FHIR_CONSTRUCTORS = {}

if FHIR_RESOURCES_AVAILABLE:
    _FHIR_CONSTRUCTORS = {
        'Patient':     FHIRPatient,
        'Observation': FHIRObservation,
    }


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def validate_fhir_resource(data: dict, resource_type: str = 'Patient') -> bool:
    """
    Validate *data* against the FHIR R4 schema for *resource_type*.

    Parameters
    ----------
    data : dict
        The FHIR resource payload to validate.
    resource_type : str
        One of 'Patient' or 'Observation'.

    Returns
    -------
    bool
        ``True`` on success.

    Raises
    ------
    rest_framework.exceptions.ValidationError
        If validation fails or if fhir.resources is not installed.
    """
    if not FHIR_RESOURCES_AVAILABLE:
        raise ValidationError(
            {"fhir_validation": "fhir.resources package is not installed."}
        )

    constructor = _FHIR_CONSTRUCTORS.get(resource_type)
    if constructor is None:
        raise ValidationError(
            {"fhir_validation": f"Unsupported resource type: '{resource_type}'"}
        )

    try:
        constructor(**data)
        return True
    except Exception as exc:
        raise ValidationError({"fhir_validation": str(exc)}) from exc
