from django.shortcuts import render, redirect
from werkzeug.security import generate_password_hash, check_password_hash

from mainapp.models import Usuario, Producto, Carrito, Item_carrito


def inicio(request):
    if request.method == 'POST':
        email = request.POST.get("email")
        password = request.POST.get("password")

        try:
            usuario = Usuario.objects.get(correo=email)
            if (check_password_hash(usuario.password, password)):
                request.session["usuario_id"] = str(usuario.id)
                return redirect("menu_usuario")
            else:
                return render(request, 'index.html', {'error_password': True})
        except:
            return render(request, 'index.html', {'error_correo': True})
    return render(request, 'index.html')


def registro(request):
    if request.method == 'POST':
        email = request.POST.get("email")
        password = request.POST.get("password")
        nombre = request.POST.get("nombre")
        telefono = request.POST.get("telefono")
        passwd_crypted = generate_password_hash(password, 'pbkdf2:sha256', 8)

        usuario = Usuario(correo=email, password=passwd_crypted, telefono=telefono, nombre=nombre)
        usuario.save()
        return redirect("inicio")

    return render(request, 'registro.html')


def menuPrincipal(request):
    if request.method == 'POST':
        categoria = request.POST.get("categoria")
        productos = Producto.objects.filter(categoria__nombre__icontains=categoria)
        return render(request, 'menu_principal.html', {'productos': productos})
    productos = Producto.objects.order_by('categoria_id')
    isLoged = False
    if "usuario_id" in request.session:
        isLoged = True
    return render(request, 'menu_principal.html', {'productos': productos, 'is_loged': isLoged})


def cerrarSesion(request):
    if request.session.has_key("usuario_id"):
        request.session.flush()
    return redirect('menu_usuario')


def anadirAlCarro(request, id):
    if "usuario_id" not in request.session:
        return redirect('inicio')

    producto = Producto.objects.get(id=id)
    try:
        carrito = Carrito.objects.get(usuario_id=request.session["usuario_id"], estado="activo")
        carrito.save()
        for item_carrito in Item_carrito.objects.filter(producto_id=id):
            item_carrito.cantidad = item_carrito.cantidad + 1
            item_carrito.subtotal = item_carrito.producto.precio * item_carrito.cantidad
            item_carrito.save()
            return redirect('carrito')
        item = Item_carrito(cantidad=1, subtotal=producto.precio, producto=producto, carrito=carrito)
        item.save()
        return redirect('carrito')
    except:
        carrito = Carrito(estado="activo", usuario_id=request.session["usuario_id"])
        carrito.save()
        item = Item_carrito(cantidad=1, subtotal=producto.precio, producto=producto, carrito=carrito)
        item.save()
        return redirect('carrito')


def carritoDelUsuario(request):
    if "usuario_id" not in request.session:
        return redirect('inicio')
    total = 0
    try:
        carrito = Carrito.objects.get(usuario_id=request.session["usuario_id"], estado="activo")
        items_carrito = Item_carrito.objects.filter(carrito=carrito)
        for item in items_carrito:
            if request.method == 'POST':
                cantidad_item = request.POST.get(str(item.id))
                if cantidad_item is not None:
                    item.cantidad = int(cantidad_item)
                    item.subtotal = item.producto.precio * int(cantidad_item)
                    item.save()
            total += item.subtotal

        if (carrito.total != total):
            carrito.total = total
            carrito.impuestos = total * 0.19
            carrito.save()
        return render(request, 'carrito.html', {'carrito': carrito, 'items': items_carrito})
    except:
        return render(request, 'carrito.html')


def eliminarProducto(request, id):
    if "usuario_id" not in request.session:
        return redirect('inicio')
    try:
        item_carrito = Item_carrito.objects.get(id=id, carrito__usuario_id=request.session["usuario_id"])
        item_carrito.delete()
        return redirect('carrito')
    except:
        return redirect('menu_usuario')


def actualizarCantidad(request, id, cantidad):
    if "usuario_id" not in request.session:
        return redirect('inicio')
    try:
        item_carrito = Item_carrito.objects.get(id=id, carrito__usuario_id=request.session["usuario_id"])
        item_carrito.cantidad = cantidad
        item_carrito.subtotal = item_carrito.producto.precio * cantidad
        item_carrito.save()
        return redirect('carrito')
    except:
        return redirect('menu_usuario')


def pago(request, id):
    if "usuario_id" not in request.session:
        return redirect('inicio')

    if request.method == 'POST':
        direccion = request.POST.get("direccion")

    carrito = Carrito.objects.get(id=id)
    items_carrito = Item_carrito.objects.filter(carrito=carrito)
    return render(request, 'pago.html', {'carrito': carrito, 'items': items_carrito})


def enviarCorreo(request):
    redirect('menu_usuario')
