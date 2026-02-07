from django.shortcuts import render, redirect, get_object_or_404
from .models import ProductoServicio, Presupuesto, DetallePresupuesto
from .forms import ProductoForm, DetallePresupuestoForm, PresupuestoInfoForm
from django.template.loader import render_to_string
from django.http import HttpResponse
from weasyprint import HTML
from django.db.models import Q
# Create your views here.


def index(request):
    return render(request, "core/index.html")

def catalogo_list(request):
    query = request.GET.get('q', '')
    productos = ProductoServicio.objects.all()
    
    if query:
        productos = productos.filter(descripcion__icontains=query)

    # Si la petición trae este encabezado, solo devolvemos las filas de la tabla
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        html = render_to_string('core/partials/catalogo_rows.html', {'productos': productos})
        return HttpResponse(html)

    return render(request, 'core/catalogo.html', {'productos': productos, 'query': query})

def catalogo_eliminar(request, pk):
    producto = get_object_or_404(ProductoServicio, pk=pk)
    if request.method == 'POST':
        producto.delete()
    return redirect('catalogo_list')

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


def crear_presupuesto(request):
    presupuesto = Presupuesto.objects.create()
    return redirect("detalle_presupuesto", pk=presupuesto.id)


def detalle_presupuesto(request, pk):
    presupuesto = get_object_or_404(Presupuesto, pk=pk)
    detalles = presupuesto.detalles.all()

    # Inicializamos ambos formularios
    form = DetallePresupuestoForm()
    form_info = PresupuestoInfoForm(instance=presupuesto)

    if request.method == "POST":
        # CASO 1: Se presionó el botón de actualizar datos del cliente/proyecto
        if "guardar_info" in request.POST:
            form_info = PresupuestoInfoForm(request.POST, instance=presupuesto)
            if form_info.is_valid():
                form_info.save()
                return redirect("detalle_presupuesto", pk=presupuesto.id)

        # CASO 2: Se presionó el botón de agregar producto (el que ya tenías)
        elif "agregar_producto" in request.POST:
            form = DetallePresupuestoForm(request.POST)
            if form.is_valid():
                detalle = form.save(commit=False)
                detalle.presupuesto = presupuesto
                detalle.save()
                return redirect("detalle_presupuesto", pk=presupuesto.id)

    total = presupuesto.total # Usamos la @property que definimos en el modelo

    return render(request, "core/presupuesto_detalle.html", {
        "presupuesto": presupuesto,
        "form": form,
        "form_info": form_info, # Enviamos el nuevo form al template
        "detalles": detalles,
        "total": total
    })

def presupuesto_pdf(request, pk):
    presupuesto = get_object_or_404(Presupuesto, pk=pk)
    detalles = presupuesto.detalles.all()
    total = presupuesto.total

    html_string = render_to_string(
        "core/presupuesto_pdf.html",
        {
            "presupuesto": presupuesto,
            "detalles": detalles,
            "total": total,
        }
    )

    #pdf = HTML(string=html_string).write_pdf()
    pdf = HTML(string=html_string, base_url=request.build_absolute_uri()).write_pdf()
    response = HttpResponse(pdf, content_type="application/pdf")
    response["Content-Disposition"] = (
        f'attachment; filename="presupuesto_{presupuesto.folio}.pdf"'
    )
    return response






