from django.contrib import admin
from .models import ProductoServicio, Presupuesto, DetallePresupuesto
# Register your models here.

class DetallePresupuestoInline(admin.TabularInline):
    model = DetallePresupuesto
    extra = 1


@admin.register(Presupuesto)
class PresupuestoAdmin(admin.ModelAdmin):
    inlines = [DetallePresupuestoInline]
    list_display = ("folio", "fecha")



admin.site.register(ProductoServicio)
