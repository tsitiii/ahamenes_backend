from django.utils import timezone
from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.decorators import action
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
from accounts.permissions import IsTeamAdmin, IsSuperAdmin, IsTeamManager

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

    def get_permissions(self):
        if self.action in ['create', 'destroy']:
            return [IsSuperAdmin()]
        if self.action in ['update', 'partial_update', 'dashboard']:
            return [IsTeamManager()]
        return [AllowAny()]

    @action(detail=True, methods=['get'])
    def dashboard(self, request, pk=None):
        team = self.get_object()
        
        # Aggregate data
        stats = {
            "total_members": team.members.count(),
            "total_projects": team.projects.count(),
            "total_achievements": team.achievements.count(),
            "members": team.members.values('id', 'full_name', 'email', 'role'),
            "recent_projects": team.projects.values('id', 'title', 'created_at')[:5],
            "recent_achievements": team.achievements.values('id', 'title', 'date')[:5]
        }
        
        return Response({
            "success": True,
            "data": stats,
            "message": f"Dashboard data for {team.name}"
        })

class MembershipApplicationViewSet(viewsets.ModelViewSet):
    queryset = MembershipApplication.objects.all()
    serializer_class = MembershipApplicationSerializer
    permission_classes = [AllowAny]

    def get_permissions(self):
        if self.action in ['review', 'list', 'retrieve', 'update', 'partial_update', 'destroy']:
            return [IsTeamAdmin()]
        return [AllowAny()]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            self.perform_create(serializer)
            return Response({
                "success": True,
                "data": serializer.data,
                "message": "Application submitted successfully"
            }, status=status.HTTP_201_CREATED)
        return Response({
            "success": False,
            "error": serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['post'])
    def review(self, request, pk=None):
        status_value = request.data.get('status')
        if status_value not in ['approved', 'rejected']:
            return Response({
                "success": False,
                "error": "Invalid status. Use 'approved' or 'rejected'."
            }, status=status.HTTP_400_BAD_REQUEST)

        application = self.get_object()
        application.status = status_value
        application.reviewed_by = request.user
        application.reviewed_at = timezone.now()
        application.save()
        
        return Response({
            "success": True,
            "data": self.get_serializer(application).data,
            "message": f"Application {status_value} successfully"
        })

class ProjectViewSet(viewsets.ModelViewSet):
    serializer_class = ProjectSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        queryset = Project.objects.all()
        team_id = self.kwargs.get('team_pk')

        if team_id:
            queryset = queryset.filter(team_id=team_id)

        return queryset

    def perform_create(self, serializer):
        team_id = self.kwargs.get('team_pk')
        if team_id:
            serializer.save(team_id=team_id, created_by=self.request.user)
        else:
            serializer.save(created_by=self.request.user)

class AchievementViewSet(viewsets.ModelViewSet):
    serializer_class = AchievementSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        queryset = Achievement.objects.all()
        team_id = self.kwargs.get('team_pk')
        if team_id:
            queryset = queryset.filter(team_id=team_id)
        return queryset

    def perform_create(self, serializer):
        team_id = self.kwargs.get('team_pk')
        if team_id:
            serializer.save(team_id=team_id, created_by=self.request.user)
        else:
            serializer.save(created_by=self.request.user)


class EventViewSet(viewsets.ModelViewSet):
    queryset = Event.objects.all()
    serializer_class = EventSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)


class EventRegistrationViewSet(viewsets.ModelViewSet):
    queryset = EventRegistration.objects.all()
    serializer_class = EventRegistrationSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        queryset = EventRegistration.objects.all()
        event_id = self.kwargs.get('event_pk')
        if event_id:
            queryset = queryset.filter(event_id=event_id)
        return queryset

    def perform_create(self, serializer):
        event_id = self.kwargs.get('event_pk')
        if event_id:
            serializer.save(event_id=event_id)
        else:
            serializer.save()
