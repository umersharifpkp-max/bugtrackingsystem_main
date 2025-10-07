from rest_framework import serializers
from .models import Project, Bug


class ProjectSerializer(serializers.ModelSerializer):
    qas = serializers.PrimaryKeyRelatedField(many=True, read_only=True)
    developers = serializers.PrimaryKeyRelatedField(many=True, read_only=True)

    class Meta:
        model = Project
        fields = ("id", "name", "description", "manager", "qas", "developers")


class BugSerializer(serializers.ModelSerializer):
    class Meta:
        model = Bug
        fields = (
            "id",
            "project",
            "title",
            "description",
            "deadline",
            "screenshot",
            "type",
            "status",
            "created_by",
            "assigned_to",
            "created_at",
            "updated_at",
        )
        read_only_fields = ("created_by", "created_at", "updated_at")
