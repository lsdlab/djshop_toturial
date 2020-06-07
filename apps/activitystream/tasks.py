from datetime import datetime
from celery.decorators import task
from .models import ActivityStream
from apps.core.utils import get_today_start_end
from apps.users.models import User


@task(name="save_activitystream")
def save_activitystream(actor, actor_id, verb, object='', object_id=''):
    user_queryset = User.objects.filter(pk=actor_id)
    if user_queryset:
        user = user_queryset[0]
        if verb == '登录了后台':
            # 记录一天的第一次
            today_start, today_end = get_today_start_end()
            exist_activitystream = ActivityStream.objects.filter(
                actor_id=actor_id,
                created_at__lte=today_end,
                created_at__gte=today_start)
            if exist_activitystream:
                pass
            else:
                activity_stream = ActivityStream(actor=actor,
                                                 actor_id=actor_id,
                                                 verb=verb,
                                                 user=user)
                activity_stream.save()
        else:
            activity_stream = ActivityStream(actor=actor,
                                             actor_id=actor_id,
                                             verb=verb,
                                             object=object,
                                             object_id=object_id,
                                             user=user)
            activity_stream.save()
    return True
