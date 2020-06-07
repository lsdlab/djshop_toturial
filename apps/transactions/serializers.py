from rest_framework import serializers
from .models import Transaction, TransactionProduct, Invoice, Refund, Collect
from apps.profiles.serializers import AddressSerializer
from apps.products.serializers import ProductCartSerializer, ProductReviewSerializer
from apps.express.serializers import ExpressSerializer
from apps.stores.serializers import StoreSerializer
from apps.users.serializers import UserPublicInfoSerializer
from apps.coupons.serializers import CouponLogSerializer


class TransactionProductSerializer(serializers.ModelSerializer):
    product_spec = ProductCartSerializer(many=False, read_only=True)

    class Meta:
        model = TransactionProduct
        fields = ('id', 'transaction', 'product_spec', 'nums', 'price',
                  'created_at', 'updated_at')
        read_only_fields = ('id', 'created_at', 'updated_at')


class TransactionProductCreateSerialier(serializers.ModelSerializer):
    class Meta:
        model = TransactionProduct
        fields = ('id', 'transaction', 'product_spec', 'nums', 'price',
                  'created_at', 'updated_at')
        read_only_fields = ('id', 'created_at', 'updated_at')


class TransactionSerializer(serializers.ModelSerializer):
    user = UserPublicInfoSerializer(many=False, read_only=True)
    status = serializers.ChoiceField(Transaction.STATUS_CHOICE, read_only=True)
    status_name = serializers.SerializerMethodField()
    payment = serializers.ChoiceField(
        Transaction.PAYMENT_CHOICE, required=True)
    payment_name = serializers.SerializerMethodField()
    deal_type = serializers.ChoiceField(
        Transaction.DEAL_TYPE_CHOICE, required=True)
    deal_type_name = serializers.SerializerMethodField()
    express_type = serializers.ChoiceField(
        Transaction.EXPRESS_TYPE_CHOICE, required=True)
    express_type_name = serializers.SerializerMethodField()
    address = serializers.SerializerMethodField()
    product_specs_header_image = serializers.SerializerMethodField()

    class Meta:
        model = Transaction
        fields = ('id', 'name', 'user', 'sn', 'status', 'status_name',
                  'payment', 'payment_name', 'deal_type', 'deal_type_name',
                  'express_type', 'express_type_name', 'note', 'total_amount',
                  'expired_datetime', 'seller_packaged_datetime',
                  'received_datetime', 'payment_sn', 'payment_datetime', 'promotion',
                  'paid', 'closed_datetime', 'review_datetime', 'address', 'product_specs_header_image',
                  'seller_note', 'created_at', 'updated_at')

    def get_status_name(self, obj):
        return obj.get_status_display()

    def get_payment_name(self, obj):
        return obj.get_payment_display()

    def get_deal_type_name(self, obj):
        return obj.get_deal_type_display()

    def get_express_type_name(self, obj):
        return obj.get_express_type_display()

    def get_address(self, obj):
        return obj.address.name + '-' + obj.address.mobile + '-' + obj.address.address

    def get_product_specs_header_image(self, obj):
        result = []
        if obj.transaction_transaction_products.all():
            for i in obj.transaction_transaction_products.all():
                result.append(i.product_spec.header_image)
            return result
        else:
            return None


class TransactionCreateSerializer(serializers.ModelSerializer):
    payment = serializers.ChoiceField(
        Transaction.PAYMENT_CHOICE, required=True)
    deal_type = serializers.ChoiceField(
        Transaction.DEAL_TYPE_CHOICE, required=True)

    class Meta:
        model = Transaction
        fields = ('id', 'payment', 'deal_type', 'address', 'coupon_log',
                  'note', 'created_at', 'updated_at')
        read_only_fields = ('id', 'created_at', 'updated_at')


class TransactionPreCreateSerializer(serializers.ModelSerializer):
    payment = serializers.ChoiceField(
        Transaction.PAYMENT_CHOICE, required=True)
    deal_type = serializers.ChoiceField(
        Transaction.DEAL_TYPE_CHOICE, required=True)

    class Meta:
        model = Transaction
        fields = ('id', 'payment', 'deal_type', 'coupon_log',
                  'note', 'created_at', 'updated_at')
        read_only_fields = ('id', 'created_at', 'updated_at')

