from rest_framework import serializers
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError as DjangoValidationError
from app.models import Produto, Estoque, Usuario, Endereco

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