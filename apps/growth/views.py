from django.conf import settings
from rest_framework import viewsets, mixins, status
from rest_framework.views import APIView
from rest_framework.generics import get_object_or_404
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from .models import Checkin, Log
from .serializers import CheckinSerializer, LogSerializer
from apps.core.serializers import EmptySerializer
from apps.core.utils import get_today_start_end
from apps.profiles.models import PointsLog
from apps.users.models import User


class CheckinViewSet(mixins.CreateModelMixin, viewsets.GenericViewSet):
    """
    签到 post，一天签到一次
    """
    queryset = Checkin.objects.all()
    serializer_class = CheckinSerializer
    permission_classes = (IsAuthenticated, )

    def get_serializer_class(self):
        if self.action == 'create':
            return EmptySerializer
        else:
            return CheckinSerializer

    def create(self, request):
        today_start, today_end = get_today_start_end()
        exist_checkin = Checkin.objects.filter(user=request.user,
                                               created_at__lte=today_end,
                                               created_at__gte=today_start)
        if not exist_checkin:
            profile = request.user.user_profile
            from_points = profile.points
            to_points = from_points +10
            checkin = Checkin(user=request.user,
                              from_points=from_points,
                              to_points=to_points)
            checkin.save()
            profile.points = to_points
            profile.save()
            serializer = CheckinSerializer(checkin, many=False)
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response({'detail': '请勿重复签到。'},
                            status=status.HTTP_400_BAD_REQUEST)


class InviteJoinAPIView(APIView):
    """
    加入一个用户的邀请
    """
    permission_classes = (IsAuthenticated, )
    serializer_class = EmptySerializer

    def post(self, request, user_id):
        """
        加入一个用户的邀请
        /api/v1/growth/invite/{user_id}/join/
        user_id 加入 request.user 的邀请中
        """
        invite = request.user.user_invite
        from_user = invite.user
        from_user_profile = from_user.user_profile
        to_user = get_object_or_404(User.objects.all(), pk=str(user_id))
        to_user_profile = to_user.user_profile
        if str(from_user.id) != str(to_user.id) and invite.left > 0:
            exist_log = Log.objects.filter(invite=invite, to_user=to_user)
            if not exist_log:
                # save points to profile, log user points change and invite log
                from_user_from_points = from_user_profile.points
                from_user_to_points = from_user_from_points + 20
                to_user_from_points = to_user_profile.points
                to_user_to_points = to_user_from_points + 20

                from_user_profile.points = from_user_to_points
                from_user_profile.save()
                invite.left -= 1
                invite.save()

                to_user_profile.points = to_user_to_points
                to_user_profile.save()

                desc = '邀请用户获得积分'
                from_user_points_log = PointsLog(
                    user=from_user,
                    from_points=from_user_from_points,
                    to_points=from_user_to_points,
                    desc=desc)
                from_user_points_log.save()
                to_user_points_log = PointsLog(user=to_user,
                                               from_points=to_user_from_points,
                                               to_points=to_user_to_points,
                                               desc=desc)
                to_user_points_log.save()

                log = Log(invite=invite, to_user=to_user, desc=desc)
                log.save()
                serializer = LogSerializer(log,
                                           many=False)
                return Response(serializer.data, status=status.HTTP_200_OK)
            else:
                return Response({'detail': '已加入该用户的邀请，不能重复加入'},
                                status=status.HTTP_400_BAD_REQUEST)
        elif str(from_user.id) == str(to_user.id):
            return Response({'detail': '不能自己邀请自己'},
                            status=status.HTTP_400_BAD_REQUEST)
        elif invite.left == 0:
            return Response({'detail': '邀请次数已使用完'},
                            status=status.HTTP_400_BAD_REQUEST)


class InviteLogsAPIView(APIView):
    permission_classes = (IsAuthenticated, )
    serializer_class = EmptySerializer

    def get(self, request):
        """
        一个用户邀请下的所有人，倒序排列，不翻页
        """
        invite = request.user.user_invite
        invite_logs = invite.invite_logs.all()
        serializer = LogSerializer(invite_logs,
                                   many=True)
        return Response(
            {
                'count': invite_logs.count(),
                'results': serializer.data
            },
            status=status.HTTP_200_OK)
