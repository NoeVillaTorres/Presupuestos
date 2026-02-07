# core/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path("", views.index, name="index"),

    path("catalogo/", views.catalogo_list, name="catalogo_list"),
    path("catalogo/nuevo/", views.catalogo_form, name="catalogo_nuevo"),
    path("catalogo/<int:pk>/editar/", views.catalogo_form, name="catalogo_editar"),

    path("presupuesto/nuevo/", views.crear_presupuesto, name="crear_presupuesto"),
    path("presupuesto/<int:pk>/", views.detalle_presupuesto, name="detalle_presupuesto"),
    path("presupuesto/<int:pk>/pdf/", views.presupuesto_pdf, name="presupuesto_pdf"),
    path('catalogo/eliminar/<int:pk>/', views.catalogo_eliminar, name='catalogo_eliminar'),
]

