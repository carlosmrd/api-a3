from rest_framework import serializers
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError as DjangoValidationError
from app.models import Produto, Estoque, Usuario, Endereco, Carrinho, ItemCarrinho

#Cadastro de usuário
class UsuarioSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8)

    class Meta:
        model = Usuario
        fields = ['id', 'email', 'password', 'nome', 'telefone', 'cpf', 'data_nascimento']
        read_only_fields = ['id']

    #Valida se a senha respeita os parâmetros definidos no settings.py
    def validate_password(self, value):
        try:
            validate_password(value)
        except DjangoValidationError as e:
            raise serializers.ValidationError(e.messages)
        return value

    def create(self, validated_data):
        password = validated_data.pop('password')
        usuario = Usuario(**validated_data)
        usuario.set_password(password)
        usuario.save()
        return usuario

#Leitura dos dados de usuário logado
class UsuarioDetalhesSerializer(serializers.ModelSerializer):
    class Meta:
        model = Usuario
        #Não exibe senha
        fields = ['id', 'email', 'nome', 'telefone', 'cpf', 'data_nascimento']

#Cadastro de endereço para o usuário logado
class EnderecoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Endereco
        fields = [
            'id',
            'usuario',
            'logradouro',
            'numero',
            'complemento',
            'bairro',
            'cidade',
            'estado',
            'cep',
            'principal',
        ]
        read_only_fields = ['id', 'usuario']

#Cria itens referenciando estoque para exibição no carrinho
class ItemCarrinhoSerializer(serializers.ModelSerializer):
    #Busca produto e tamanho pela tabela de estoque
    produto = serializers.CharField(source='estoque.produto.nome', read_only=True)
    tamanho = serializers.CharField(source='estoque.tamanho', read_only=True)
    preco = serializers.DecimalField(
        source='estoque.produto.preco',
        max_digits=10,
        decimal_places=2,
        read_only=True
    )
    subtotal = serializers.SerializerMethodField()

    class Meta:
        model = ItemCarrinho
        fields = ['id', 'estoque', 'produto', 'tamanho', 'preco', 'quantidade', 'subtotal']

    def get_subtotal(self, obj):
        return obj.estoque.produto.preco * obj.quantidade

    #Impede quantidade menor que 1
    def validate_quantidade(self, value):
        if value <= 0:
            raise serializers.ValidationError("A quantidade deve ser maior que zero.")
        return value

    #Valida se a quantidade existe em estoque antes de criar um ItemCarrinho
    def validate(self, attrs):
        estoque = attrs.get('estoque')
        quantidade = attrs.get('quantidade')

        if estoque and quantidade and quantidade > estoque.quantidade:
            raise serializers.ValidationError({
                'quantidade': 'Quantidade solicitada maior que a disponível em estoque.'
            })

        return attrs

#Atualiza item carrinho existente (quantidade, exclusão)
class AtualizarItemCarrinhoSerializer(serializers.ModelSerializer):
    class Meta:
        model = ItemCarrinho
        fields = ['quantidade']

    #Impede quantidade menor que 1
    def validate_quantidade(self, value):
        if value <= 0:
            raise serializers.ValidationError("A quantidade deve ser maior que zero.")
        return value

    #Valida se a quantidade existe em estoque antes de atualizar ItemCarrinho
    def validate(self, attrs):
        instance = self.instance
        quantidade = attrs.get('quantidade')

        if instance and quantidade > instance.estoque.quantidade:
            raise serializers.ValidationError({
                'quantidade': 'Quantidade solicitada maior que a disponível em estoque.'
            })

        return attrs

#Verifica os ItemCarrinho do usuário e calcula total
class CarrinhoSerializer(serializers.ModelSerializer):
    itens = ItemCarrinhoSerializer(many=True, read_only=True)
    total = serializers.SerializerMethodField()

    class Meta:
        model = Carrinho
        fields = ['id', 'usuario', 'itens', 'total']
        read_only_fields = ['id', 'usuario', 'itens', 'total']

    def get_total(self, obj):
        return sum(
            item.estoque.produto.preco * item.quantidade
            for item in obj.itens.all()
        )

# lucas - estoque
class EstoqueSerializer(serializers.ModelSerializer):
    class Meta:
        model = Estoque
        fields = ['id', 'produto', 'tamanho', 'quantidade']

# lucas - produto
class ProdutoSerializer(serializers.ModelSerializer):
    estoques = EstoqueSerializer(many=True, read_only=True)

    class Meta:
        model = Produto
        fields = [
            'id',
            'nome',
            'descricao',
            'preco',
            'marca',
            'status_ativo',
            'usuario_responsavel',
            'estoques'
        ]