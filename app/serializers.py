from rest_framework import serializers
from app.models import Produto, Estoque

# lucas - estoque
class EstoqueSerializer(serializers.ModelSerializer):
    class Meta:
        model = Estoque
        fields = ['id', 'produto', 'tamanho', 'quantidade']

# lucas -  produto
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