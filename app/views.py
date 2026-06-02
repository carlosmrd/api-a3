from django.contrib.auth import authenticate
from django.db import transaction
from decimal import Decimal
from rest_framework import status, viewsets
from rest_framework.authtoken.models import Token
from rest_framework.permissions import IsAuthenticated, IsAdminUser, AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from app.models import Produto, Estoque, Endereco, CartaoCredito, ItemCarrinho, Carrinho, ItemPedido, Pedido
from app.serializers import (
    ProdutoSerializer, EstoqueSerializer,UsuarioSerializer, UsuarioDetalhesSerializer, EnderecoSerializer,
    CartaoCreditoSerializer, ItemCarrinhoSerializer, AtualizarItemCarrinhoSerializer, CarrinhoSerializer,
    PedidoSerializer, CriarPedidoSerializer
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

class CartaoCreditoViewSet(viewsets.ModelViewSet):
    serializer_class = CartaoCreditoSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return CartaoCredito.objects.filter(usuario=self.request.user)

    #Mesmo funcionamento do ViewSet de Endereço
    @transaction.atomic
    def perform_create(self, serializer):
        possui_cartao = CartaoCredito.objects.filter(usuario=self.request.user).exists()
        principal_enviado = serializer.validated_data.get('principal', False)
        principal_final = True if not possui_cartao else principal_enviado

        if principal_final:
            CartaoCredito.objects.filter(usuario=self.request.user).update(principal=False)

        serializer.save(usuario=self.request.user, principal=principal_final)

    @transaction.atomic
    def perform_update(self, serializer):
        principal_enviado = serializer.validated_data.get('principal', None)

        if principal_enviado is True:
            CartaoCredito.objects.filter(
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

#View do carrinho do usuário logado
class CarrinhoViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated]

    def list(self, request):
        #Cria um carrinho se ainda não existir um para o usuário. Exibe o já criado caso existente
        carrinho, _ = Carrinho.objects.get_or_create(usuario=request.user)
        serializer = CarrinhoSerializer(carrinho)
        return Response(serializer.data)

#View para manipulação dos ItemCarrinho
class ItemCarrinhoViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]

    #Restringe operações ao carrinho do usuário logado
    def get_queryset(self):
        #Verifica se o carrinho do usuário já existe. Cria carrinho se não existir
        carrinho, _ = Carrinho.objects.get_or_create(usuario=self.request.user)
        return ItemCarrinho.objects.filter(
            carrinho=carrinho
        ).select_related('estoque', 'estoque__produto')

    def get_serializer_class(self):
        if self.action in ['update', 'partial_update']:
            return AtualizarItemCarrinhoSerializer
        return ItemCarrinhoSerializer

    #Cria ItemCarrinho referente ao estoque
    def create(self, request, *args, **kwargs):
        carrinho, _ = Carrinho.objects.get_or_create(usuario=request.user)

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        estoque = serializer.validated_data['estoque']
        quantidade = serializer.validated_data['quantidade']

        #Verifica se o item já existe no carrinho
        item_existente = ItemCarrinho.objects.filter(
            carrinho=carrinho,
            estoque=estoque
        ).first()

        #Se item já estiver no carrinho, adiciona à quantidade e impede duplicidade
        if item_existente:
            nova_quantidade = item_existente.quantidade + quantidade

            #Verifica se quantidade em estoque existe antes de adicionar
            if nova_quantidade > estoque.quantidade:
                return Response(
                    {'erro': 'Quantidade total no carrinho maior que a disponível em estoque.'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            item_existente.quantidade = nova_quantidade
            item_existente.save()

            return Response(
                ItemCarrinhoSerializer(item_existente).data,
                status=status.HTTP_200_OK
            )

        #Adiciona item se não existir no carrinho
        item = ItemCarrinho.objects.create(
            carrinho=carrinho,
            estoque=estoque,
            quantidade=quantidade
        )

        return Response(
            ItemCarrinhoSerializer(item).data,
            status=status.HTTP_201_CREATED
        )

#Cria pedido usando o carrinho do usuário logado ao receber uma requisição post com o "endereco_id" do endereço
#de entrega
class PedidoViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    #Não permite PUT, PATCH, DELETE
    http_method_names = ['get', 'post', 'head', 'options']

    #Restringe operações aos pedidos do usuário logado
    def get_queryset(self):
        return Pedido.objects.filter(usuario=self.request.user).select_related(
            'endereco'
        ).prefetch_related(
            'itens__estoque__produto'
        )

    #Define qual serializer a operação vai usar
    def get_serializer_class(self):
        if self.action == 'create':
            return CriarPedidoSerializer
        return PedidoSerializer

    @transaction.atomic
    def create(self, request, *args, **kwargs):
        #Valida a requisição
        serializer = self.get_serializer(
            data=request.data,
            context={'request': request}
        )
        serializer.is_valid(raise_exception=True)

        #Busca o endereço recebido no banco
        endereco = Endereco.objects.get(
            id=serializer.validated_data['endereco_id'],
            usuario=request.user
        )

        #Busca o cartão de crédito recebido no banco
        cartao = CartaoCredito.objects.get(
            id=serializer.validated_data['cartao_id'],
            usuario=request.user
        )

        #Busca o carrinho do usuário logado e verifica se está vazio
        carrinho, _ = Carrinho.objects.get_or_create(usuario=request.user)
        itens_carrinho = ItemCarrinho.objects.filter(
            carrinho=carrinho
        ).select_related('estoque', 'estoque__produto')

        if not itens_carrinho.exists():
            return Response(
                {'erro': 'O carrinho está vazio.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        #Verifica se os itens do carrinho existem em estoque e soma os subtotais
        total = Decimal('0.00')

        for item in itens_carrinho:
            if item.quantidade > item.estoque.quantidade:
                return Response(
                    {
                        'erro': f'Estoque insuficiente para o produto {item.estoque.produto.nome}.'
                    },
                    status=status.HTTP_400_BAD_REQUEST
                )

            total += item.subtotal()

        #Cria objeto pedido
        pedido = Pedido.objects.create(
            usuario=request.user,
            endereco=endereco,
            cartao=cartao,
            total=total,
            #Define o pedido como pago já que não tem gateway de pagamento
            status='pago'
        )

        #Cria ItemPedido para cada ItemCarrinho e baixa a quantidade correspondente do estoque
        for item in itens_carrinho:
            ItemPedido.objects.create(
                pedido=pedido,
                estoque=item.estoque,
                quantidade=item.quantidade,
                preco_unitario=item.estoque.produto.preco
            )

            item.estoque.quantidade -= item.quantidade
            item.estoque.save()

        #Limpa o carrinho
        itens_carrinho.delete()

        return Response(
            PedidoSerializer(pedido).data,
            status=status.HTTP_201_CREATED
        )