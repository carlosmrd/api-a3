from django.contrib.auth import authenticate
from rest_framework import status, viewsets
from rest_framework.authtoken.models import Token
from rest_framework.permissions import IsAuthenticated, IsAdminUser, AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from app.models import Produto, Estoque
from app.serializers import (
    ProdutoSerializer, EstoqueSerializer,
    UsuarioSerializer, UsuarioDetalhesSerializer
)


#Cadastro de Usuário - POST /api/auth/registro/
class RegistroView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = UsuarioSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(
                {"mensagem": "Usuário criado com sucesso!"},
                status=status.HTTP_201_CREATED
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

#Login - POST /api/auth/login/
class LoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        email = request.data.get('email')
        password = request.data.get('password')

        usuario = authenticate(request, username=email, password=password)

        if usuario is None:
            return Response(
                {"erro": "Credenciais inválidas."},
                status=status.HTTP_401_UNAUTHORIZED
            )

        #Cria ou busca o token do usuário
        token, _ = Token.objects.get_or_create(user=usuario)
        return Response({"token": token.key})

#Logout - POST /api/auth/logout/
class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        #Deleta o token
        Token.objects.filter(user=request.user).delete()
        return Response({"mensagem": "Logout realizado com sucesso."})

#Perfil - GET /api/auth/perfil/
class PerfilView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        serializer = UsuarioDetalhesSerializer(request.user)
        return Response(serializer.data)

# lucas - viewset para o CRUD completo de produtos
class ProdutoViewSet(viewsets.ModelViewSet):
    queryset = Produto.objects.all()
    serializer_class = ProdutoSerializer

    def get_permissions(self):
        #Somente leitura para usuário comum
        if self.action in ['list', 'retrieve']:
            return [AllowAny()]
        #Permissão de escrita para funcionário
        return [IsAdminUser()]

# lucas - viewset para controlar as quantidades e tamanhos no estoque
class EstoqueViewSet(viewsets.ModelViewSet):
    queryset = Estoque.objects.all()
    serializer_class = EstoqueSerializer

    def get_permissions(self):
        #Somente leitura para usuário comum
        if self.action in ['list', 'retrieve']:
            return [AllowAny()]
        #Permissão de escrita para funcionário
        return [IsAdminUser()]