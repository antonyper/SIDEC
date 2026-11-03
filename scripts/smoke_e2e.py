"""Smoke E2E de SIDEC contra la API publicada (por defecto vía el proxy /api del frontend).

Uso: python3 scripts/smoke_e2e.py BASE_URL ADMIN_USER ADMIN_PASSWORD

Crea datos con sufijo aleatorio: no correrlo contra una base con datos reales.
"""
import json
import sys
import time
import urllib.error
import urllib.request
from datetime import date

BASE, USER, PASSWORD = sys.argv[1].rstrip("/"), sys.argv[2], sys.argv[3]
SUFIJO = str(int(time.time()))[-6:]
fallos = []


def call(method, path, body=None, token=None, raw=False):
    data = json.dumps(body).encode() if body is not None else None
    req = urllib.request.Request(BASE + path, data=data, method=method)
    req.add_header("Content-Type", "application/json")
    if token:
        req.add_header("Authorization", f"Bearer {token}")
    try:
        with urllib.request.urlopen(req, timeout=60) as r:
            payload = r.read()
            return r.status, (payload if raw else (json.loads(payload) if payload else None)), r.headers
    except urllib.error.HTTPError as e:
        payload = e.read()
        try:
            return e.code, json.loads(payload), e.headers
        except ValueError:
            return e.code, payload[:200], e.headers


def check(nombre, cond, detalle=""):
    print(("OK   " if cond else "FAIL ") + nombre + (f"  -> {detalle}" if detalle and not cond else ""))
    if not cond:
        fallos.append(nombre)


st, _, _ = call("POST", "/auth/login", {"username": USER, "password": "incorrecta"})
check("login con contraseña incorrecta -> 401", st == 401, st)

st, login, _ = call("POST", "/auth/login", {"username": USER, "password": PASSWORD})
check("login ADMIN -> 200", st == 200, login)
tok = login["access_token"]

st, _, _ = call("GET", "/agencias")
check("API sin token -> 401", st == 401, st)

st, me, _ = call("GET", "/auth/me", token=tok)
check("/auth/me rol ADMIN", st == 200 and me["rol"] == "ADMIN", me)

st, ag, _ = call("POST", "/agencias", {"nombre": f"Agencia Smoke {SUFIJO}", "propietario": "Prueba", "ruta": "R1"}, tok)
check("crear agencia", st in (200, 201) and ag.get("id"), ag)
st, pr, _ = call("POST", "/productos", {"nombre": f"Diario Smoke {SUFIJO}", "categoria": "Diarios", "precio": 2.5}, tok)
check("crear producto", st in (200, 201) and pr.get("id"), pr)

hoy = date.today().isoformat()
st, mov, _ = call("POST", "/inventario/movimientos",
                  {"producto_id": pr["id"], "tipo": "STOCK_INICIAL", "cantidad": 100, "fecha": hoy}, tok)
check("stock inicial 100", st in (200, 201), mov)

st, num, _ = call("GET", "/guias/siguiente-numero", token=tok)
check("siguiente número de guía", st == 200, num)

st, guia, _ = call("POST", "/guias", {"fecha": hoy, "agencia_id": ag["id"], "detalles": [
    {"producto_id": pr["id"], "cantidad": 40, "precio": 2.5, "porcentaje_cobro": 80},
]}, tok)
check("crear guía con 1 detalle", st in (200, 201) and guia.get("id"), guia)
detalle_id = guia["detalles"][0]["id"]

st, inv, _ = call("GET", f"/inventario/{pr['id']}/movimientos", token=tok)
check("salida por guía registrada en inventario", st == 200 and "SALIDA_GUIA" in json.dumps(inv), inv)

# Regresión: un pago a cuenta mayor al monto se rechaza SIN dejar la liquidación guardada.
st, mala, _ = call("POST", "/liquidaciones", {"fecha": hoy, "guia_id": guia["id"], "pago_a_cuenta": 100000,
                                              "detalles": [{"detalle_guia_id": detalle_id, "cantidad_devuelta": 10}]}, tok)
check("pago a cuenta mayor al monto -> rechazado", st >= 400, (st, mala))
st, previas, _ = call("GET", f"/liquidaciones/por-guia/{guia['id']}", token=tok)
check("el rechazo no deja liquidación guardada", st == 200 and previas == [], previas)

