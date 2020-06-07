import os
from django.db import models
from django.conf import settings
from apps.core.models import TimestampedModel
import shortuuid


class Checkin(TimestampedModel):
    user = models.ForeignKey(settings.AUTH_USER_MODEL,
                             on_delete=models.CASCADE,
                             related_name='user_checkins',
                             blank=False,
                             help_text='用户')
    from_points = models.IntegerField(blank=False, help_text='变更前积分')
    to_points = models.IntegerField(blank=False, help_text='变更后积分')

    def __str__(self):
        return str(self.id)

    class Meta:
        ordering = ['-created_at', '-updated_at']
        verbose_name = '签到日志'
        verbose_name_plural = verbose_name


class Invite(TimestampedModel):
    user = models.OneToOneField(settings.AUTH_USER_MODEL,
                                on_delete=models.CASCADE,
                                related_name='user_invite',
                                blank=False,
                                help_text='用户')
    left = models.IntegerField(default=10, help_text='剩余邀请次数')
    shortuuid = models.CharField(max_length=255, blank=False, help_text='UUID')

    def __str__(self):
        return str(self.id)

    def save(self, *args, **kwargs):
        if not self.shortuuid:
            self.shortuuid = shortuuid.uuid().upper()
        super().save(*args, **kwargs)

    class Meta:
        ordering = ['-created_at', '-updated_at']
        verbose_name = '邀请'
        verbose_name_plural = verbose_name


class Log(TimestampedModel):
    invite = models.ForeignKey('Invite',
                               on_delete=models.CASCADE,
                               related_name='invite_logs',
                               blank=False,
                               help_text='邀请')
    to_user = models.ForeignKey(settings.AUTH_USER_MODEL,
                                on_delete=models.CASCADE,
                                related_name='to_user_logs',
                                blank=False,
                                help_text='被邀请用户')
    desc = models.CharField(max_length=255, default='', help_text='描述')

    def __str__(self):
        return self.desc

    class Meta:
        ordering = ['-created_at', '-updated_at']
        verbose_name = '邀请日志'
        verbose_name_plural = verbose_name
