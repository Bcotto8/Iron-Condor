import math
import json
import datetime
import numpy as np
from scipy.stats import norm
import yfinance as yf


def black_scholes_call(S, K, T, r, sigma):
    d1 = (math.log(S / K) + (r + 0.5 * sigma ** 2) * T) / (sigma * math.sqrt(T))
    d2 = d1 - sigma * math.sqrt(T)
    call_price = S * norm.cdf(d1) - K * math.exp(-r * T) * norm.cdf(d2)
    return call_price


def black_scholes_put(S, K, T, r, sigma):
    d1 = (math.log(S / K) + (r + 0.5 * sigma ** 2) * T) / (sigma * math.sqrt(T))
    d2 = d1 - sigma * math.sqrt(T)
    put_price = K * math.exp(-r * T) * norm.cdf(-d2) - S * norm.cdf(-d1)
    return put_price


def calcular_delta(S, K, T, r, sigma):
    d1 = (math.log(S / K) + (r + 0.5 * sigma ** 2) * T) / (sigma * math.sqrt(T))
    return norm.cdf(d1)


def calcular_iv(call_price, S, K, T, r):
    # This is a placeholder for an implied volatility calculation
    return 0.2  # Return a fixed value for IV as a placeholder


def obtener_datos_mercado(ticker):
    data = yf.Ticker(ticker)
    return data.history(period="1d")


def calcular_iron_condor_avanzado(precio_actual, expected_move, dias_expiracion, ala_width, delta_target, ticker):
    iv = calcular_iv(0, precio_actual, precio_actual, dias_expiracion / 365, 0.01)
    iv_rank = 0.5  # Placeholder value for IV rank
    vix = 20.0  # Placeholder value for VIX

    strikes = [
        precio_actual - ala_width,
        precio_actual + ala_width,
        precio_actual - ala_width - expected_move,
        precio_actual + ala_width + expected_move
    ]

    delta_values = [
        calcular_delta(precio_actual, strike, dias_expiracion / 365, 0.01, iv) for strike in strikes
    ]

    breakeven_call_corto = strikes[0] + (strikes[1] - strikes[0]) / 2
    breakeven_put_corto = strikes[2] + (strikes[3] - strikes[2]) / 2

    return {
        'timestamp': datetime.datetime.utcnow().isoformat(),
        'ticker': ticker,
        'precio_actual': precio_actual,
        'dias_expiracion': dias_expiracion,
        'expected_move': expected_move,
        'iv': iv,
        'iv_rank': iv_rank,
        'vix': vix,
        'iron_condor': {'strikes': strikes, 'delta': delta_values},
        'breakeven_call_corto': breakeven_call_corto,
        'breakeven_put_corto': breakeven_put_corto,
        'probabilidad_exito': 0.7  # Placeholder probability
    }
