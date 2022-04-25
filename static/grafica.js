const carritos = JSON.parse(
  document.getElementById("carritos").innerHTML.replaceAll("'", '"')
);
const items = JSON.parse(
  document.getElementById("items").innerHTML.replaceAll("'", '"')
);
const productos = JSON.parse(
  document.getElementById("productos").innerHTML.replaceAll("'", '"')
);
const categorias = JSON.parse(
  document.getElementById("categorias").innerHTML.replaceAll("'", '"')
);
const facturas = JSON.parse(
  document.getElementById("facturas").innerHTML.replaceAll("'", '"')
);
facturas.sort((a, b) => {
  if (new Date(a.fecha_creacion) < new Date(b.fecha_creacion)) {
    return -1;
  }
  if (new Date(a.fecha_creacion) > new Date(b.fecha_creacion)) {
    return 1;
  }
  return 0;
});

/*Generar objeto completo de factura*/
facturas.map((factura) => {
  const carrito = carritos.find((carrito) => factura.carrito_id == carrito.id);
  const itemsPorCarrito = items.filter((item) => item.carrito_id == carrito.id);
  itemsPorCarrito.map((item) => {
    const producto = productos.find(
      (producto) => item.producto_id == producto.id
    );
    const categoria = categorias.find(
      (categoria) => producto.categoria_id == categoria.id
    );
    item.producto = producto;
    item.producto.categoria = categoria.nombre;
    delete item.carrito_id;
    delete item.producto_id;
    return item;
  });
  factura.carrito = carrito;
  factura.carrito.items = itemsPorCarrito;
  delete factura.carrito_id;
  return factura;
});

/*Data de ventas en total por dia*/
const ventasTotalPorDia = facturas.reduce((accumulator, value) => {
  return {
    ...accumulator,
    [value.fecha_creacion]: (accumulator[value.fecha_creacion] || 0) + 1,
  };
}, {});

/*ChartJS */
const ctx = document.getElementById("myChart").getContext("2d");
const myChartVentas = new Chart(ctx, {
  type: "line",
  data: {
    labels: Object.keys(ventasTotalPorDia),
    datasets: [
      {
        label: "Total por día",
        data: Object.values(ventasTotalPorDia),
        borderColor: "rgba(255, 99, 132, 1)",
        borderWidth: 1,
      },
    ],
  },
  options: {
    scales: {
      y: {
        beginAtZero: true,
      },
    },
  },
});

/*Data de ventas(Precio) por mes*/
const ventasPorDia = facturas.reduce((accumulator, value) => {
  return {
    ...accumulator,
    [value.fecha_creacion]:
      (accumulator[value.fecha_creacion] || 0) + value.carrito.total,
  };
}, {});

const ctx2 = document.getElementById("myChart2").getContext("2d");
const myChartVentasDinero = new Chart(ctx2, {
  type: "bar",
  data: {
    labels: Object.keys(ventasPorDia),
    datasets: [
      {
        label: "Ventas por día",
        data: Object.values(ventasPorDia),
        borderColor: "rgba(255, 99, 132, 1)",
        borderWidth: 1,
      },
    ],
  },
  options: {
    scales: {
      y: {
        beginAtZero: true,
      },
    },
  },
});

/*Data de ventas(Precio) por producto*/
const productosPorFactura = [];
facturas.forEach((factura) => {
  factura.carrito.items.forEach((item) => {
    productosPorFactura.push(item);
  });
});
const ventasPorProducto = productosPorFactura.reduce((accumulator, value) => {
  return {
    ...accumulator,
    [value.producto.nombre]:
      (accumulator[value.producto.nombre] || 0) + value.cantidad,
  };
}, {});

const ctx3 = document.getElementById("myChart3").getContext("2d");
const myChartVentasPorProducto = new Chart(ctx3, {
  type: "bar",
  data: {
    labels: Object.keys(ventasPorProducto),
    datasets: [
      {
        label: "Ventas por producto",
        data: Object.values(ventasPorProducto),
        borderColor: "rgba(255, 99, 132, 1)",
        borderWidth: 1,
      },
    ],
  },
  options: {
    scales: {
      y: {
        beginAtZero: true,
      },
    },
  },
});
