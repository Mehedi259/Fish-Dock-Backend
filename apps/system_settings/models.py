from django.db import models
from core.models import TimeStampedModel

class SystemSetting(TimeStampedModel):
    key = models.CharField(max_length=80, unique=True, db_index=True)
    value = models.TextField()
    description = models.CharField(max_length=255, blank=True, null=True)
    is_public = models.BooleanField(
        default=True,
        help_text="If True, accessible by public website frontend"
    )

    class Meta:
        ordering = ['key']

    def __str__(self):
        return f"{self.key} = {self.value}"

    @classmethod
    def get_val(cls, key, default=""):
        setting = cls.objects.filter(key=key).first()
        return setting.value if setting else default
