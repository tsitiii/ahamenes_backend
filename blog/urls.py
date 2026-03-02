from rest_framework.routers import DefaultRouter
from rest_framework_nested import routers
from .views import BlogPostViewSet, CommentViewSet

router = DefaultRouter()

router.register(r'posts', BlogPostViewSet, basename='posts')


blog_router = routers.NestedDefaultRouter(router, r'posts', lookup='post')
blog_router.register(r'comments', CommentViewSet, basename='post-comments')

urlpatterns = router.urls + blog_router.urls