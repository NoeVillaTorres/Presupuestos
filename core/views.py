import os
from django.conf import settings
from django.contrib.staticfiles import finders
from django.shortcuts import render, redirect, get_object_or_404
from .models import ProductoServicio, Presupuesto, DetallePresupuesto
from .forms import ProductoForm, DetallePresupuestoForm, PresupuestoInfoForm
from django.template.loader import render_to_string
from django.http import HttpResponse
from weasyprint import HTML
from django.db.models import Q, F
from django.contrib.auth.decorators import login_required


@login_required
def index(request):
    return render(request, "core/index.html")

@login_required
def catalogo_list(request):
    query = request.GET.get('q', '').strip()
    productos = ProductoServicio.objects.all()
    
    if query:
        # Buscamos coincidencias en descripción o en categoría
        productos = productos.filter(
            Q(descripcion__icontains=query) | Q(categoria__icontains=query)
        )

    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        html = render_to_string('core/partials/catalogo_rows.html', {'productos': productos})
        return HttpResponse(html)

    return render(request, 'core/catalogo.html', {'productos': productos, 'query': query})

@login_required
def catalogo_eliminar(request, pk):
    producto = get_object_or_404(ProductoServicio, pk=pk)
    if request.method == 'POST':
        producto.delete()
    return redirect('catalogo_list')

@login_required
def catalogo_form(request, pk=None):
    producto = get_object_or_404(ProductoServicio, pk=pk) if pk else None

    if request.method == "POST":
        form = ProductoForm(request.POST, instance=producto)
        if form.is_valid():
            producto = form.save(commit=False)

            categoria_nueva = form.cleaned_data.get("categoria_nueva")
            categoria = form.cleaned_data.get("categoria")

            if categoria_nueva:
                producto.categoria = categoria_nueva
            else:
                producto.categoria = categoria

            producto.save()
            return redirect("catalogo_list")
    else:
        form = ProductoForm(instance=producto)

    return render(request, "core/catalogo_form.html", {"form": form})

@login_required
def crear_presupuesto(request):
    presupuesto = Presupuesto.objects.create()
    return redirect("detalle_presupuesto", pk=presupuesto.id)

@login_required
def detalle_presupuesto(request, pk):
    presupuesto = get_object_or_404(Presupuesto, pk=pk)
    # Optimización: select_related trae el ProductoServicio en la misma consulta SQL
    detalles = presupuesto.detalles.select_related('producto').all()

    form = DetallePresupuestoForm()
    form_info = PresupuestoInfoForm(instance=presupuesto)

    if request.method == "POST":
        if "guardar_info" in request.POST:
            form_info = PresupuestoInfoForm(request.POST, instance=presupuesto)
            if form_info.is_valid():
                form_info.save()
                return redirect("detalle_presupuesto", pk=presupuesto.id)

        elif "agregar_producto" in request.POST:
            form = DetallePresupuestoForm(request.POST)
            if form.is_valid():
                detalle = form.save(commit=False)
                detalle.presupuesto = presupuesto
                detalle.save()
                return redirect("detalle_presupuesto", pk=presupuesto.id)

    total = presupuesto.total

    return render(request, "core/presupuesto_detalle.html", {
        "presupuesto": presupuesto,
        "form": form,
        "form_info": form_info,
        "detalles": detalles,
        "total": total
    })

@login_required
def aumentar_precios_catalogo(request):
    if request.method == 'POST':
        porcentaje_str = request.POST.get('porcentaje', '10')
        try:
            porcentaje = float(porcentaje_str)
        except ValueError:
            porcentaje = 0

        if porcentaje != 0:
            factor = 1 + (porcentaje / 100)
            ProductoServicio.objects.all().update(precio_unitario=F('precio_unitario') * factor)
    
    # Corregido el nombre de la ruta de fallback a 'catalogo_list'
    return redirect(request.META.get('HTTP_REFERER', 'catalogo_list'))

@login_required
def presupuesto_pdf(request, pk):
    presupuesto = get_object_or_404(Presupuesto, pk=pk)
    detalles = presupuesto.detalles.select_related('producto').all()
    total = presupuesto.total

    # Obtenemos la ruta absoluta de la imagen en el sistema de archivos
    logo_path = finders.find('core/images/logo.png')
    
    # Si la encuentra, la convertimos a formato URI que WeasyPrint entiende perfectamente
    if logo_path:
        logo_url = f"file://{logo_path}"
    else:
        logo_url = ""

    html_string = render_to_string(
        "core/presupuesto_pdf.html",
        {
            "presupuesto": presupuesto,
            "detalles": detalles,
            "total": total,
            "logo_url": logo_url,  # Enviamos la ruta exacta al template
        }
    )

    pdf = HTML(string=html_string, base_url=request.build_absolute_uri('/')).write_pdf()
    
    response = HttpResponse(pdf, content_type="application/pdf")
    response["Content-Disposition"] = f'inline; filename="presupuesto_{presupuesto.folio}.pdf"'
    return response