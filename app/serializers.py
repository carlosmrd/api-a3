from rest_framework import serializers
from app.models import Produto, Estoque

# lucas -  estoque
class EstoqueSerializer(serializers.ModelSerializer):
    class Meta:
        model = Estoque
        fields = ['id', 'tamanho', 'quantidade']

# lucas -  produto
class ProdutoSerializer(serializers.ModelSerializer):
    # Essa linha puxa as informações do estoque pra dentro do produto
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