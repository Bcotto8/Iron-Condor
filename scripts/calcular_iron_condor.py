import math
import json
import datetime
from scipy.stats import norm
from scipy.optimize import brentq
import yfinance as yf

def black_scholes_call(S, K, T, r, sigma):
    # Validar que T sea mayor que 0 para evitar división por cero
    if T <= 0 or sigma <= 0:
        return max(S - K, 0)
    
    d1 = (math.log(S / K) + (r + 0.5 * sigma ** 2) * T) / (sigma * math.sqrt(T))
    d2 = d1 - sigma * math.sqrt(T)
    call_price = S * norm.cdf(d1) - K * math.exp(-r * T) * norm.cdf(d2)
    return call_price

def black_scholes_put(S, K, T, r, sigma):
    # Validar que T sea mayor que 0 para evitar división por cero
    if T <= 0 or sigma <= 0:
        return max(K - S, 0)
    
    d1 = (math.log(S / K) + (r + 0.5 * sigma ** 2) * T) / (sigma * math.sqrt(T))
    d2 = d1 - sigma * math.sqrt(T)
    put_price = K * math.exp(-r * T) * norm.cdf(-d2) - S * norm.cdf(-d1)
    return put_price

def calcular_delta(S, K, T, r, sigma):
    if T <= 0 or sigma <= 0:
        if S > K:
            return 1.0
        else:
            return 0.0
    
    d1 = (math.log(S / K) + (r + 0.5 * sigma ** 2) * T) / (sigma * math.sqrt(T))
    return norm.cdf(d1)

def calcular_iv(call_price, S, K, T, r, initial_guess=0.2):
    """Calcula la volatilidad implícita usando el método de Newton-Raphson"""
    if T <= 0:
        return initial_guess
    
    def objective(sigma):
        return black_scholes_call(S, K, T, r, sigma) - call_price
    
    try:
        # Usar brentq para encontrar la raíz de manera robusta
        iv = brentq(objective, 0.001, 3.0)
        return iv
    except ValueError:
        # Si no se encuentra una solución, retornar el valor inicial
        return initial_guess

def obtener_datos_mercado(ticker):
    data = yf.Ticker(ticker)
    return data.history(period="1d")

def calcular_iron_condor_avanzado(precio_actual, expected_move, dias_expiracion, ala_width, delta_target, ticker):
    """
    Calcula las métricas avanzadas del Iron Condor
    
    Args:
        precio_actual: Precio actual del activo subyacente
        expected_move: Movimiento esperado del precio
        dias_expiracion: Días hasta la expiración
        ala_width: Ancho entre strikes de call/put
        delta_target: Delta objetivo para las alas (0-1)
        ticker: Símbolo del ticker
    """
    T = dias_expiracion / 365.0
    r = 0.01  # Tasa de interés sin riesgo
    
    # Validar que delta_target esté en rango válido
    if not (0 < delta_target < 1):
        delta_target = 0.25  # Valor por defecto
    
    # Obtener datos de mercado para mejorar estimaciones (opcional)
    # market_data = obtener_datos_mercado(ticker)
    
    iv = calcular_iv(10, precio_actual, precio_actual, T, r)  # Estimar IV
    iv_rank = 0.5  # Placeholder value for IV rank
    vix = 20.0  # Placeholder value for VIX

    # Definir los strikes del Iron Condor
    short_call_strike = precio_actual + ala_width
    long_call_strike = precio_actual + ala_width + expected_move
    short_put_strike = precio_actual - ala_width
    long_put_strike = precio_actual - ala_width - expected_move

    strikes = [
        long_put_strike,
        short_put_strike,
        short_call_strike,
        long_call_strike
    ]

    # Calcular deltas para cada strike
    delta_values = [
        calcular_delta(precio_actual, strike, T, r, iv) for strike in strikes
    ]

    # Calcular precios de las opciones
    short_call_price = black_scholes_call(precio_actual, short_call_strike, T, r, iv)
    long_call_price = black_scholes_call(precio_actual, long_call_strike, T, r, iv)
    short_put_price = black_scholes_put(precio_actual, short_put_strike, T, r, iv)
    long_put_price = black_scholes_put(precio_actual, long_put_strike, T, r, iv)

    # Calcular breakeven correctamente
    # Breakeven call = strike corto + (prima neta recibida)
    prima_call_spread = short_call_price - long_call_price
    prima_put_spread = short_put_price - long_put_price
    prima_neta = prima_call_spread + prima_put_spread

    breakeven_call = short_call_strike + prima_neta
    breakeven_put = short_put_strike - prima_neta

    # Calcular probabilidad de éxito (simplificada)
    prob_success = (norm.cdf(long_call_strike, precio_actual, precio_actual * iv * math.sqrt(T)) -
                    norm.cdf(long_put_strike, precio_actual, precio_actual * iv * math.sqrt(T)))

    return {
        'timestamp': datetime.datetime.utcnow().isoformat(),
        'ticker': ticker,
        'precio_actual': precio_actual,
        'dias_expiracion': dias_expiracion,
        'expected_move': expected_move,
        'iv': iv,
        'iv_rank': iv_rank,
        'vix': vix,
        'delta_target': delta_target,
        'iron_condor': {
            'strikes': strikes,
            'delta': delta_values,
            'long_put_strike': long_put_strike,
            'short_put_strike': short_put_strike,
            'short_call_strike': short_call_strike,
            'long_call_strike': long_call_strike
        },
        'premios': {
            'short_call_price': short_call_price,
            'long_call_price': long_call_price,
            'short_put_price': short_put_price,
            'long_put_price': long_put_price,
            'prima_neta': prima_neta
        },
        'breakeven_call': breakeven_call,
        'breakeven_put': breakeven_put,
        'probabilidad_exito': min(prob_success, 0.99) if prob_success > 0 else 0.5
    }