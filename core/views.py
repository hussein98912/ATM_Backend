from rest_framework import viewsets
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status,permissions
from rest_framework.decorators import action
from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken
from .models import User, CardDetail, Transaction, DeliveryLocation, DeliverySchedule,DigitalSignature
from .serializers import *
from rest_framework.permissions import IsAdminUser
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404

class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAdminUser]  

    @action(detail=True, methods=['post'])
    def change_status(self, request, pk=None):
        user = self.get_object()
        status = request.data.get('status')
        if status in ['pending', 'verified', 'blocked']:
            user.status = status
            user.save()
            return Response({'status': f'Updated to {status}'})
        return Response({'error': 'Invalid status'}, status=400)
    

class LoginView(APIView):
    def post(self, request):
        email = request.data.get("email")
        password = request.data.get("password")

        user = authenticate(email=email, password=password)
        if user:
            refresh = RefreshToken.for_user(user)
            return Response({
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            })
        return Response({"detail": "Invalid credentials"}, status=status.HTTP_401_UNAUTHORIZED)

class CardDetailViewSet(viewsets.ModelViewSet):
    queryset = CardDetail.objects.all()
    serializer_class = CardDetailSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        # عشان المستخدم يشوف فقط كروته
        return self.queryset.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

class TransactionViewSet(viewsets.ModelViewSet):
    queryset = Transaction.objects.all()
    serializer_class = TransactionSerializer

    @action(detail=False, methods=['post'])
    def start(self, request):
        
        data = request.data.copy()
        data['user'] = request.user.id  
        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        serializer.save(user=request.user)  

        return Response(serializer.data, status=status.HTTP_201_CREATED)

        serializer = self.get_serializer(transaction)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

class TransferTransactionViewSet(viewsets.ModelViewSet):
    queryset = TransferTransaction.objects.all()
    serializer_class = TransferTransactionSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return self.queryset.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

class DeliveryLocationViewSet(viewsets.ModelViewSet):
    queryset = DeliveryLocation.objects.all()
    serializer_class = DeliveryLocationSerializer
    permission_classes = [IsAuthenticated]

class DeliveryScheduleViewSet(viewsets.ModelViewSet):
    queryset = DeliverySchedule.objects.all()
    serializer_class = DeliveryScheduleSerializer

class EmployeeCreateView(APIView):
    permission_classes = [permissions.IsAdminUser]

    def post(self, request):
        serializer = EmployeeSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({'message': 'Employee added successfully', 'data': serializer.data}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class EmployeeUpdateView(APIView):
    permission_classes = [permissions.IsAdminUser]

    def put(self, request, pk):
        employee = get_object_or_404(Employee, pk=pk)
        serializer = EmployeeSerializer(employee, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({'message': 'Employee updated successfully', 'data': serializer.data})
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
class EmployeeListView(APIView):
    permission_classes = [permissions.IsAdminUser]

    def get(self, request):
        employees = Employee.objects.all()
        serializer = EmployeeSerializer(employees, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
class EmployeeDeleteView(APIView):
    permission_classes = [permissions.IsAdminUser]

    def delete(self, request, pk):
        employee = get_object_or_404(Employee, pk=pk)
        employee.delete()
        return Response({'message': 'Employee deleted successfully'}, status=status.HTTP_204_NO_CONTENT)
    

class PaymentView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        user = request.user
        data = request.data

        # Save card if requested
        if data.get("save_card"):
            card = CardDetail.objects.create(
                user=user,
                card_number=data["card_number"],
                expiry=data["expiry"],
                cvv=data["cvv"],
                cardholder_name=data["cardholder_name"]
            )
        else:
            card = None

        # Create transaction
        transaction = Transaction.objects.create(
            user=user,
            card=card,
            transaction_type="deposit",
            amount=data["amount"],
            status="pending",
            currency_from=data["currency_from"],
            currency_to=data["currency_to"]
        )

        return Response({"message": "Payment initiated", "transaction_id": transaction.id}, status=201)
    

class FaceIDVerificationView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        user = request.user
        face_scan = request.data.get("face_scan")
        emirates_id = request.data.get("emirates_id")

        if not face_scan or not emirates_id:
            return Response({"error": "Missing face scan or Emirates ID"}, status=400)

       
        user.face_scan = face_scan
        user.emirates_id = emirates_id
        user.status = 'verified'
        user.save()

        return Response({"message": "Face & Emirates ID verified successfully"}, status=200)
    
class SignatureView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        user = request.user
        signature_data = request.data.get("signature_data")

        if not signature_data:
            return Response({"error": "No signature data provided"}, status=400)

        DigitalSignature.objects.update_or_create(
            user=user,
            defaults={"signature_data": signature_data}
        )

        return Response({"message": "Digital signature saved"}, status=200)

