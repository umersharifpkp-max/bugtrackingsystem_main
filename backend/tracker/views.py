from django.db.models import Q
from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response

from .models import Project, Bug
from .serializers import ProjectSerializer, BugSerializer
from .permissions import IsManager, IsQA, IsDeveloper


class ProjectViewSet(viewsets.ModelViewSet):
    serializer_class = ProjectSerializer
    queryset = Project.objects.all()

    def get_permissions(self):
        if self.action in {"list", "retrieve"}:
            return [permissions.IsAuthenticated()]
        return [IsManager()]

    def get_queryset(self):
        user = self.request.user
        if getattr(user, 'user_type', None) == 'manager':
            return Project.objects.filter(manager=user)
        if getattr(user, 'user_type', None) == 'qa':
            return Project.objects.filter(Q(qas=user) | Q(manager=user)).distinct()
        if getattr(user, 'user_type', None) == 'developer':
            return Project.objects.filter(Q(developers=user) | Q(manager=user)).distinct()
        return Project.objects.none()

    @action(detail=True, methods=["post"], permission_classes=[IsManager])
    def assign(self, request, pk=None):
        project = self.get_object()
        qa_ids = request.data.get("qas", [])
        dev_ids = request.data.get("developers", [])
        if qa_ids:
            project.qas.set(qa_ids)
        if dev_ids:
            project.developers.set(dev_ids)
        project.save()
        return Response(ProjectSerializer(project).data)


class BugViewSet(viewsets.ModelViewSet):
    serializer_class = BugSerializer
    queryset = Bug.objects.select_related("project").all()

    def get_permissions(self):
        if self.action in {"list", "retrieve"}:
            return [permissions.IsAuthenticated()]
        if self.action in {"create"}:
            # QA can create bugs in assigned projects; Managers can create; Developers no
            return [permissions.IsAuthenticated()]
        if self.action in {"update", "partial_update", "destroy", "set_status"}:
            return [permissions.IsAuthenticated()]
        return [permissions.IsAuthenticated()]

    def get_queryset(self):
        user = self.request.user
        if getattr(user, 'user_type', None) == 'manager':
            return Bug.objects.filter(project__manager=user)
        if getattr(user, 'user_type', None) == 'qa':
            return Bug.objects.filter(project__qas=user)
        if getattr(user, 'user_type', None) == 'developer':
            return Bug.objects.filter(Q(assigned_to=user) | Q(project__developers=user)).distinct()
        return Bug.objects.none()

    def perform_create(self, serializer):
        user = self.request.user
        project = serializer.validated_data.get("project")
        if getattr(user, 'user_type', None) == 'qa' and not project.qas.filter(id=user.id).exists():
            raise permissions.PermissionDenied("QA can only create in assigned projects")
        if getattr(user, 'user_type', None) == 'developer':
            raise permissions.PermissionDenied("Developers cannot create bugs")
        if getattr(user, 'user_type', None) == 'manager' and project.manager_id != user.id:
            raise permissions.PermissionDenied("Managers can only create in managed projects")
        serializer.save(created_by=user)

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        user = request.user
        if getattr(user, 'user_type', None) == 'developer':
            return Response({"detail": "Use set_status action"}, status=status.HTTP_400_BAD_REQUEST)
        if getattr(user, 'user_type', None) == 'qa':
            if not instance.project.qas.filter(id=user.id).exists():
                return Response({"detail": "Forbidden"}, status=status.HTTP_403_FORBIDDEN)
        if getattr(user, 'user_type', None) == 'manager':
            if instance.project.manager_id != user.id:
                return Response({"detail": "Forbidden"}, status=status.HTTP_403_FORBIDDEN)
        return super().update(request, *args, **kwargs)

    def partial_update(self, request, *args, **kwargs):
        kwargs['partial'] = True
        return self.update(request, *args, **kwargs)

    @action(detail=True, methods=["post"], permission_classes=[permissions.IsAuthenticated])
    def set_status(self, request, pk=None):
        bug = self.get_object()
        user = request.user
        new_status = request.data.get("status")
        if getattr(user, 'user_type', None) == 'developer':
            if bug.assigned_to_id != user.id:
                return Response({"detail": "Only assignee can update status"}, status=status.HTTP_403_FORBIDDEN)
            bug.status = new_status
            bug.save()
            return Response(BugSerializer(bug).data)
        if getattr(user, 'user_type', None) == 'qa':
            if not bug.project.qas.filter(id=user.id).exists():
                return Response({"detail": "Forbidden"}, status=status.HTTP_403_FORBIDDEN)
            bug.status = new_status
            bug.save()
            return Response(BugSerializer(bug).data)
        if getattr(user, 'user_type', None) == 'manager':
            if bug.project.manager_id != user.id:
                return Response({"detail": "Forbidden"}, status=status.HTTP_403_FORBIDDEN)
            bug.status = new_status
            bug.save()
            return Response(BugSerializer(bug).data)
        return Response({"detail": "Forbidden"}, status=status.HTTP_403_FORBIDDEN)
