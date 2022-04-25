from django.contrib import admin

# Register your models here.
from mainapp.models import Usuario, Categoria, Producto, Carrito, Item_carrito, Factura, Administrador

admin.site.register(Usuario)
admin.site.register(Categoria)
admin.site.register(Producto)
admin.site.register(Carrito)
admin.site.register(Item_carrito)
admin.site.register(Factura)
admin.site.register(Administrador)
