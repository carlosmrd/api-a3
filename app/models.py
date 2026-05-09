from django.db import models

class Usuario(models.Model):
    id = models.AutoField(primary_key=True)
    email = models.CharField(max_length = 30)
    senha = models.CharField(max_length = 20)
    nome = models.CharField(max_length = 30)
    telefone = models.CharField(max_length = 11)
    data_nascimento = models.DateField()
    cpf = models.CharField(max_length = 11)
    endereco = models.CharField(max_length = 100)
    cep = models.CharField(max_length = 8)
    endereco_numero = models.CharField(max_length = 4)
    def __str__(self):
        return self.username