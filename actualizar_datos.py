#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de extracción y cálculo financiero para Ruta Capital Asesores de Inversión.
Proyecto de aula — Mercado de Capitales — UNIPAZ (Barrancabermeja, Colombia).

Descarga 3 años de datos históricos diarios desde Yahoo Finance (yfinance) para
las 8 acciones seleccionadas de la Bolsa de Valores de Colombia (BVC) y la TRM
(USDCOP=X), calcula indicadores de rentabilidad, volatilidad, caída máxima y
rendimiento por dividendos, y genera el archivo 'datos.json'.
"""

import json
import math
import os
import sys
from datetime import datetime, timezone

import numpy as np
import pandas as pd
import yfinance as yf


# ==============================================================================
# 1. CONFIGURACIÓN DE ACCIONES DE LA BVC Y CONSTANTES DEL SCRIPT
# ==============================================================================
ACCIONES_BVC = [
    {
        "ticker": "ECOPETROL.CL",
        "nombre": "Ecopetrol",
        "nemotecnico": "ECOPETROL",
        "sector": "Petróleo y gas",
    },
    {
        "ticker": "PFCIBEST.CL",
        "nombre": "Grupo Cibest preferencial",
        "nemotecnico": "PFCIBEST",
        "sector": "Financiero",
    },
    {
        "ticker": "CIBEST.CL",
        "nombre": "Grupo Cibest ordinaria",
        "nemotecnico": "CIBEST",
        "sector": "Financiero",
    },
    {
        "ticker": "ISA.CL",
        "nombre": "ISA",
        "nemotecnico": "ISA",
        "sector": "Energía e infraestructura",
    },
    {
        "ticker": "EXITO.CL",
        "nombre": "Grupo Éxito",
        "nemotecnico": "EXITO",
        "sector": "Comercio",
    },
    {
        "ticker": "PFAVAL.CL",
        "nombre": "Grupo Aval preferencial",
        "nemotecnico": "PFAVAL",
        "sector": "Financiero",
    },
    {
        "ticker": "GEB.CL",
        "nombre": "Grupo Energía Bogotá",
        "nemotecnico": "GEB",
        "sector": "Energía",
    },
    {
        "ticker": "CELSIA.CL",
        "nombre": "Celsia",
        "nemotecnico": "CELSIA",
        "sector": "Energía",
    },
]

ARCHIVO_SALIDA = "datos.json"
FUENTE_TEXTO = (
    "Yahoo Finance (yfinance); rentabilidades con precio ajustado por dividendos"
)


# ==============================================================================
# 2. FUNCIONES DE CÁLCULO FINANCIERO Y DESCARGA
# ==============================================================================
def obtener_trm() -> dict | None:
    """
    Intenta descargar la TRM oficial aproximada desde Yahoo Finance ('USDCOP=X').
    Retorna un diccionario {'valor': float, 'fecha': 'AAAA-MM-DD'} o None si falla.
    """
    try:
        hist_trm = yf.Ticker("USDCOP=X").history(period="5d", auto_adjust=False)
        if hist_trm is None or hist_trm.empty or "Close" not in hist_trm.columns:
            return None

        closes = hist_trm["Close"].dropna()
        if closes.empty:
            return None

        ultimo_valor = float(closes.iloc[-1])
        ultima_fecha = closes.index[-1].strftime("%Y-%m-%d")

        if math.isnan(ultimo_valor) or ultimo_valor <= 0:
            return None

        return {
            "valor": round(ultimo_valor, 2),
            "fecha": ultima_fecha,
        }
    except Exception as exc:
        print(f"[AVISO] No se pudo obtener la TRM (USDCOP=X): {exc}")
        return None


def procesar_accion(info_accion: dict) -> dict:
    """
    Descarga el historial de 3 años de una acción y calcula todas las métricas
    solicitadas. Lanza ValueError si los datos son insuficientes o inválidos.
    """
    ticker = info_accion["ticker"]
    df = yf.Ticker(ticker).history(period="3y", auto_adjust=False)

    if df is None or df.empty:
        raise ValueError("Yahoo Finance devolvió una tabla vacía.")

    for col in ("Close", "Adj Close"):
        if col not in df.columns:
            raise ValueError(f"Falta la columna obligatoria '{col}'.")

    # Normalizar el índice de fechas sin zona horaria para cálculos exactos
    df = df.copy()
    if getattr(df.index, "tz", None) is not None:
        df.index = df.index.tz_localize(None)
    df = df.sort_index()

    # Filtrar filas donde Close o Adj Close sean nulos
    df_precios = df.dropna(subset=["Close", "Adj Close"])
    if len(df_precios) < 2:
        raise ValueError("Menos de 2 días válidos de negociación disponibles.")

    # 1. Precio actual y fecha del último cierre
    ultimo_close = float(df_precios["Close"].iloc[-1])
    close_anterior = float(df_precios["Close"].iloc[-2])
    fecha_ultima_dt = df_precios.index[-1]
    fecha_ultima_str = fecha_ultima_dt.strftime("%Y-%m-%d")

    if ultimo_close <= 0 or close_anterior <= 0:
        raise ValueError("Precios de cierre inválidos (<= 0).")

    # 2. Variación diaria (%)
    variacion_dia_pct = ((ultimo_close / close_anterior) - 1.0) * 100.0

    # 3. Rentabilidad 1 año con Adj Close (fecha más cercana a hace 365 días)
    adj_ultimo = float(df_precios["Adj Close"].iloc[-1])
    fecha_objetivo_1a = fecha_ultima_dt - pd.Timedelta(days=365)

    # Buscar el índice con la diferencia absoluta mínima respecto a hace 1 año
    diferencias_dias = np.abs((df_precios.index - fecha_objetivo_1a).days)
    idx_1a = int(np.argmin(diferencias_dias))
    adj_hace_1a = float(df_precios["Adj Close"].iloc[idx_1a])

    if adj_hace_1a <= 0:
        raise ValueError("Adj Close de referencia a 1 año inválido (<= 0).")

    rent_1a_pct = ((adj_ultimo / adj_hace_1a) - 1.0) * 100.0

    # 4. Rentabilidad anual promedio 3 años (CAGR con fechas reales)
    adj_primero = float(df_precios["Adj Close"].iloc[0])
    fecha_primera_dt = df_precios.index[0]
    dias_transcurridos = (fecha_ultima_dt - fecha_primera_dt).days

    if adj_primero <= 0 or dias_transcurridos <= 0:
        raise ValueError("Datos insuficientes para calcular rentabilidad anual a 3 años.")

    anios_transcurridos = dias_transcurridos / 365.25
    rent_anual_3a_pct = (
        ((adj_ultimo / adj_primero) ** (1.0 / anios_transcurridos)) - 1.0
    ) * 100.0

    # 5. Subconjunto del último año (últimos 365 días calendario)
    df_1a = df_precios[df_precios.index >= fecha_objetivo_1a]
    if len(df_1a) < 2:
        df_1a = df_precios.iloc[-min(len(df_precios), 252) :]

    # Volatilidad anual (%) = std(log returns diarios 1a) * sqrt(252)
    adj_1a_series = df_1a["Adj Close"]
    log_returns = np.log(adj_1a_series / adj_1a_series.shift(1)).dropna()
    if len(log_returns) >= 2:
        volatilidad_anual_pct = float(log_returns.std(ddof=1) * math.sqrt(252)) * 100.0
    else:
        volatilidad_anual_pct = 0.0

    # 6. Caída máxima en 1 año (Max Drawdown negativo desde máximo previo)
    max_acumulado_1a = adj_1a_series.cummax()
    drawdowns_1a = (adj_1a_series / max_acumulado_1a) - 1.0
    caida_maxima_1a_pct = float(drawdowns_1a.min()) * 100.0
    if caida_maxima_1a_pct > 0:
        caida_maxima_1a_pct = 0.0

    # 7. Rendimiento por dividendo (%) = suma de Dividends últimos 365 días / precio
    if "Dividends" in df.columns:
        div_1a = df.loc[df.index >= fecha_objetivo_1a, "Dividends"].fillna(0.0)
        suma_dividendos_1a = float(div_1a.sum())
    else:
        suma_dividendos_1a = 0.0

    dividendo_rend_pct = (suma_dividendos_1a / ultimo_close) * 100.0

    # 8. Histórico mensual: último Close de cada mes de los 3 años
    cierre_mensual = df_precios["Close"].resample("ME").last().dropna()
    historico_mensual = [
        {
            "mes": fecha_mes.strftime("%Y-%m"),
            "cierre": round(float(valor_cierre), 2),
        }
        for fecha_mes, valor_cierre in cierre_mensual.items()
    ]

    return {
        "ticker": ticker,
        "nombre": info_accion["nombre"],
        "nemotecnico": info_accion["nemotecnico"],
        "sector": info_accion["sector"],
        "moneda": "COP",
        "precio": round(ultimo_close, 2),
        "fecha": fecha_ultima_str,
        "variacion_dia_pct": round(variacion_dia_pct, 2),
        "rent_1a_pct": round(rent_1a_pct, 2),
        "rent_anual_3a_pct": round(rent_anual_3a_pct, 2),
        "volatilidad_anual_pct": round(volatilidad_anual_pct, 2),
        "caida_maxima_1a_pct": round(caida_maxima_1a_pct, 2),
        "dividendo_rend_pct": round(dividendo_rend_pct, 2),
        "historico": historico_mensual,
    }


# ==============================================================================
# 3. ORQUESTACIÓN PRINCIPAL Y GUARDADO SEGURO DE datos.json
# ==============================================================================
def main() -> int:
    print("=== Ruta Capital Asesores de Inversión — Actualizador de Datos BVC ===")
    marca_tiempo_utc = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

    # Descargar TRM (si falla, conserva None -> null en JSON)
    trm_data = obtener_trm()
    if trm_data:
        print(f"[OK] TRM obtenida: $ {trm_data['valor']} ({trm_data['fecha']})")
    else:
        print("[AVISO] TRM no disponible; se registrará como null.")

    acciones_exitosas = []
    errores_registro = []

    # Procesar cada acción de manera independiente para garantizar resiliencia
    for item in ACCIONES_BVC:
        ticker = item["ticker"]
        try:
            datos_accion = procesar_accion(item)
            acciones_exitosas.append(datos_accion)
            print(
                f"[OK] {ticker:<13} | Precio: {datos_accion['precio']:>10,.2f} COP | "
                f"Rent 3a: {datos_accion['rent_anual_3a_pct']:>6.2f}%"
            )
        except Exception as exc:
            motivo = str(exc).strip() or exc.__class__.__name__
            errores_registro.append({"ticker": ticker, "motivo": motivo})
            print(f"[ERROR] {ticker:<13} -> {motivo}")

    print("\n----------------------------------------------------------------------")
    print(
        f"Resumen de ejecución: {len(acciones_exitosas)} de {len(ACCIONES_BVC)} "
        f"acciones actualizadas."
    )
    if errores_registro:
        fallidas_str = ", ".join(
            f"{e['ticker']} ({e['motivo']})" for e in errores_registro
        )
        print(f"Acciones que fallaron: {fallidas_str}")
    else:
        print("Acciones que fallaron: Ninguna.")

    # Si TODAS fallaron, no sobrescribir datos.json
    if len(acciones_exitosas) == 0:
        if os.path.exists(ARCHIVO_SALIDA):
            print(
                f"[AVISO CRÍTICO] Todas las acciones fallaron. Se conserva el archivo "
                f"'{ARCHIVO_SALIDA}' anterior sin modificaciones."
            )
        else:
            print(
                f"[AVISO CRÍTICO] Todas las acciones fallaron y no existe un "
                f"'{ARCHIVO_SALIDA}' previo. No se creó ningún archivo."
            )
        return 0

    # Construir estructura exacta de datos.json
    salida_json = {
        "actualizado": marca_tiempo_utc,
        "fuente": FUENTE_TEXTO,
        "trm": trm_data,
        "acciones": acciones_exitosas,
        "errores": errores_registro,
    }

    try:
        with open(ARCHIVO_SALIDA, "w", encoding="utf-8") as archivo:
            json.dump(salida_json, archivo, ensure_ascii=False, indent=2)
        print(f"[OK] Archivo '{ARCHIVO_SALIDA}' guardado correctamente.")
    except Exception as exc:
        print(f"[AVISO] No se pudo escribir '{ARCHIVO_SALIDA}': {exc}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
