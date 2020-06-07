from rest_framework import serializers
from .models import Checkin, Invite, Log
from apps.users.serializers import UserPublicInfoSerializer


class CheckinSerializer(serializers.ModelSerializer):
    class Meta:
        model = Checkin
        fields = ('id', 'user', 'from_points', 'to_points', 'created_at',
                  'updated_at')
        read_only_fields = ('id', 'created_at', 'updated_at')


class InviteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Invite
        fields = ('id', 'user', 'shortuuid', 'created_at', 'updated_at')
        read_only_fields = ('id', 'created_at', 'updated_at')


class LogSerializer(serializers.ModelSerializer):
    to_user = UserPublicInfoSerializer(many=False, read_only=True)

    class Meta:
        model = Log
        fields = ('id', 'invite', 'to_user', 'desc', 'created_at',
                  'updated_at')
        read_only_fields = ('id', 'created_at', 'updated_at')
