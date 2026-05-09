from django.contrib import admin
from app.models import Usuario

class Usuarios(admin.ModelAdmin):
    list_display = ('id','email','senha','nome','telefone','data_nascimento','cpf','endereco','cep','endereco_numero')
    list_display_links = ('id','email')
    list_per_page = 20
    search_fields = ('id','email')

admin.site.register(Usuario,Usuarios)