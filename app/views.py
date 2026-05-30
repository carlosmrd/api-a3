from django.contrib.auth import authenticate
from django.db import transaction
from rest_framework import status, viewsets
from rest_framework.authtoken.models import Token
from rest_framework.permissions import IsAuthenticated, IsAdminUser, AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from app.models import Produto, Estoque, Endereco
from app.serializers import (
    ProdutoSerializer, EstoqueSerializer,
    UsuarioSerializer, UsuarioDetalhesSerializer,
    EnderecoSerializer
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

#Cadastro de endereço
class EnderecoViewSet(viewsets.ModelViewSet):
    serializer_class = EnderecoSerializer
    permission_classes = [IsAuthenticated]

    #Só retorna endereços do usuário que fez a requisição
    def get_queryset(self):
        return Endereco.objects.filter(usuario=self.request.user)

    #Transaction atomic só salva alterações no banco se tudo for executado com sucesso
    #Caso o campo "principal" de um endereço seja marcado como true perform_create e perform_update alteram o mesmo
    #campo nos outros endereços do usuário para false
    #principal_enviado e principal_final servem para definir todos os endereços principais para false antes de uma
    #atualização, caso contrário o unique constraint lança erro
    @transaction.atomic
    def perform_create(self, serializer):
        possui_endereco = Endereco.objects.filter(usuario=self.request.user).exists()
        principal_enviado = serializer.validated_data.get('principal', False)
        principal_final = True if not possui_endereco else principal_enviado

        if principal_final:
            Endereco.objects.filter(usuario=self.request.user).update(principal=False)

        serializer.save(usuario=self.request.user, principal=principal_final)

    @transaction.atomic
    def perform_update(self, serializer):
        principal_enviado = serializer.validated_data.get('principal', None)

        if principal_enviado is True:
            Endereco.objects.filter(
                usuario=self.request.user
            ).exclude(id=self.get_object().id).update(principal=False)

        serializer.save()

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