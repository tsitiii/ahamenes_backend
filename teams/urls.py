from django.urls import path
from rest_framework.routers import DefaultRouter
from rest_framework_nested import routers
from .views import (
    TeamViewSet,
    MembershipApplicationViewSet,
    ProjectViewSet,
    TopLevelProjectViewSet,
    AchievementViewSet,
    EventViewSet,
    EventRegistrationViewSet,
    AboutStatsView,
)

router = DefaultRouter()

router.register(r'teams', TeamViewSet, basename='teams')
teams_router = routers.NestedDefaultRouter(router, r'teams', lookup='team')
teams_router.register(r'projects', ProjectViewSet, basename='team-projects')
teams_router.register(r'achievements', AchievementViewSet, basename='team-achievements')

router.register(r'membership/applications', MembershipApplicationViewSet)

# Top-level projects (read-only: list, retrieve, featured)
router.register(r'projects', TopLevelProjectViewSet, basename='projects')

router.register(r'events', EventViewSet, basename='events')
events_router = routers.NestedDefaultRouter(router, r'events', lookup='event')
events_router.register(r'registrations', EventRegistrationViewSet, basename='event-registrations')

extra_urlpatterns = [
    path('about/stats/', AboutStatsView.as_view(), name='about-stats'),
]

urlpatterns = router.urls + teams_router.urls + events_router.urls + extra_urlpatterns