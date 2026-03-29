from rest_framework import status, views, viewsets
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.decorators import action
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenRefreshView
from drf_spectacular.utils import extend_schema, OpenApiResponse
from .models import CustomUser
from .serializers import (
    UserSerializer, LoginSerializer, 
    ActivationSerializer, UserUpdateSerializer
)
from .permissions import IsSuperAdmin

class LoginView(views.APIView):
    permission_classes = [AllowAny]

    @extend_schema(
        request=LoginSerializer,
        responses={
            200: OpenApiResponse(description="Login successful"),
            401: OpenApiResponse(description="Invalid credentials")
        },
        description="Authenticate a user and return JWT tokens."
    )
    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.validated_data
            refresh = RefreshToken.for_user(user)
            return Response({
                "success": True,
                "data": {
                    "access_token": str(refresh.access_token),
                    "refresh_token": str(refresh),
                    "user": UserSerializer(user).data
                },
                "message": "Login successful"
            }, status=status.HTTP_200_OK)
        return Response({
            "success": False,
            "error": "Invalid credentials"
        }, status=status.HTTP_401_UNAUTHORIZED)

class CustomTokenRefreshView(TokenRefreshView):
    @extend_schema(
        responses={
            200: OpenApiResponse(description="Token refreshed successfully"),
        },
        description="Refresh JWT access token."
    )
    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)
        if response.status_code == 200:
            return Response({
                "success": True,
                "data": response.data,
                "message": "Token refreshed successfully"
            }) 
        return response

class ActivationView(views.APIView):
    permission_classes = [AllowAny]

    @extend_schema(
        request=ActivationSerializer,
        responses={
            200: OpenApiResponse(description="Account activated successfully"),
            400: OpenApiResponse(description="Invalid token/data")
        },
        description="Activate an account and set password."
    )
    def post(self, request):
        serializer = ActivationSerializer(data=request.data)
        if serializer.is_valid():
            # Mock activation logic: Find user by token (here we assume token is email for simplicity)
            # In production, use a secure token generator.
            token = serializer.validated_data.get('token')
            password = serializer.validated_data.get('password')
            try:
                user = CustomUser.objects.get(email=token)
                user.set_password(password)
                user.is_active = True
                user.save()
                return Response({
                    "success": True,
                    "message": "Account activated successfully"
                }, status=status.HTTP_200_OK)
            except CustomUser.DoesNotExist:
                return Response({
                    "success": False,
                    "error": "Invalid activation token"
                }, status=status.HTTP_400_BAD_REQUEST)
        return Response({
            "success": False,
            "error": serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)

class UserViewSet(viewsets.ModelViewSet):
    queryset = CustomUser.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsSuperAdmin]

    def get_permissions(self):
        if self.action == 'me':
            return [IsAuthenticated()]
        return super().get_permissions()

    @action(detail=False, methods=['get'])
    def me(self, request):
        serializer = self.get_serializer(request.user)
        return Response({
            "success": True,
            "data": serializer.data
        })

    def get_queryset(self):
        queryset = CustomUser.objects.all()
        role = self.request.query_params.get('role')
        team = self.request.query_params.get('team')

        if role:
            queryset = queryset.filter(role=role)
        if team:
            queryset = queryset.filter(team_id=team)
        
        return queryset

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response({
            "success": True,
            "data": serializer.data
        })

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return Response({
            "success": True,
            "data": serializer.data
        })

    def partial_update(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = UserUpdateSerializer(instance, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({
                "success": True,
                "data": UserSerializer(instance).data,
                "message": "User updated successfully"
            })
        return Response({
            "success": False,
            "error": serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.is_active = False
        instance.save()
        return Response({
            "success": True,
            "message": "User deactivated successfully"
        }, status=status.HTTP_200_OK)

