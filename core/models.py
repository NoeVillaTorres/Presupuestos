from django.db import models


class ProductoServicio(models.Model):
    categoria = models.CharField(max_length=100)
    descripcion = models.CharField(max_length=300)
    precio_unitario = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return self.descripcion


# core/models.py


class Presupuesto(models.Model):
    folio = models.CharField(
        max_length=20,
        unique=True,
        editable=False
    )
    fecha = models.DateTimeField(auto_now_add=True)

    # --- NUEVOS CAMPOS ---
    proyecto = models.CharField(max_length=200, default="Proyecto...")
    cliente_nombre = models.CharField(max_length=200, blank=True, null=True)
    cliente_direccion = models.CharField(max_length=300, blank=True, null=True)
    cliente_ciudad = models.CharField(max_length=100, blank=True, null=True)
    cliente_cp = models.CharField(max_length=10, blank=True, null=True)


    def save(self, *args, **kwargs):
        if not self.pk and not self.folio:
            ultimo = Presupuesto.objects.order_by("id").last()
            numero = (ultimo.id + 1) if ultimo else 1
            self.folio = f"P-{numero:05d}"
        super().save(*args, **kwargs)

    def __str__(self):
        return self.folio
    @property
    def total(self):
        return sum(d.subtotal for d in self.detalles.all())



class DetallePresupuesto(models.Model):
    presupuesto = models.ForeignKey(Presupuesto, on_delete=models.CASCADE, related_name="detalles")
    producto = models.ForeignKey(ProductoServicio, on_delete=models.PROTECT)
    cantidad = models.DecimalField(max_digits=10, decimal_places=2)
    # --- NUEVO CAMPO ---
    unidad = models.CharField(max_length=20, default="PZA")
    @property    
    def subtotal(self):
        return self.cantidad * self.producto.precio_unitario
