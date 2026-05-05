COMPROBANTE1_CONFIG = {
    "template": "img/plantilla1.jpg",
    "output": "comprobante1_generado.png",
    "styles": {
        "nombre": {"size": 22, "color": "#200021", "pos": (50, 605)},
        "telefono": {"size": 22, "color": "#200021", "pos": (50, 780)},
        "valor1": {"size": 22, "color": "#200021", "pos": (50, 693)},
        "fecha": {"size": 22, "color": "#200021", "pos": (50, 865)},
        "referencia": {"size": 22, "color": "#200021", "pos": (50, 955)},
        "disponible": {"size": 22, "color": "#200021", "pos": (50, 1043)},
    },
    "font": "fuente/Manrope-Medium.ttf",
}

COMPROBANTE4_CONFIG = {
    "template": "img/plantilla4.jpg",
    "output": "comprobante4_generado.png",
    "styles": {
        "telefono": {"size": 22, "color": "#200021", "pos": (47, 262)},
        "valor1": {"size": 22, "color": "#200021", "pos": (47, 342)},
        "fecha": {"size": 22, "color": "#200021", "pos": (47, 423)},
        "referencia": {"size": 22, "color": "#200021", "pos": (47, 500)},
        "disponible": {"size": 22, "color": "#200021", "pos": (47, 580)},
    },
    "font": "fuente/Manrope-Medium.ttf"
}

COMPROBANTE_MOVIMIENTO_CONFIG = {
    "template": "img/comprobante_movimiento.jpg",
    "output": "comprobante_movimiento_generado.png",
    "styles": {
        "nombre": {"size": 18, "color": "#1b0b19", "pos": (87, 324), "font": "fuente/Manrope-Medium.ttf"},
        "valor1": {"size": 21, "color": "#D32F2F", "pos": (450, 333), "max_width": 200, "font": "fuente/Manrope-Bold.ttf"},
        "valor_decimal": {"size": 26, "color": "#D32F2F", "pos": (0, 0), "font": "fuente/Manrope-Bold.ttf"},
    },
    "font": "fuente/Manrope-Medium.ttf"
}

COMPROBANTE_QR_CONFIG = {
    "template": "img/plantilla_qr.jpg",
    "output": "comprobante_qr_generado.png",
    "styles": {
        "nombre": {"size": 22, "color": "#2e2b33", "pos": (48, 585)},
        "valor1": {"size": 22, "color": "#2e2b33", "pos": (48, 666)},
        "fecha": {"size": 22, "color": "#2e2b33", "pos": (48, 743)},
        "referencia": {"size": 22, "color": "#2e2b33", "pos": (48, 823)},
        "disponible": {"size": 22, "color": "#2e2b33", "pos": (48, 902)},
    },
    "font": "fuente/Manrope-Medium.ttf",
}

COMPROBANTE_NUEVO_CONFIG = {
    "template": "img/plantillakey.jpg",
    "output": "comprobante_nuevo_generado.png",
    "styles": {
        "nombre": {"size": 21, "color": "#200020", "pos": (48, 512)},
        "valor1": {"size": 21, "color": "#200020", "pos": (48, 825)},
        "llave": {"size": 21, "color": "#200020", "pos": (48, 590)},
        "banco": {"size": 21, "color": "#200020", "pos": (48, 670)},
        "numero_envia": {"size": 21, "color": "#200020", "pos": (46, 985)},
        "fecha": {"size": 21, "color": "#200020", "pos": (48, 748)},
        "referencia": {"size": 21, "color": "#200020", "pos": (48, 905)},
        "disponible": {"size": 21, "color": "#200020", "pos": (48, 1065)},
    },
    "font": "fuente/Manrope-Medium.ttf",
}

COMPROBANTE_AHORROS_CONFIG = {
    "template": "img/p.jpg",
    "output": "comprobante_ahorros_generado.png",
    "styles": {
        "nombre": {"size": 24, "color": "#FFFFFF", "pos": (45, 825), "font": "fuente/cibfontsans_bold.ttf"},
        "numero_cuenta": {"size": 21, "color": "#FFFFFF", "pos": (45, 876), "font": "fuente/OpenSans-Semibold.ttf"},
        "valor": {"size": 26, "color": "#FFFFFF", "pos": (45, 559), "font": "fuente/cibfontsans_bold.ttf"},
        "fecha": {"size": 19, "color": "#FFFFFF", "pos": (190, 360), "font": "fuente/opensans_regular.ttf"},
    },
    "font": "fuente/cibfontsans_bold.ttf",
}

COMPROBANTE_DAVIPLATA_CONFIG = {
    "template": "img/daviplata.jpg",
    "output": "comprobante_daviplata_generado.png",
    "styles": {
        "nombre": {"size": 22, "color": "#333333", "pos": (90, 650), "font": "fuente/Manrope-Bold.ttf"},
        "recibe": {"size": 22, "color": "#333333", "pos": (273, 960), "font": "fuente/Manrope-Bold.ttf"},
        "valor": {"size": 32, "color": "#333333", "pos": (111, 828), "font": "fuente/Manrope-Bold.ttf"},
        "envia": {"size": 22, "color": "#333333", "pos": (155, 676), "font": "fuente/Manrope-Bold.ttf"},
        "fecha": {"size": 22, "color": "#333333", "pos": (84, 1143), "font": "fuente/Manrope-Bold.ttf"},
        "aprobacion": {"size": 22, "color": "#333333", "pos": (88, 1230), "font": "fuente/Manrope-Bold.ttf"},
    },
    "font": "fuente/Manrope-Bold.ttf",
}

# CONFIGURACIONES DE MOVIMIENTOS (Ajustado a carpeta 'img' si mov bancol no existe como carpeta separada)
MOVIMIENTO_BC_AHORROS_CONFIG = {
    "template": "img/ahorros.jpg", 
    "output": "movimiento_bc_ahorros_generado.png",
    "styles": {
        "valor": {"size": 23, "color": "#F2879E", "pos": (532, 716)},
        "fecha": {"size": 18, "color": "#FFFFFF", "pos": (25, 643), "font": "fuente/OpenSans-Bold.ttf"},
        "nombre": {"size": 23, "color": "#FFFFFF", "pos": (197, 667), "font": "fuente/OpenSans-Light.ttf"},
    },
    "font": "fuente/CIBFontSans-Bold.ttf"
}
