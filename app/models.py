from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager

class UsuarioManager(BaseUserManager):
    #Registro para usuário
    def criar_usuario(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("O e-mail é obrigatório")
        email = self.normalize_email(email)
        usuario = self.model(email=email, **extra_fields)
        usuario.set_password(password)
        usuario.save(using=self._db)
        return usuario

    #Registro para funcionário ou superusuário
    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        return self.criar_usuario(email, password, **extra_fields)

#Parâmetros do usuário para o UsuarioManager
class Usuario(AbstractBaseUser):
    class Meta:
        verbose_name = "Usuário"
        verbose_name_plural = "Usuários"

    email = models.EmailField(max_length=254, unique=True)
    nome = models.CharField(max_length=100)
    telefone = models.CharField(max_length=11)
    data_nascimento = models.DateField()
    cpf = models.CharField(max_length=11, unique=True)

    is_active = models.BooleanField(default=True)
    #Define se usuário é funcionário ou superusuário
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)

    #Define email como campo de login
    USERNAME_FIELD = "email"
    #Define nome e cpf como campos obrigatórios ao criar um usuário, mesmo com o createsuperuser.
    REQUIRED_FIELDS = ["nome", "cpf"]

    objects = UsuarioManager()

    #Propriedades para o AUTH_USER_MODEL no settings.py
    @property
    def is_anonymous(self):
        return False

    @property
    def is_authenticated(self):
        return True

    def has_perm(self, perm, obj=None):
        return self.is_superuser

    def has_module_perms(self, app_label):
        return self.is_superuser

    def __str__(self):
        return self.email

class Endereco(models.Model):
    class Meta:
        verbose_name = "Endereço"
        verbose_name_plural = "Endereços"

    #Cria uma foreign key "usuario_id" na tabela Endereco referente ao id na tabela Usuario
    usuario = models.ForeignKey(
        Usuario,
        on_delete=models.CASCADE,
        related_name="enderecos"
    )

    #Informações do endereço
    logradouro = models.CharField(max_length=200)
    numero = models.CharField(max_length=10)
    complemento = models.CharField(max_length=100, blank=True)
    bairro = models.CharField(max_length=100)
    cidade = models.CharField(max_length=100)
    estado = models.CharField(max_length=2)
    cep = models.CharField(max_length=8)
    #Boolean para o endereço padrão
    principal = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.logradouro}, {self.numero} — {self.cidade}/{self.estado}"

class CartaoCredito(models.Model):
    class Meta:
        verbose_name = "Cartão de Crédito"
        verbose_name_plural = "Cartões de Crédito"

    BANDEIRAS = [
        ('visa', 'Visa'),
        ('mastercard', 'Mastercard'),
        ('elo', 'Elo'),
        ('amex', 'American Express'),
        ('hipercard', 'Hipercard'),
    ]

    #Cria uma foreign key "usuario_id" na tabela CartaoCredito referente ao id na tabela Usuario
    usuario = models.ForeignKey(
        Usuario,
        on_delete=models.CASCADE,
        related_name="cartoes"
    )

    nome_titular = models.CharField(max_length=100)
    #Não salva número completo do cartão nem CVV, somente dados para exibição.
    ultimos_digitos = models.CharField(max_length=4)
    bandeira = models.CharField(max_length=20, choices=BANDEIRAS)
    validade_mes = models.PositiveSmallIntegerField()
    validade_ano = models.PositiveSmallIntegerField()
    #Boolean para o cartão padrão
    principal = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.get_bandeira_display()} •••• {self.ultimos_digitos} ({self.nome_titular})"


class Produto(models.Model):
    class Meta:
        verbose_name = "Produto"
        verbose_name_plural = "Produtos"

    # infos principais do tenis
    nome = models.CharField(max_length=200, help_text="Ex: Air Jordan 1 Retro")
    descricao = models.TextField(help_text="Detalhes do tênis (material, cor, etc.)")
    preco = models.DecimalField(max_digits=10, decimal_places=2)
    status_ativo = models.BooleanField(default=True)

    # liga com o usuario que cadastrou o produto para saber quem foi
    usuario_responsavel = models.ForeignKey(
        Usuario,
        on_delete=models.CASCADE,
        related_name="tenis_cadastrados"
    )

    # detalhes especificos para o nosso nicho de tenis
    marca = models.CharField(max_length=50, help_text="Ex: Nike, Adidas, Puma")

    def __str__(self):
        return f"{self.nome} (R$ {self.preco})"

