from django.db import models


class TimestampedModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True
        ordering = ['-created_at', '-updated_at']


class SoftDeleteModel(models.Model):
    deleted = models.BooleanField(default=False)

    class Meta:
        abstract = True

    def delete(self, using=None, soft=True, *args, **kwargs):
        """
        Soft delete object (set its ``deleted`` field to True).
        Actually delete object if setting ``soft`` to False.
        """
        if soft:
            self.deleted = True
            self.save(using=using)
        else:
            return super().delete(using=using, *args, **kwargs)
