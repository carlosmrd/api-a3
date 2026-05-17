from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager

class UsuarioManager(BaseUserManager):
    def criar_usuario(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("O e-mail é obrigatório")
        email = self.normalize_email(email)
        usuario = self.model(email=email, **extra_fields)
        usuario.set_password(password)
        usuario.save(using=self._db)
        return usuario

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        return self.criar_usuario(email, password, **extra_fields)

class Usuario(AbstractBaseUser):
    email = models.EmailField(max_length=254, unique=True)
    nome = models.CharField(max_length=100)
    telefone = models.CharField(max_length=11)
    data_nascimento = models.DateField(null=True, blank=True)
    cpf = models.CharField(max_length=11, unique=True)

    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["nome", "cpf"]

    objects = UsuarioManager()

    #Propriedades para o AUTH_USER_MODEL
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
    usuario = models.ForeignKey(
        Usuario,
        on_delete=models.CASCADE,
        related_name="enderecos"
    )
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


# lucas

class Produto(models.Model):
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

    # detalhes especificos pro nosso nicho de tenis
    marca = models.CharField(max_length=50, help_text="Ex: Nike, Adidas, Puma")
    tamanho = models.CharField(max_length=5, help_text="Ex: 39, 40, 41")

    def __str__(self):
        return f"{self.nome} - Tam: {self.tamanho} (R$ {self.preco})"


class FormaVenda(models.Model):
    # opcoes de venda que a loja vai aceitar
    TIPO_VENDA_CHOICES = [
        ('UN', 'Unitária (Par)'),
        ('AT', 'Atacado (Caixa com 12)'),
        ('EN', 'Encomenda (Importação)'),
    ]
    tipo = models.CharField(max_length=2, choices=TIPO_VENDA_CHOICES, default='UN')

    # como o cliente pode pagar esse tenis especifico
    condicoes_pagamento = models.CharField(
        max_length=200,
        help_text="Ex: PIX com 10% OFF, Cartão em até 12x"
    )

    # vincula a regra de venda ao tenis certo
    produto = models.ForeignKey(
        Produto,
        on_delete=models.CASCADE,
        related_name="formas_venda"
    )

    def __str__(self):
        return f"{self.get_tipo_display()} - {self.produto.nome}"