class TransactionBGSCreateSerializer(serializers.ModelSerializer):
    payment = serializers.ChoiceField(
        Transaction.PAYMENT_CHOICE, required=True)
    deal_type = serializers.ChoiceField(
        Transaction.DEAL_TYPE_CHOICE, required=True)

    class Meta:
        model = Transaction
        fields = ('id', 'payment', 'deal_type', 'address', 'note',
                  'created_at', 'updated_at')
        read_only_fields = ('id', 'created_at', 'updated_at')


class TransactionPatchSerializer(serializers.ModelSerializer):
    class Meta:
        model = Transaction
        fields = ('id', 'address', 'seller_note', 'paid', 'created_at',
                  'updated_at')
        read_only_fields = ('id', 'created_at', 'updated_at')


class CollectInTransactionSerializer(serializers.ModelSerializer):
    store = StoreSerializer(many=False, read_only=True)

    class Meta:
        model = Collect
        fields = ('id', 'store', 'name', 'mobile', 'pickup_datetime', 'note',
                  'picked', 'picked_datetime', 'created_at', 'updated_at')
        read_only_fields = ('id', 'created_at', 'updated_at')


class TransactionDetailSerializer(serializers.ModelSerializer):
    user = UserPublicInfoSerializer(many=False, read_only=True)
    status = serializers.ChoiceField(Transaction.STATUS_CHOICE)
    status_name = serializers.SerializerMethodField()
    payment = serializers.ChoiceField(Transaction.PAYMENT_CHOICE)
    payment_name = serializers.SerializerMethodField()
    deal_type = serializers.ChoiceField(Transaction.DEAL_TYPE_CHOICE)
    deal_type_name = serializers.SerializerMethodField()
    express_type = serializers.ChoiceField(Transaction.EXPRESS_TYPE_CHOICE)
    express_type_name = serializers.SerializerMethodField()
    address = AddressSerializer(many=False, read_only=True)
    products = TransactionProductSerializer(
        source='transaction_transaction_products', many=True, read_only=True)
    express = ExpressSerializer(
        source='transaction_express', many=False, read_only=True)
    collect = CollectInTransactionSerializer(
        source='transaction_collect', many=False, read_only=True)
    coupon_log = CouponLogSerializer(many=False, read_only=True)
    reviews = serializers.SerializerMethodField()
    refunded = serializers.SerializerMethodField()

    class Meta:
        model = Transaction
        fields = ('id', 'name', 'user', 'sn', 'status', 'status_name',
                  'payment', 'payment_name', 'deal_type', 'deal_type_name',
                  'express_type', 'express_type_name', 'note', 'total_amount',
                  'expired_datetime', 'seller_packaged_datetime',
                  'received_datetime', 'payment_sn', 'payment_datetime', 'promotion',
                  'paid', 'closed_datetime', 'review_datetime', 'address', 'coupon_log', 'reviews', 'refunded',
                  'seller_note', 'products', 'express', 'collect',
                  'created_at', 'updated_at')

    def get_status_name(self, obj):
        return obj.get_status_display()

    def get_payment_name(self, obj):
        return obj.get_payment_display()

    def get_deal_type_name(self, obj):
        return obj.get_deal_type_display()

    def get_express_type_name(self, obj):
        return obj.get_express_type_display()

    def get_reviews(self, obj):
        return ProductReviewSerializer(obj.transaction_reviews.all(), many=True).data

    def get_refunded(self, obj):
        if obj.transaction_refund:
            return True
        else:
            return False


class TransactionAddressSerializer(serializers.ModelSerializer):
    address = AddressSerializer(many=False, read_only=True)

    class Meta:
        model = Transaction
        fields = ('id', 'name', 'sn', 'address', 'created_at', 'updated_at')
        read_only_fields = ('id', 'created_at', 'updated_at')


