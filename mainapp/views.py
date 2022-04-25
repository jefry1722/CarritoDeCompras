import datetime
import smtplib
import time
from django.shortcuts import render, redirect
from werkzeug.security import generate_password_hash, check_password_hash
from mainapp.models import Usuario, Producto, Carrito, Item_carrito, Factura, Administrador, Categoria
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter


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


def loginAdministrador(request):
    if request.method == 'POST':
        email = request.POST.get("email")
        password = request.POST.get("password")
        try:
            administrador = Administrador.objects.get(correo=email)

            if administrador.password == password:
                request.session["admin_id"] = str(administrador.id)
                return redirect("menu_admin")
            else:
                return render(request, 'login_admin.html', {'error_password': True})
        except:
            return render(request, 'login_admin.html', {'error_correo': True})
    return render(request, 'login_admin.html')


def menuAdministrador(request):
    if "admin_id" not in request.session:
        return redirect('login_admin')
    carritos = list(Carrito.objects.filter(estado="completado").values('id', 'estado', 'total', 'impuestos', 'direccion', 'usuario_id'))
    items = list(Item_carrito.objects.values('id', 'cantidad', 'subtotal', 'carrito_id', 'producto_id'))
    productos = list(Producto.objects.values('id', 'nombre', 'descripcion', 'precio', 'categoria_id'))
    categorias = list(Categoria.objects.values('id', 'nombre'))
    facturas = list(Factura.objects.values('id', 'costo_envio', 'fecha_creacion', 'fecha_llegada', 'carrito_id'))
    for factura in facturas:
        factura["fecha_llegada"] = (factura["fecha_llegada"]).strftime(
            "%Y-%m-%d").__str__()
        factura["fecha_creacion"] = (factura["fecha_creacion"]).strftime(
            "%Y-%m-%d").__str__()
    return render(request, 'menu_admin.html',
                  {'carritos': carritos, 'items': items, 'productos': productos, 'facturas': facturas,
                   'categorias': categorias})


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
    isLoged = False
    if "usuario_id" in request.session:
        isLoged = True

    if request.method == 'POST':
        categoria = request.POST.get("categoria")
        productos = Producto.objects.filter(categoria__nombre__icontains=categoria)
        return render(request, 'menu_principal.html', {'productos': productos, 'is_loged': isLoged})
    productos = Producto.objects.order_by('categoria_id')
    return render(request, 'menu_principal.html', {'productos': productos, 'is_loged': isLoged})


def cerrarSesion(request):
    if request.session.has_key("usuario_id"):
        request.session.flush()
    if request.session.has_key("admin_id"):
        request.session.flush()
    return redirect('menu_usuario')


def anadirAlCarro(request, id):
    if "usuario_id" not in request.session:
        return redirect('inicio')

    producto = Producto.objects.get(id=id)
    try:
        carrito = Carrito.objects.get(usuario_id=request.session["usuario_id"], estado="activo")
        carrito.save()
        for item_carrito in Item_carrito.objects.filter(producto_id=id, carrito__estado="activo"):
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

    carrito = Carrito.objects.get(id=id)
    items_carrito = Item_carrito.objects.filter(carrito=carrito)
    if request.method == 'POST':
        direccion = request.POST.get("direccion")
        carrito.direccion = direccion
        carrito.estado = "completado"
        carrito.save()
        usuario = Usuario.objects.get(id=request.session["usuario_id"])
        costo_envio = 0
        if carrito.total < 100000:
            costo_envio = 10000
        factura = Factura(costo_envio=costo_envio, fecha_creacion=datetime.datetime.now(),
                          fecha_llegada=(datetime.datetime.now() + datetime.timedelta(days=3)).strftime("%Y-%m-%d"),
                          carrito=carrito)
        factura.save()
        enviarCorreo(carrito, items_carrito, usuario.correo, factura)
        return redirect('menu_usuario')

    return render(request, 'pago.html', {'carrito': carrito, 'items': items_carrito})


def enviarCorreo(carrito, items, correo_destino, factura):
    port = 587
    email = "jefrynaicipa1@gmail.com"
    codigo = "vtfiydwicqajouoz"
    costo_total = carrito.total + factura.costo_envio + carrito.impuestos
    costo_total = "{:,}".format(costo_total).replace(",", ".")
    message = MIMEMultipart()
    message["From"] = email
    message["To"] = correo_destino
    message["Subject"] = "Envio de factura"
    message.attach(MIMEText("El costo total es: $" + costo_total + "\nEn la factura puedes revisar tus productos"))
    generarPdf(message, factura, carrito, items)
    server = smtplib.SMTP("smtp.gmail.com", port)
    server.starttls()
    server.login(email, codigo)
    server.sendmail(email, [correo_destino], message.as_string())
    server.quit()


def generarPdf(message, factura, carrito, items):
    costo_total = carrito.total + factura.costo_envio + carrito.impuestos
    costo_total = "{:,}".format(costo_total).replace(",", ".")

    c = canvas.Canvas("documento.pdf", pagesize=letter)
    c.setFont("Times-Roman", 12)
    c.setLineWidth(.3)
    c.drawString(50, 700, 'FACTURA DE VENTA')
    c.line(50, 750, 1050, 747)
    c.drawString(50, 660, "El costo de los productos es: $" + "{:,}".format(carrito.total).replace(",", "."))
    c.drawString(50, 640, "El costo de los impuestos es: $" + "{:,}".format(carrito.impuestos).replace(",", "."))
    c.drawString(50, 620, "El costo del envio es: $" + "{:,}".format(factura.costo_envio).replace(",", "."))
    c.drawString(50, 600, "El costo total es: $" + costo_total)
    c.drawString(50, 560, "La fecha de llegada del pedido es: " + factura.fecha_llegada.__str__())
    c.drawString(50, 540, "TUS PRODUCTOS")
    y_position = 520
    for item in items:
        c.drawString(50, y_position, "Producto: " + item.producto.nombre.encode('ascii', 'ignore').decode(
            'ascii') + " - Cantidad: " + str(item.cantidad) + " - Costo: $" + "{:,}".format(item.subtotal).replace(
            ",", "."))
        y_position -= 20
    c.showPage()
    c.save()
    time.sleep(1)
    archivo_adjunto = open("documento.pdf", 'rb')
    adjunto_MIME = MIMEBase('application', 'octet-stream')
    adjunto_MIME.set_payload((archivo_adjunto.read()))
    encoders.encode_base64(adjunto_MIME)
    adjunto_MIME.add_header('Content-Disposition', "attachment; filename= documento.pdf")
    message.attach(adjunto_MIME)
