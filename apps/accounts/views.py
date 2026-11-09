from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.views import TokenObtainPairView
from django.contrib.auth import get_user_model
from .serializers import CustomTokenObtainPairSerializer, UserSerializer
from .permissions import IsAdminOrStaff, IsSuperAdmin
from core.utils import api_response

User = get_user_model()

class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer

class CurrentUserProfileView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        serializer = UserSerializer(request.user)
        return api_response(success=True, data=serializer.data)

    def patch(self, request):
        serializer = UserSerializer(request.user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return api_response(success=True, message="Profile updated successfully", data=serializer.data)
        return api_response(success=False, message="Validation error", errors=serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class UserListView(generics.ListCreateAPIView):
    permission_classes = [IsAdminOrStaff]
    queryset = User.objects.all().order_by('-date_joined')
    serializer_class = UserSerializer

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        role = request.query_params.get('role')
        if role:
            queryset = queryset.filter(role=role)
        search = request.query_params.get('search')
        if search:
            queryset = queryset.filter(username__icontains=search) | queryset.filter(phone__icontains=search) | queryset.filter(email__icontains=search)
        serializer = self.get_serializer(queryset, many=True)
        return api_response(success=True, data=serializer.data)

class UserDetailView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [IsSuperAdmin]
    queryset = User.objects.all()
    serializer_class = UserSerializer
