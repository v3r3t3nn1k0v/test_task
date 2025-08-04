from rest_framework import serializers


class GetHeroSerializer(serializers.Serializer):
    name = serializers.CharField()

class FilterSerializer(serializers.Serializer):
    FILTER_TYPE_CHOICES = [
        ('exact'),
        ('less'),
        ('more'),
    ]
    
    PROPERTY_CHOICES = [
        ('strength'),
        ('intelligence'),
        ('speed'),
        ('power')

    ]
    
    filter_type = serializers.ChoiceField(choices=FILTER_TYPE_CHOICES)
    property = serializers.ChoiceField(choices=PROPERTY_CHOICES)
    value = serializers.IntegerField()

class PostHeroSerializer(serializers.Serializer):
    name = serializers.CharField(required=True, max_length=100)
    filters = serializers.ListField(
        child=FilterSerializer(),
        required=False,
        default=[]
    )