from django import forms
from .models import ProductoServicio, Presupuesto, DetallePresupuesto

class ProductoForm(forms.ModelForm):

    categoria = forms.ChoiceField(
        choices=[],
        required=False,
        widget=forms.Select()
    )

    categoria_nueva = forms.CharField(
        required=False,
        label="Nueva categoría",
        widget=forms.TextInput()
    )

    class Meta:
        model = ProductoServicio
        fields = ["descripcion", "categoria", "categoria_nueva", "precio_unitario"]
        widgets = {
            "descripcion": forms.TextInput(),
            "precio_unitario": forms.NumberInput(),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        base_classes = (
            "w-full bg-transparent border border-zinc-700 rounded-md "
            "px-3 py-2 text-sm text-zinc-100 "
            "focus:outline-none focus:ring-2 focus:ring-blue-600"
        )

        select_classes = (
            base_classes +
            " bg-zinc-900 text-zinc-100"
        )

        self.fields["categoria"].widget.attrs["class"] = select_classes


        for field in self.fields.values():
            field.widget.attrs.update({
                "class": base_classes
            })

        self.fields["categoria_nueva"].widget.attrs.update({
            "placeholder": "Escribe una nueva categoría"
        })

        categorias = (
            ProductoServicio.objects
            .values_list("categoria", flat=True)
            .distinct()
            .order_by("categoria")
        )

        self.fields["categoria"].choices = [
            ("", "— Selecciona una categoría —")
        ] + [(c, c) for c in categorias if c]



class DetallePresupuestoForm(forms.ModelForm):
    # Definimos explícitamente el campo como IntegerField para evitar decimales
    cantidad = forms.IntegerField(
        min_value=1,
        widget=forms.NumberInput(attrs={
            'class': 'w-full rounded-md bg-gray-900 text-gray-100 border border-gray-700 focus:ring-2 focus:ring-indigo-500 focus:outline-none',
            'step': '1',  # Esto evita que las flechas del input usen decimales
            'oninput': "this.value = Math.round(this.value);" # Truco extra: redondea si pegan un valor
        })
    )

    class Meta:
        model = DetallePresupuesto
        fields = ["producto", "cantidad", "unidad"]

        widgets = {
            'producto': forms.Select(attrs={
                'class': 'w-full rounded-md bg-gray-900 text-gray-100 border border-gray-700 focus:ring-2 focus:ring-indigo-500 focus:outline-none'
            }),
            'unidad': forms.TextInput(attrs={
                'class': 'w-full rounded-md bg-gray-900 text-gray-100 border border-gray-700 focus:ring-2 focus:ring-indigo-500 focus:outline-none',
                'placeholder': 'PZA, MT, SERVICIO...'
            })
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["producto"].queryset = ProductoServicio.objects.all()
        self.initial['unidad'] = 'PZA'


class PresupuestoInfoForm(forms.ModelForm):
    class Meta:
        model = Presupuesto
        fields = ['proyecto', 'cliente_nombre', 'cliente_direccion', 'cliente_ciudad', 'cliente_cp']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Reutilizamos tus clases de diseño para mantener la estética
        base_classes = (
            "w-full bg-transparent border border-zinc-700 rounded-md "
            "px-3 py-2 text-sm text-zinc-100 "
            "focus:outline-none focus:ring-2 focus:ring-blue-600"
        )
        for field in self.fields.values():
            field.widget.attrs.update({"class": base_classes})