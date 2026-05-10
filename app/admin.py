from django.contrib import admin
from app.models import Usuario, Endereco

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