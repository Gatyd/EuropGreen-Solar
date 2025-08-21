from rest_framework import viewsets, permissions
from rest_framework.response import Response
from rest_framework.decorators import action
from .models import Form
from .serializers import FormSerializer


class FormViewSet(viewsets.ModelViewSet):
	queryset = Form.objects.select_related('offer', 'created_by').all()
	serializer_class = FormSerializer
	permission_classes = [permissions.IsAuthenticated]

	def perform_create(self, serializer):
		serializer.save(created_by=self.request.user)
