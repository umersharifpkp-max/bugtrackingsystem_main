from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from PIL import Image


def validate_png_gif(file):
    # First check mimetype if provided by client
    valid_mimetypes = {"image/png", "image/gif"}
    content_type = getattr(file, 'content_type', None)
    if content_type and content_type not in valid_mimetypes:
        raise ValidationError("Only .png and .gif files are allowed.")
    # Then verify using Pillow by attempting to open and check format
    try:
        image = Image.open(file)
        if image.format not in {"PNG", "GIF"}:
            raise ValidationError("Only .png and .gif files are allowed.")
    except Exception as exc:
        raise ValidationError("Invalid image file.") from exc


class Project(models.Model):
    name = models.CharField(max_length=255, unique=True)
    description = models.TextField(blank=True)
    manager = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="managed_projects")
    qas = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name="qa_projects", blank=True)
    developers = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name="dev_projects", blank=True)

    def __str__(self) -> str:
        return self.name


class Bug(models.Model):
    class BugType(models.TextChoices):
        FEATURE = 'feature', 'Feature'
        BUG = 'bug', 'Bug'

    class FeatureStatus(models.TextChoices):
        NEW = 'new', 'New'
        STARTED = 'started', 'Started'
        COMPLETED = 'completed', 'Completed'

    class BugStatus(models.TextChoices):
        NEW = 'new', 'New'
        STARTED = 'started', 'Started'
        RESOLVED = 'resolved', 'Resolved'

    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name="bugs")
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    deadline = models.DateField(null=True, blank=True)
    screenshot = models.ImageField(upload_to="screenshots/", validators=[validate_png_gif], blank=True, null=True)
    type = models.CharField(max_length=20, choices=BugType.choices)
    status = models.CharField(max_length=20)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="created_bugs")
    assigned_to = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, related_name="assigned_bugs", null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["project", "title"], name="unique_title_per_project"),
        ]

    def clean(self):
        # Validate status based on type
        if self.type == self.BugType.FEATURE:
            valid = {self.FeatureStatus.NEW, self.FeatureStatus.STARTED, self.FeatureStatus.COMPLETED}
        elif self.type == self.BugType.BUG:
            valid = {self.BugStatus.NEW, self.BugStatus.STARTED, self.BugStatus.RESOLVED}
        else:
            valid = set()
        if self.status not in {v.value for v in valid}:
            raise ValidationError("Invalid status for type")

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    def __str__(self) -> str:
        return f"{self.title} ({self.type})"
