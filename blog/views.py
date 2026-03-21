from rest_framework import viewsets, permissions
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiTypes
from .models import BlogPost, Comment
from .serializers import BlogPostSerializer, CommentSerializer


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
    permission_classes = [permissions.IsAuthenticated]
    parser_classes = (MultiPartParser, FormParser, JSONParser)

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)


class CommentViewSet(viewsets.ModelViewSet):
    serializer_class = CommentSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Comment.objects.filter(post_id=self.kwargs['post_pk'])

    def perform_create(self, serializer):
        serializer.save(post_id=self.kwargs['post_pk'], user=self.request.user)

