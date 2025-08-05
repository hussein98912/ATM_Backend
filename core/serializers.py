from rest_framework import serializers
from .models import User, CardDetail, Transaction, TransferTransaction, DeliveryLocation, DeliverySchedule,Employee
from django.contrib.auth import get_user_model
from .models import Transaction, DeliveryLocation, DeliverySchedule


User = get_user_model()

class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['id', 'first_name', 'last_name','status','username', 'email', 'password', 'phone_number', 'birth_date', 'emirates_id', 'passport']

    def create(self, validated_data):
        password = validated_data.pop('password')
        user = User(**validated_data)
        user.set_password(password)  
        user.save()
        return user
    
class DeliveryLocationSerializer(serializers.ModelSerializer):
    class Meta:
        model = DeliveryLocation
        fields = ['is_current_location', 'building_type', 'latitude', 'longitude', 'address']


class DeliveryScheduleSerializer(serializers.ModelSerializer):
    class Meta:
        model = DeliverySchedule
        fields = ['delivery_type', 'scheduled_date', 'scheduled_time']

class CardDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = CardDetail
        fields = ['card_number', 'expiry', 'cvv', 'cardholder_name']
        extra_kwargs = {
            'user': {'read_only': True}
        }
    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)
    


class TransactionSerializer(serializers.ModelSerializer):
    delivery_locations = DeliveryLocationSerializer(many=True)
    delivery_schedules = DeliveryScheduleSerializer(many=True)
    card = CardDetailSerializer() 

    class Meta:
        model = Transaction
        fields = ['id', 'transaction_type', 'amount', 'status', 'currency_from', 'currency_to',
                  'delivery_locations', 'delivery_schedules', 'card']

    def create(self, validated_data):
        delivery_locations_data = validated_data.pop('delivery_locations')
        delivery_schedules_data = validated_data.pop('delivery_schedules')
        card_data = validated_data.pop('card')

        user = self.context['request'].user

        
        card = CardDetail.objects.create(user=user, **card_data)

       
        transaction = Transaction.objects.create(card=card, user=user, **validated_data)

        for location_data in delivery_locations_data:
            DeliveryLocation.objects.create(transaction=transaction, **location_data)

        for schedule_data in delivery_schedules_data:
            DeliverySchedule.objects.create(transaction=transaction, **schedule_data)

        return transaction


class TransferTransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = TransferTransaction
        fields = '__all__'
        read_only_fields = ['user']

    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)




class EmployeeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Employee
        fields = '__all__'



