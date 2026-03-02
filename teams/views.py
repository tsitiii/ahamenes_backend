from rest_framework import viewsets
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiTypes
from .models import (Team, MembershipApplication,
                    Project, Achievement, 
                    Event, EventRegistration)
from .serializers import (
    TeamSerializer,
    MembershipApplicationSerializer,
    ProjectSerializer,
    AchievementSerializer,
    EventSerializer, EventRegistrationSerializer
)

@extend_schema(
    request={
        'multipart/form-data': {
            'type': 'object',
            'properties': {
                'logo': {
                    'type': 'string',
                    'format': 'binary'
                },
                'name': {'type': 'string'},
                'slug': {'type': 'string'},
                'description': {'type': 'string'},
            }
        },
        'application/json': TeamSerializer
    }
)
class TeamViewSet(viewsets.ModelViewSet):
    queryset = Team.objects.all()
    serializer_class = TeamSerializer
    permission_classes = [AllowAny]
    parser_classes = (MultiPartParser, FormParser, JSONParser)

class MembershipApplicationViewSet(viewsets.ModelViewSet):
    queryset = MembershipApplication.objects.all()
    serializer_class = MembershipApplicationSerializer
    permission_classes = [AllowAny]

class ProjectViewSet(viewsets.ModelViewSet):
    serializer_class = ProjectSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        queryset = Project.objects.all()
        team_id = self.kwargs.get('team_pk')

        if team_id:
            queryset = queryset.filter(team_id=team_id)

        return queryset

    def perform_create(self, serializer):
        team_id = self.kwargs.get('team_pk')
        if team_id:
            serializer.save(team_id=team_id)
        else:
            serializer.save()

class AchievementViewSet(viewsets.ModelViewSet):
    queryset = Achievement.objects.all()
    serializer_class = AchievementSerializer
    permission_classes = [AllowAny]


class EventViewSet(viewsets.ModelViewSet):
    queryset = Event.objects.all()
    serializer_class = EventSerializer


class EventRegistrationViewSet(viewsets.ModelViewSet):
    queryset = EventRegistration.objects.all()
    serializer_class = EventRegistrationSerializer
