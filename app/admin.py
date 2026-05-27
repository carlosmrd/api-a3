from django.contrib import admin
from app.models import Usuario, Endereco, CartaoCredito, Produto, Estoque, Carrinho, ItemCarrinho, Pedido, ItemPedido

#Registro para usuário
@admin.register(Usuario)
class UsuarioAdmin(admin.ModelAdmin):
    list_display = ('id', 'email', 'nome', 'telefone', 'cpf', 'data_nascimento', 'is_active', 'is_staff')
    list_display_links = ('id', 'email')
    list_per_page = 20
    search_fields = ('id', 'email', 'cpf', 'nome')

#Registro para endereço de um usuário
@admin.register(Endereco)
class EnderecoAdmin(admin.ModelAdmin):
    list_display = ('id', 'usuario', 'logradouro', 'numero', 'bairro', 'cidade', 'estado', 'cep', 'principal')
    list_display_links = ('id', 'usuario')
    list_per_page = 20
    search_fields = ('usuario__email', 'cep', 'cidade')

#Registro para cartão de crédito de um usuário (Só salva bandeira e últimos 4 digitos para exibição)
@admin.register(CartaoCredito)
class CartaoCreditoAdmin(admin.ModelAdmin):
    list_display = ('id', 'usuario', 'bandeira', 'ultimos_digitos', 'nome_titular', 'validade_mes', 'validade_ano',
                    'principal')
    list_display_links = ('id', 'usuario')
    list_per_page = 20
    search_fields = ('usuario__email', 'nome_titular', 'ultimos_digitos')

#Classe para usar o model de estoque dentro de outra página (Produto).
class EstoqueInline(admin.TabularInline):
    model = Estoque
    extra = 3
    fields = ('tamanho', 'quantidade')

#Registro para produto
@admin.register(Produto)
class ProdutoAdmin(admin.ModelAdmin):
    list_display = ('id', 'nome', 'marca', 'preco', 'status_ativo', 'usuario_responsavel')
    list_display_links = ('id', 'nome')
    list_filter = ('status_ativo', 'marca')
    search_fields = ('nome', 'marca', 'descricao', 'usuario_responsavel__email')
    list_per_page = 20
    inlines = [EstoqueInline]

#Classe para usar o model de ItemCarrinho dentro de outra página (Carrinho).
class ItemCarrinhoInline(admin.TabularInline):
    model = ItemCarrinho
    #Não exibe linhas porque não precisa ser cadastrado manualmente
    extra = 0
    fields = ('estoque', 'quantidade')
    #Impede que o carrinho seja editado pelo Django Admin, comentado para teste.
    #readonly_fields = ('estoque')

#Registro para carrinho
@admin.register(Carrinho)
class CarrinhoAdmin(admin.ModelAdmin):
    list_display = ('id', 'usuario', 'total')
    list_display_links = ('id', 'usuario')
    search_fields = ('usuario__email',)
    list_per_page = 20
    inlines = [ItemCarrinhoInline]

#Classe para usar o model de ItemPedido dentro de outra página (Pedido).
class ItemPedidoInline(admin.TabularInline):
    model = ItemPedido
    #Não exibe linhas porque não precisa ser cadastrado manualmente
    extra = 0
    fields = ('estoque', 'quantidade', 'preco_unitario')
    #Impede que o pedido seja editado pelo Django Admin
    readonly_fields = ('estoque', 'quantidade', 'preco_unitario')

#Registro para pedido
@admin.register(Pedido)
class PedidoAdmin(admin.ModelAdmin):
    list_display = ('id', 'usuario', 'status', 'total', 'data_criacao')
    list_display_links = ('id', 'usuario')
    list_filter = ('status',)
    search_fields = ('usuario__email',)
    list_per_page = 20
    inlines = [ItemPedidoInline]