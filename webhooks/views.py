from webhooks.models import Webhook
from webhooks.serializers import WebhookSerializer
from webhooks.permissions import IsOwner
from rest_framework import generics, permissions


class WebhookList(generics.ListCreateAPIView):
    serializer_class = WebhookSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        if self.request.user.is_anonymous:
            # For unauthenticated users we want to return an empty queryset, otherwise we will get an exception
            return Webhook.objects.none()
        else: 
            # We want to return a queryset with objects owned by authenticated user
            return Webhook.objects.filter(owner=self.request.user)

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)


class WebhookDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Webhook.objects.all()
    serializer_class = WebhookSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwner]