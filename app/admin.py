from django.contrib import admin
from app.models import Usuario, Endereco
from app.models import Produto, FormaVenda

@admin.register(Usuario)
class UsuarioAdmin(admin.ModelAdmin):
    list_display = ('id', 'email', 'nome', 'telefone', 'cpf', 'data_nascimento', 'is_active', 'is_staff')
    list_display_links = ('id', 'email')
    list_per_page = 20
    search_fields = ('id', 'email', 'cpf', 'nome')

@admin.register(Endereco)
class EnderecoAdmin(admin.ModelAdmin):
    list_display = ('id', 'usuario', 'logradouro', 'numero', 'bairro', 'cidade', 'estado', 'cep', 'principal')
    list_display_links = ('id', 'usuario')
    list_per_page = 20
    search_fields = ('usuario__email', 'cep', 'cidade')

    # lucas
    @admin.register(Produto)
    class ProdutoAdmin(admin.ModelAdmin):
        list_display = ('id', 'nome', 'marca', 'tamanho', 'preco', 'status_ativo', 'usuario_responsavel')
        list_display_links = ('id', 'nome')
        list_per_page = 20
        search_fields = ('nome', 'marca', 'usuario_responsavel__email')
        list_filter = ('status_ativo', 'marca')

    @admin.register(FormaVenda)
    class FormaVendaAdmin(admin.ModelAdmin):
        list_display = ('id', 'produto', 'tipo', 'condicoes_pagamento')
        list_display_links = ('id', 'produto')
        list_per_page = 20
        search_fields = ('produto__nome', 'condicoes_pagamento')
        list_filter = ('tipo',)