from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'patients',       views.PatientViewSet,       basename='patient')
router.register(r'observations',   views.ObservationViewSet,   basename='observation')
router.register(r'practitioners',  views.PractitionerViewSet,  basename='practitioner')
router.register(r'encounters',     views.EncounterViewSet,     basename='encounter')

urlpatterns = [
    path('', include(router.urls)),
]
