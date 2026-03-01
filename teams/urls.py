from rest_framework.routers import DefaultRouter
from rest_framework_nested import routers
from .views import (
    TeamViewSet,
    MembershipApplicationViewSet,
    ProjectViewSet,
    AchievementViewSet
)

router = DefaultRouter()
router.register(r'teams', TeamViewSet, basename='teams')
teams_router = routers.NestedDefaultRouter(router, r'teams', lookup='team')
teams_router.register(r'projects', ProjectViewSet, basename='team-projects')

router.register(r'membership/applications', MembershipApplicationViewSet)

router.register(r'achievements', AchievementViewSet)

urlpatterns = router.urls + teams_router.urls