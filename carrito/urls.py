"""carrito URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path

from mainapp.views import inicio, registro, menuPrincipal, cerrarSesion, anadirAlCarro, carritoDelUsuario, \
    eliminarProducto, pago

urlpatterns = [
    path('admin/', admin.site.urls),
    path('login', inicio, name='inicio'),
    path('registro', registro),
    path('', menuPrincipal, name='menu_usuario'),
    path('cerrar_sesion', cerrarSesion),
    path('anadir_al_carro/<int:id>', anadirAlCarro),
    path('carrito', carritoDelUsuario, name='carrito'),
    path('eliminar_producto/<int:id>', eliminarProducto),
    path('pago/<int:id>', pago),
]