st, liq, _ = call("POST", "/liquidaciones", {"fecha": hoy, "guia_id": guia["id"], "pago_a_cuenta": 10,
                                             "detalles": [{"detalle_guia_id": detalle_id, "cantidad_devuelta": 10}]}, tok)
check("crear liquidación (devuelve 10 de 40, pago a cuenta 10)", st in (200, 201) and liq.get("id"), liq)

st, cob, _ = call("GET", f"/cobranzas/liquidacion/{liq['id']}", token=tok)
# 30 vendidos x 2.5 x 80% = 60.00
check("cobranza automática: monto 60, pagado 10, PENDIENTE",
      st == 200 and float(cob["monto"]) == 60 and float(cob["monto_pagado"]) == 10 and cob["estado"] == "PENDIENTE", cob)

st, g2, _ = call("GET", f"/guias/{guia['id']}", token=tok)
check("guía pasa a LIQUIDADA (único detalle liquidado)", st == 200 and g2["estado"] == "LIQUIDADA", g2.get("estado"))

st, liq2, _ = call("POST", "/liquidaciones", {"fecha": hoy, "guia_id": guia["id"],
                                              "detalles": [{"detalle_guia_id": detalle_id, "cantidad_devuelta": 0}]}, tok)
check("no se puede liquidar dos veces el mismo detalle", st >= 400, (st, liq2))

st, cob2, _ = call("PUT", f"/cobranzas/{cob['id']}", {"monto_pagado": 60}, tok)
check("pago completo -> COBRADO", st == 200 and cob2["estado"] == "COBRADO", cob2)
st, cob3, _ = call("PUT", f"/cobranzas/{cob['id']}", {"monto_pagado": 61}, tok)
check("pago mayor al monto -> rechazado", st >= 400, (st, cob3))

for rep in ["/reportes/resumen-guias", "/reportes/deuda-pendiente", "/reportes/distribucion",
            "/reportes/ranking-agencias-venta", "/reportes/detalle-por-agencia", "/reportes/resumen-periodo",
            "/reportes/guias-pendientes", "/reportes/por-producto", "/reportes/agencias"]:
    st, body, _ = call("GET", rep, token=tok)
    check(f"reporte {rep}", st == 200, (st, body))

st, pdf, hdr = call("GET", "/reportes/detalle-por-agencia/pdf", token=tok, raw=True)
check("PDF detalle por agencia", st == 200 and isinstance(pdf, bytes) and pdf[:4] == b"%PDF", (st, hdr.get("content-type")))

op_user = f"op{SUFIJO}"
st, op, _ = call("POST", "/usuarios", {"nombre": "Operador Smoke", "username": op_user, "password": "Operador-123", "rol": "OPERADOR"}, tok)
check("ADMIN crea OPERADOR", st in (200, 201), op)
st, oplogin, _ = call("POST", "/auth/login", {"username": op_user, "password": "Operador-123"})
optok = oplogin["access_token"]
st, _, _ = call("GET", "/reportes/resumen-guias", token=optok)
check("OPERADOR no ve reportes -> 403", st == 403, st)
st, _, _ = call("GET", "/usuarios", token=optok)
check("OPERADOR no gestiona usuarios -> 403", st == 403, st)
st, _, _ = call("GET", "/guias", token=optok)
check("OPERADOR sí ve guías", st == 200, st)

st, an, _ = call("PATCH", f"/liquidaciones/{liq['id']}/anular", token=tok)
check("anular liquidación", st == 200 and an["estado"] == "ANULADA", an)
st, cob4, _ = call("GET", f"/cobranzas/liquidacion/{liq['id']}", token=tok)
check("cobranza anulada con la liquidación", st == 200 and cob4["estado"] == "ANULADA", cob4)
st, g3, _ = call("GET", f"/guias/{guia['id']}", token=tok)
check("guía vuelve a PENDIENTE_LIQUIDACION tras anular", st == 200 and g3["estado"] == "PENDIENTE_LIQUIDACION", g3.get("estado"))

print(f"\n{len(fallos)} fallos" + (": " + "; ".join(fallos) if fallos else ""))
sys.exit(1 if fallos else 0)
