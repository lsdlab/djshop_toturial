from rest_framework import serializers
from .models import Feedback
from apps.profiles.serializers import ProductCartSerializer
from apps.users.serializers import UserSerializer
from apps.transactions.serializers import TransactionProductSerializer


class FeedbackSerializer(serializers.ModelSerializer):
    user = UserSerializer(many=False, read_only=True)
    type = serializers.CharField(read_only=True)
    type_name = serializers.SerializerMethodField()
    product_spec = ProductCartSerializer(many=False, read_only=True)
    transaction_product = TransactionProductSerializer(many=False,
                                                       read_only=True)
    content = serializers.CharField(read_only=True)
    solved = serializers.BooleanField(required=True)

    class Meta:
        model = Feedback
        fields = ('id', 'user', 'type', 'type_name', 'product_spec',
                  'transaction_product', 'content', 'solved', 'created_at',
                  'updated_at')
        read_only_fields = ('id', 'type_name', 'created_at', 'updated_at')

    def get_type_name(self, obj):
        return obj.get_type_display()


class FeedbackCreateSerializer(serializers.ModelSerializer):
    type = serializers.ChoiceField(choices=Feedback.TYPE_CHOICE, required=True)
    content = serializers.CharField(required=True)

    class Meta:
        model = Feedback
        fields = ('id', 'type', 'product_spec', 'transaction_product',
                  'content', 'created_at', 'updated_at')
        read_only_fields = ('id', 'created_at', 'updated_at')
