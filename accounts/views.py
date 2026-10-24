from rest_framework.response import Response
from rest_framework import generics
from rest_framework.permissions import AllowAny, IsAuthenticated

from .serializers import RegisterSerializer


class RegisterView(generics.CreateAPIView):
    serializer_class = RegisterSerializer
    permission_classes = [AllowAny]


class MyProfileView(generics.RetrieveAPIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user

        return Response({
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "role": user.role,
            "college": user.college.name if user.college else None,
            "college_id": user.college.id if user.college else None
        })