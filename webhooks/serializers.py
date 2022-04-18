from rest_framework_json_api import serializers
from webhooks.models import Webhook


class WebhookSerializer(serializers.ModelSerializer):
    owner = serializers.ReadOnlyField(source='owner.username')

    class Meta:
        model = Webhook
        fields = ['id', 'url', 'owner', 'comment']