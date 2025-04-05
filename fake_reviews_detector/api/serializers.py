from rest_framework import serializers

class ParserTriggerSerializer(serializers.Serializer):
    url = serializers.URLField(required=True)