class InvoiceSerializer(serializers.ModelSerializer):
    type = serializers.ChoiceField(Invoice.TYPE_CHOICE)
    type_name = serializers.SerializerMethodField()
    address = AddressSerializer(many=False, read_only=True)
    transaction_sn = serializers.SerializerMethodField()
    user_sn = serializers.SerializerMethodField()

    class Meta:
        model = Invoice
        fields = ('id', 'transaction', 'transaction_sn', 'user_sn', 'type',
                  'type_name', 'title', 'price', 'company_tax_sn', 'shipped',
                  'shipped_datetime', 'issued', 'issued_datetime', 'address',
                  'note', 'created_at', 'updated_at')

    def get_type_name(self, obj):
        return obj.get_type_display()

    def get_transaction_sn(self, obj):
        return obj.transaction.sn

    def get_user_sn(self, obj):
        return obj.transaction.user.id


class InvoiceCreateSerializer(serializers.ModelSerializer):
    type = serializers.ChoiceField(Invoice.TYPE_CHOICE, required=True)

    class Meta:
        model = Invoice
        fields = ('id', 'type', 'title', 'price', 'company_tax_sn', 'shipped',
                  'shipped_datetime', 'issued', 'issued_datetime', 'address',
                  'note', 'created_at', 'updated_at')
        read_only_fields = ('id', 'price', 'shipped', 'shipped_datetime',
                            'issued', 'issued_datetime', 'created_at',
                            'updated_at')


class InvoicePatchSerializer(serializers.ModelSerializer):
    type = serializers.ChoiceField(Invoice.TYPE_CHOICE)

    class Meta:
        model = Invoice
        fields = ('id', 'type', 'title', 'price', 'company_tax_sn', 'shipped',
                  'issued', 'address', 'note', 'created_at', 'updated_at')
        read_only_fields = ('id', 'created_at', 'updated_at')


class RefundSerializer(serializers.ModelSerializer):
    user = serializers.CharField(source='user.username', read_only=True)
    refund_type_name = serializers.SerializerMethodField()
    auditor = serializers.CharField(source='user.username', read_only=True)
    audit_name = serializers.SerializerMethodField()
    transaction_sn = serializers.SerializerMethodField()

    class Meta:
        model = Refund
        fields = ('id', 'user', 'transaction', 'transaction_sn', 'sn',
                  'refund_price', 'note', 'refund_type', 'refund_type_name',
                  'auditor', 'audit', 'audit_name', 'audit_datetime',
                  'audit_note', 'shipper', 'shipper_sn',
                  'refund_enter_ship_info_datetime', 'created_at',
                  'updated_at')
        read_only_fields = ('id', 'sn', 'refund_price', 'note', 'refund_type',
                            'audit', 'audit_name', 'audit_datetime',
                            'audit_note', 'shipper', 'shipper_sn',
                            'refund_enter_ship_info_datetime', 'created_at',
                            'updated_at')

    def get_refund_type_name(self, obj):
        return obj.get_refund_type_display()

    def get_audit_name(self, obj):
        return obj.get_audit_display()

    def get_transaction_sn(self, obj):
        return obj.transaction.sn


class RefundSuperuserPatchSerializer(serializers.ModelSerializer):
    audit = serializers.CharField(required=True)

    class Meta:
        model = Refund
        fields = ('id', 'refund_price', 'auditor', 'audit', 'audit_note')
        read_only_fields = ('id', )


class RefundNormaluserPatchSerializer(serializers.ModelSerializer):
    shipper = serializers.CharField(required=True)
    shipper_sn = serializers.CharField(required=True)

    class Meta:
        model = Refund
        fields = ('shipper', 'shipper_sn')


class RefundCreateSerializer(serializers.ModelSerializer):
    note = serializers.CharField(required=True)

    class Meta:
        model = Refund
        fields = (
            'id',
            'note',
        )
        read_only_fields = ('id', )


class CollectSerializer(serializers.ModelSerializer):
    store = StoreSerializer(many=False, read_only=True)
    transaction_sn = serializers.SerializerMethodField()

    class Meta:
        model = Collect
        fields = ('id', 'transaction', 'transaction_sn', 'store', 'name',
                  'mobile', 'pickup_datetime', 'note', 'picked',
                  'picked_datetime', 'created_at', 'updated_at')
        read_only_fields = ('id', 'created_at', 'updated_at')

    def get_transaction_sn(self, obj):
        return obj.transaction.sn


class CollectCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Collect
        fields = ('id', 'store', 'name', 'mobile', 'pickup_datetime', 'note',
                  'created_at', 'updated_at')
        read_only_fields = ('id', 'created_at', 'updated_at')
