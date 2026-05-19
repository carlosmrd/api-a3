from django.contrib import admin
from app.models import Usuario, Endereco, CartaoCredito, Produto, FormaVenda, Estoque

@admin.register(Usuario)
#Registro para usuário
class UsuarioAdmin(admin.ModelAdmin):
    list_display = ('id', 'email', 'nome', 'telefone', 'cpf', 'data_nascimento', 'is_active', 'is_staff')
    list_display_links = ('id', 'email')
    list_per_page = 20
    search_fields = ('id', 'email', 'cpf', 'nome')

@admin.register(Endereco)
#Registro para endereço de um usuário
class EnderecoAdmin(admin.ModelAdmin):
    list_display = ('id', 'usuario', 'logradouro', 'numero', 'bairro', 'cidade', 'estado', 'cep', 'principal')
    list_display_links = ('id', 'usuario')
    list_per_page = 20
    search_fields = ('usuario__email', 'cep', 'cidade')

@admin.register(CartaoCredito)
#Registro para endereço de um usuário (Só salva bandeira e últimos 4 digitos para exibição)
class CartaoCreditoAdmin(admin.ModelAdmin):
    list_display = ('id', 'usuario', 'bandeira', 'ultimos_digitos', 'nome_titular', 'validade_mes', 'validade_ano', 'principal')
    list_display_links = ('id', 'usuario')
    list_per_page = 20
    search_fields = ('usuario__email', 'nome_titular', 'ultimos_digitos')

class EstoqueInline(admin.TabularInline):
    #Classe para usar o model de estoque dentro de outra página (Produto).
    model = Estoque
    extra = 3
    fields = ('tamanho', 'quantidade')

@admin.register(Produto)
#Registro para produto
class ProdutoAdmin(admin.ModelAdmin):
    list_display = ('id', 'nome', 'marca', 'preco', 'status_ativo', 'usuario_responsavel')
    list_display_links = ('id', 'nome')
    list_filter = ('status_ativo', 'marca')
    search_fields = ('nome', 'marca', 'descricao', 'usuario_responsavel__email')
    list_per_page = 20
    inlines = [EstoqueInline]

@admin.register(FormaVenda)
class FormaVendaAdmin(admin.ModelAdmin):
    list_display = ('id', 'produto', 'tipo', 'condicoes_pagamento')
    list_display_links = ('id', 'produto')
    list_per_page = 20
    search_fields = ('produto__nome', 'condicoes_pagamento')
    list_filter = ('tipo',)