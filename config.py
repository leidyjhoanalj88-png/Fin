# Asegúrate de que estas configuraciones existan y usen 'img/bc.png'
COMPROBANTE_NEQUI_BC_CONFIG = {
    "template": "img/bc.png",  # <--- Cambiado de 'nequi_template.png' a 'img/bc.png'
    "output": "comprobante_nequi_bc_generado.png",
    "styles": {
        "nombre": {"size": 22, "color": "#200021", "pos": (48, 562)},
        "valor": {"size": 22, "color": "#200021", "pos": (48, 652)},
        "fecha": {"size": 22, "color": "#200021", "pos": (48, 732)},
        "banco": {"size": 22, "color": "#200021", "pos": (48, 813)},
        "numero_cuenta": {"size": 22, "color": "#200021", "pos": (48, 897)},
        "referencia": {"size": 22, "color": "#200021", "pos": (48, 979)},
        "disponible": {"size": 22, "color": "#200021", "pos": (48, 1065)},
    },
    "font": "fuente/Manrope-Medium.ttf"
}

# Repite lo mismo para Nequi Ahorros
COMPROBANTE_NEQUI_AHORROS_CONFIG = {
    "template": "img/bc.png", # <--- Siempre con el prefijo 'img/'
    "output": "comprobante_nequi_ahorros_generado.png",
    "styles": {
        "nombre": {"size": 22, "color": "#200021", "pos": (48, 562)},
        "valor": {"size": 22, "color": "#200021", "pos": (48, 652)},
        "fecha": {"size": 22, "color": "#200021", "pos": (48, 732)},
        "banco": {"size": 22, "color": "#200021", "pos": (48, 813)},
        "numero_cuenta": {"size": 22, "color": "#200021", "pos": (48, 897)},
        "referencia": {"size": 22, "color": "#200021", "pos": (48, 979)},
        "disponible": {"size": 22, "color": "#200021", "pos": (48, 1065)},
    },
    "font": "fuente/Manrope-Medium.ttf"
}
