from django.db import models


# Create your models here.
class Usuario(models.Model):
    nombre = models.CharField(max_length=255)
    correo = models.CharField(max_length=255)
    password = models.CharField(max_length=255)
    telefono = models.CharField(max_length=10)


class Categoria(models.Model):
    nombre = models.CharField(max_length=255)


class Producto(models.Model):
    nombre = models.CharField(max_length=255)
    categoria = models.ForeignKey(Categoria, on_delete=models.SET_NULL, null=True)
    descripcion = models.CharField(max_length=255)
    precio = models.IntegerField()
    foto = models.TextField()


class Carrito(models.Model):
    estado = models.CharField(max_length=255)
    total = models.IntegerField(default=0)
    impuestos = models.IntegerField(default=0)
    direccion = models.CharField(max_length=255,null=True)
    usuario = models.ForeignKey(Usuario, on_delete=models.SET_NULL, null=True)


class Item_carrito(models.Model):
    cantidad = models.IntegerField()
    subtotal = models.IntegerField()
    producto = models.ForeignKey(Producto, on_delete=models.SET_NULL, null=True)
    carrito = models.ForeignKey(Carrito, on_delete=models.SET_NULL, null=True)


class Factura(models.Model):
    carrito = models.ForeignKey(Carrito, on_delete=models.SET_NULL, null=True)
    costo_envio = models.IntegerField(default=0)
    fecha_creacion = models.DateTimeField()
    fecha_llegada = models.DateTimeField()
