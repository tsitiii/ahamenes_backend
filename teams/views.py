from django.utils import timezone
from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.decorators import action
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from rest_framework.views import APIView
from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiTypes, OpenApiResponse, OpenApiExample
from drf_spectacular.openapi import AutoSchema
from .models import (Team, MembershipApplication,
                    Project, Achievement, 
                    Event, EventRegistration)
from .serializers import (
    TeamSerializer,
    MembershipApplicationSerializer,
    ProjectSerializer,
    ProjectListSerializer,
    FeaturedProjectSerializer,
    AchievementSerializer,
    EventSerializer, EventRegistrationSerializer
)
from accounts.models import CustomUser
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
        
        return Response(stats,status=status.HTTP_200_OK)

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
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['post'])
    def review(self, request, pk=None):
        status_value = request.data.get('status')
        if status_value not in ['approved', 'rejected']:
            return Response({"error": "Invalid status. Use 'approved' or 'rejected'."}, status=status.HTTP_400_BAD_REQUEST)

        application = self.get_object()
        application.status = status_value
        application.reviewed_by = request.user
        application.reviewed_at = timezone.now()
        application.save()
        
        return Response(self.get_serializer(application).data, status=status.HTTP_200_OK)

# --- Nested under /teams/{team_pk}/projects/ ---
class ProjectViewSet(viewsets.ModelViewSet):
    """Handles create/update/delete — nested under a specific team."""
    serializer_class = ProjectSerializer

    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            return [AllowAny()]
        return [IsAuthenticated()]

    def get_queryset(self):
        queryset = Project.objects.select_related('team').all()
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


# --- Top-level /projects/ (read-only, public) ---
class TopLevelProjectViewSet(viewsets.ReadOnlyModelViewSet):
    """
    GET /api/v1/club_management/projects/          — paginated list of all projects
    GET /api/v1/club_management/projects/{id}/     — project detail
    GET /api/v1/club_management/projects/featured/ — featured projects (lightweight)
    """
    permission_classes = [AllowAny]
    serializer_class = ProjectListSerializer

    def get_queryset(self):
        return Project.objects.select_related('team', 'created_by').all()

    @extend_schema(
        parameters=[
            OpenApiParameter('limit', OpenApiTypes.INT, description='Max number of featured projects to return (default 6)')
        ]
    )
    @action(detail=False, methods=['get'], url_path='featured')
    def featured(self, request):
        """Returns a lightweight list of featured (most recent) projects."""
        limit = int(request.query_params.get('limit', 6))
        qs = self.get_queryset()[:limit]
        serializer = FeaturedProjectSerializer(qs, many=True)
        return Response({'results': serializer.data}, status=status.HTTP_200_OK)


# --- About stats ---
class AboutStatsView(APIView):
    """
    GET /api/v1/club_management/about/stats/
    Returns key club-wide statistics for the About page.
    """
    permission_classes = [AllowAny]

    @extend_schema(
        summary='Get About Page Stats',
        description='Returns a list of key club-wide statistics (members, teams, projects, events, achievements).',
        responses={
            200: OpenApiResponse(
                description='Club statistics',
                examples=[
                    OpenApiExample(
                        'Example Stats',
                        value={
                            'stats': [
                                {'key': 'total_members', 'value': '42', 'label': 'Active Members'},
                                {'key': 'total_teams',   'value': '5',  'label': 'Teams'},
                                {'key': 'total_projects','value': '18', 'label': 'Projects Built'},
                                {'key': 'total_events',  'value': '10', 'label': 'Events Hosted'},
                                {'key': 'total_achievements', 'value': '7', 'label': 'Achievements'},
                            ]
                        }
                    )
                ]
            )
        }
    )
    def get(self, request):
        stats = [
            {
                'key': 'total_members',
                'value': str(CustomUser.objects.filter(is_active=True).count()),
                'label': 'Active Members',
            },
            {
                'key': 'total_teams',
                'value': str(Team.objects.count()),
                'label': 'Teams',
            },
            {
                'key': 'total_projects',
                'value': str(Project.objects.count()),
                'label': 'Projects Built',
            },
            {
                'key': 'total_events',
                'value': str(Event.objects.count()),
                'label': 'Events Hosted',
            },
            {
                'key': 'total_achievements',
                'value': str(Achievement.objects.count()),
                'label': 'Achievements',
            },
        ]
        return Response({'stats': stats}, status=status.HTTP_200_OK)

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

    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            return [AllowAny()]
        return [IsTeamAdmin()]

    def get_queryset(self):
        queryset = Event.objects.all()
        # Archive logic (FR-24)
        archive = self.request.query_params.get('archive')
        now = timezone.now()
        
        if archive == 'true':
            queryset = queryset.filter(date__lt=now)
        elif archive == 'false':
            queryset = queryset.filter(date__gte=now)
        # Default behavior: show upcoming events unless archive is specified
        elif not archive:
            queryset = queryset.filter(date__gte=now)
            
        return queryset

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)


class EventRegistrationViewSet(viewsets.ModelViewSet):
    queryset = EventRegistration.objects.all()
    serializer_class = EventRegistrationSerializer

    def get_permissions(self):
        if self.action == 'create':
            return [AllowAny()]
        return [IsTeamAdmin()]

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
