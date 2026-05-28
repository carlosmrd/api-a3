from rest_framework import viewsets
from app.models import Produto, Estoque
from app.serializers import ProdutoSerializer, EstoqueSerializer

# lucas - viewset para o CRUD completo de produtos
class ProdutoViewSet(viewsets.ModelViewSet):
    queryset = Produto.objects.all()
    serializer_class = ProdutoSerializer

# lucas - viewset para controlar as quantidades e tamanhos no estoque
class EstoqueViewSet(viewsets.ModelViewSet):
    queryset = Estoque.objects.all()
    serializer_class = EstoqueSerializer