from rest_framework import viewsets, permissions, status as http_status
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiTypes
from .models import BlogPost, Comment
from .serializers import BlogPostSerializer, CommentSerializer
from accounts.permissions import IsSuperAdmin


@extend_schema(
    request={
        'multipart/form-data': {
            'type': 'object',
            'properties': {
                'featured_image': {
                    'type': 'string',
                    'format': 'binary'
                },
                'title': {'type': 'string'},
                'slug': {'type': 'string'},
                'content': {'type': 'string'},
                'category': {'type': 'string'},
                'status': {'type': 'string'},
                'author_id': {'type': 'string', 'format': 'uuid'},
                'published_at': {'type': 'string', 'format': 'date-time'},
            }
        },
        'application/json': BlogPostSerializer
    }
)
class BlogPostViewSet(viewsets.ModelViewSet):
    queryset = BlogPost.objects.all()
    serializer_class = BlogPostSerializer
    parser_classes = (MultiPartParser, FormParser, JSONParser)

    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            return [permissions.AllowAny()]
        if self.action == 'create':
            return [permissions.IsAuthenticated()]
        if self.action in ['update', 'partial_update', 'destroy']:
            return [IsSuperAdmin()]
        return [permissions.IsAuthenticated()]

    def get_queryset(self):
        queryset = BlogPost.objects.all()
        # Public users see only published posts
        if not self.request.user.is_authenticated or self.request.user.role != 'super_admin':
            queryset = queryset.filter(status='published')
        
        # Filtering by category
        category = self.request.query_params.get('category')
        if category:
            queryset = queryset.filter(category__iexact=category)
        
        # Search by title/content
        search = self.request.query_params.get('search')
        if search:
            queryset = queryset.filter(title__icontains=search) | queryset.filter(content__icontains=search)

        return queryset.distinct()

    def perform_create(self, serializer):
        # Members can only create drafts (FR-11, FR-12)
        serializer.save(author=self.request.user, status='draft')

    def update(self, request, *args, **kwargs):
        # Only super admins can change status to published (FR-12)
        if 'status' in request.data and request.data['status'] == 'published' and not IsSuperAdmin().has_permission(request, self):
            return Response({"detail": "Only Super Admins can publish posts."}, status=http_status.HTTP_403_FORBIDDEN)
        return super().update(request, *args, **kwargs)


class CommentViewSet(viewsets.ModelViewSet):
    serializer_class = CommentSerializer

    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            return [permissions.AllowAny()] # Allow public to see comments? SRS says members can comment.
        return [permissions.IsAuthenticated()]

    def get_queryset(self):
        return Comment.objects.filter(post_id=self.kwargs['post_pk'])

    def perform_create(self, serializer):
        serializer.save(post_id=self.kwargs['post_pk'], user=self.request.user)

