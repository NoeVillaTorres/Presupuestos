import re
import pandas as pd
from django.core.management.base import BaseCommand
from core.models import ProductoServicio


class Command(BaseCommand):
    help = "Importa el catálogo INELECTRICA desde Excel"


    def handle(self, *args, **kwargs):
        df = pd.read_excel("catalogo.xlsx", header=None)

        categoria_actual = "GENERAL"

        for col in df.columns:
            for valor in df[col]:
                if not isinstance(valor, str):
                    continue

                texto = valor.strip()

                # Categorías (no tienen $)
                if "$" not in texto and len(texto) < 30:
                    categoria_actual = texto
                    continue

                # Productos (sí tienen $)
                match = re.search(r"\$\s*([\d\.]+)", texto)
                if match:
                    precio = match.group(1)
                    descripcion = texto.replace(match.group(0), "").strip("* ").strip()

                    ProductoServicio.objects.create(
                        categoria=categoria_actual,
                        descripcion=descripcion,
                        precio_unitario=precio
                    )

        self.stdout.write(self.style.SUCCESS("Catálogo importado correctamente"))
