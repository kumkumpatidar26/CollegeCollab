from rest_framework import generics
from rest_framework.permissions import AllowAny, IsAuthenticated

from .models import College
from .serializers import CollegeSerializer


class CollegeListCreateView(generics.ListCreateAPIView):
    queryset = College.objects.all()
    serializer_class = CollegeSerializer

    def get_permissions(self):
        if self.request.method == 'GET':
            return [AllowAny()]
        return [IsAuthenticated()]
