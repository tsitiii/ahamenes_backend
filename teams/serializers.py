from rest_framework import serializers
from .models import Team, MembershipApplication, Project, Achievement, Event, EventRegistration


class TeamSerializer(serializers.ModelSerializer):
    logo = serializers.ImageField(required=False, allow_null=True)

    class Meta:
        model = Team
        fields = '__all__'
        read_only_fields = ('id', 'created_at', 'updated_at')

class MembershipApplicationSerializer(serializers.ModelSerializer):

    class Meta:
        model = MembershipApplication
        fields = '__all__'
        read_only_fields = ('id', 'status', 'reviewed_at', 'reviewed_by', 'created_at')

class ProjectSerializer(serializers.ModelSerializer):

    class Meta:
        model = Project
        fields = '__all__'
        read_only_fields = ('id', 'created_by','team', 'created_at', 'updated_at')

class AchievementSerializer(serializers.ModelSerializer):

    class Meta:
        model = Achievement
        fields = '__all__'
        read_only_fields = ('id', 'team', 'created_by', 'created_at')


class EventSerializer(serializers.ModelSerializer):
    class Meta:
        model = Event
        fields = "__all__"
        read_only_fields = ('id','created_by', 'created_at', 'updated_at')


class EventRegistrationSerializer(serializers.ModelSerializer):
    class Meta:
        model = EventRegistration
        fields = "__all__"
        read_only_fields = ('id', 'event', 'created_at')

