from rest_framework import viewsets
from app.models import Produto
from app.serializers import ProdutoSerializer

# lucas -  CRUD completo de produtos
class ProdutoViewSet(viewsets.ModelViewSet):
    # Puxa todos os produtos do banco
    queryset = Produto.objects.all()
    # Diz qual tradutor (serializer) vai ser usado
    serializer_class = ProdutoSerializer
    serializer_class = ProdutoSerializer