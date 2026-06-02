from django.contrib import admin
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from app import views

# lucas - configurando as rotas da api com o roteador do DRF
router = DefaultRouter()
router.register(r'produtos', views.ProdutoViewSet, basename='produto')
router.register(r'estoques', views.EstoqueViewSet, basename='estoque')
router.register(r'enderecos', views.EnderecoViewSet, basename='enderecos')
router.register(r'carrinho', views.CarrinhoViewSet, basename='carrinho')
router.register(r'itens-carrinho', views.ItemCarrinhoViewSet, basename='itens-carrinho')

urlpatterns = [
    path('admin/', admin.site.urls),
    # Inclui todas as rotas automáticas que o DRF criou
    path('api/', include(router.urls)),
    path('api/auth/registro/', views.RegistroView.as_view()),
    path('api/auth/login/', views.LoginView.as_view()),
    path('api/auth/logout/', views.LogoutView.as_view()),
    path('api/auth/perfil/', views.PerfilView.as_view()),
]