class Estoque(models.Model):
    class Meta:
        verbose_name = "Estoque"
        verbose_name_plural = "Estoques"
        #UniqueConstraint para impedir que o mesmo tamanho seja cadastrado várias vezes no mesmo produto
        constraints = [
            models.UniqueConstraint(
                fields=["produto", "tamanho"],
                name="estoque_produto_tamanho_unico"
            )
        ]

    TAMANHOS = [
        ('33', '33'), ('33.5', '33,5'),
        ('34', '34'), ('34.5', '34,5'),
        ('35', '35'), ('35.5', '35,5'),
        ('36', '36'), ('36.5', '36,5'),
        ('37', '37'), ('37.5', '37,5'),
        ('38', '38'), ('38.5', '38,5'),
        ('39', '39'), ('39.5', '39,5'),
        ('40', '40'), ('40.5', '40,5'),
        ('41', '41'), ('41.5', '41,5'),
        ('42', '42'), ('42.5', '42,5'),
        ('43', '43'), ('43.5', '43,5'),
        ('44', '44'), ('44.5', '44,5'),
        ('45', '45'), ('45.5', '45,5'),
        ('46', '46'), ('46.5', '46,5'),
    ]

    #Cria uma foreign key "produto_id" na tabela Estoque referente ao id na tabela Produto
    produto = models.ForeignKey(
        Produto,
        on_delete=models.CASCADE,
        related_name="estoques"
    )

    tamanho = models.CharField(max_length=4, choices=TAMANHOS)
    quantidade = models.PositiveIntegerField(default=0)

    def __str__(self):
        return f"{self.produto.nome} | Tam {self.tamanho} | Qtd: {self.quantidade}"

class Carrinho(models.Model):
    class Meta:
        verbose_name = "Carrinho"
        verbose_name_plural = "Carrinhos"

    #Cria uma foreign key "usuario_id" na tabela Carrinho referente ao id na tabela Usuário
    #OneToOne para criar um único carrinho para cada usuário
    usuario = models.OneToOneField(
        Usuario,
        on_delete=models.CASCADE,
        related_name="carrinho"
    )

    def total(self):
        return sum(item.subtotal() for item in self.itens.all())

    def __str__(self):
        return f"Carrinho de {self.usuario.email}"

class ItemCarrinho(models.Model):
    #ItemCarrinho serve como intermediário entre Carrinho e Estoque, para definir a quantidade de um produto que vai
    #ser comprada e o tamanho que o cliente quer
    class Meta:
        verbose_name = "Item do Carrinho"
        verbose_name_plural = "Itens do Carrinho"
        constraints = [
            models.UniqueConstraint(
                fields=["carrinho", "estoque"],
                name="item_carrinho_estoque_unico"
            )
        ]

    #Cria uma foreign key "carrinho_id" na tabela ItemCarrinho referente ao id na tabela Carrinho
    #Conecta o item de ItemCarrinho com o Carrinho (que conecta a cliente)
    carrinho = models.ForeignKey(
        Carrinho,
        on_delete=models.CASCADE,
        related_name="itens"
    )

    #Conecta o item de ItemCarrinho ao Estoque (Que tem informação de tamanhos e quantidade em estoque)
    estoque = models.ForeignKey(
        Estoque,
        on_delete=models.CASCADE,
        related_name="itens_carrinho"
    )
    quantidade = models.PositiveIntegerField(default=1)

    def subtotal(self):
        return self.quantidade * self.estoque.produto.preco

    def __str__(self):
        return f"{self.quantidade}x {self.estoque.produto.nome} (Tam {self.estoque.tamanho})"

class Pedido(models.Model):
    class Meta:
        verbose_name = "Pedido"
        verbose_name_plural = "Pedidos"

    STATUS = [
        ('pendente', 'Pendente'),
        ('pago', 'Pago'),
        ('enviado', 'Enviado'),
        ('entregue', 'Entregue'),
        ('cancelado', 'Cancelado'),
    ]

    #Cria uma foreign key "usuario_id" na tabela Pedido referente ao id na tabela Usuário
    usuario = models.ForeignKey(
        Usuario,
        on_delete=models.CASCADE,
        related_name="pedidos"
    )

    #Cria uma foreign key "endereco_id" na tabela Pedido referente ao id na tabela Endereco
    #Referente ao endereço selecionado no checkout
    endereco = models.ForeignKey(
        Endereco,
        on_delete=models.SET_NULL,
        null=True,
        related_name="pedidos"
    )

    #Informações do pedido
    status = models.CharField(max_length=10, choices=STATUS, default='pendente')
    data_criacao = models.DateTimeField(auto_now_add=True)
    total = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"Pedido #{self.id} - {self.usuario.email} ({self.get_status_display()})"


class ItemPedido(models.Model):
    #ItemPedido serve para registrar os ItemCarrinho no Pedido final
    class Meta:
        verbose_name = "Item do Pedido"
        verbose_name_plural = "Itens do Pedido"

    #Cria uma foreign key "pedido_id" na tabela ItemPedido referente ao id na tabela Pedido
    pedido = models.ForeignKey(
        Pedido,
        on_delete=models.CASCADE,
        related_name="itens"
    )

    #Conecta o item de ItemCarrinho ao Estoque (Que tem informação de tamanhos e quantidade em estoque)
    #SET_NULL ao invés de CASCADE no delete para salvar pedidos mesmo que o produto seja excluído
    estoque = models.ForeignKey(
        Estoque,
        on_delete=models.SET_NULL,
        null=True,
        related_name="itens_pedido"
    )

    #Preço e quantidade congelados para serem registrados no momento da compra
    quantidade = models.PositiveIntegerField()
    preco_unitario = models.DecimalField(max_digits=10, decimal_places=2)

    def subtotal(self):
        return self.quantidade * self.preco_unitario

    def __str__(self):
        if self.estoque:
            return f"{self.quantidade}x {self.estoque.produto.nome} (Tam {self.estoque.tamanho})"
        #Evita erros em produtos removidos, que vão retornar None
        return f"{self.quantidade}x [produto removido]"