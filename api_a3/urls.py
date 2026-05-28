from django.contrib import admin
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from app import views

# lucas - configurando as rotas da api com o roteador do DRF
router = DefaultRouter()
router.register(r'produtos', views.ProdutoViewSet, basename='produto')

router.register(r'estoque', views.EstoqueViewSet, basename='estoque')

urlpatterns = [
    path('admin/', admin.site.urls),
    # Inclui todas as rotas automáticas que o DRF criou
    path('api/', include(router.urls)),
]