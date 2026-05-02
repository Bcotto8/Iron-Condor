import numpy as np
from scipy.optimize import brentq
from scipy.stats import norm

class IronCondor:
    def __init__(self, strikes, premiums, delta_target):
        self.strikes = strikes
        self.premiums = premiums
        self.delta_target = delta_target

    def implied_volatility(self, market_price, strike, expiry, interest_rate=0.01):
        def objective_function(vol):
            return black_scholes_price(strike, market_price, vol, expiry, interest_rate) - market_price
        # Using Brent's method to find the implied volatility
        return brentq(objective_function, 0.0001, 10)

    def breakeven(self):
        return self.strikes[0] + self.premiums[0] - self.premiums[1], self.strikes[2] + self.premiums[2] - self.premiums[3]

    def max_profit(self):
        return sum(self.premiums)

    def max_loss(self):
        return (self.strikes[2] - self.strikes[0]) - sum(self.premiums)

    def calculate_delta(self):
        # Calculate delta for each option in the iron condor
        deltas = []
        for strike, premium in zip(self.strikes, self.premiums):
            d1 = (np.log(100 / strike) + 0.01 * 0.25) / (0.2 * np.sqrt(0.25))
            delta = norm.cdf(d1)
            deltas.append(delta)
        return deltas

    def validate_parameters(self):
        assert all(isinstance(x, (int, float)) for x in self.strikes), 'Strikes must be numeric.'
        assert all(isinstance(x, (int, float)) for x in self.premiums), 'Premiums must be numeric.'
        assert len(self.strikes) == 4, 'Iron Condor requires 4 strikes.'
        assert len(self.premiums) == 4, 'Iron Condor requires 4 premiums.'

    def option_strategy(self):
        self.validate_parameters()
        # Calculate key metrics for the Iron Condor strategy
        profit = self.max_profit()
        loss = self.max_loss()
        breakeven = self.breakeven()
        deltas = self.calculate_delta()
        
        return {
            'max_profit': profit,
            'max_loss': loss,
            'breakeven_points': breakeven,
            'deltas': deltas
        }

def black_scholes_price(S, K, sigma, T, r):
    # Black-Scholes model for option pricing
    # S: Spot price, K: Strike price, sigma: Volatility, T: Time to expiry, r: Interest rate
    if T <= 0 or sigma <= 0:
        return max(S - K, 0)
    
    d1 = (np.log(S / K) + (r + 0.5 * sigma ** 2) * T) / (sigma * np.sqrt(T))
    d2 = d1 - sigma * np.sqrt(T)
    call_price = S * norm.cdf(d1) - K * np.exp(-r * T) * norm.cdf(d2)
    return call_price

# Example usage
if __name__ == "__main__":
    # Define Iron Condor parameters
    strikes = [95, 100, 105, 110]  # Put spread and Call spread strikes
    premiums = [0.5, -0.2, -0.2, 0.5]  # Premium received/paid for each option
    delta_target = 0.15
    
    # Create Iron Condor instance
    ic = IronCondor(strikes, premiums, delta_target)
    
    # Get strategy metrics
    metrics = ic.option_strategy()
    
    print("Iron Condor Strategy Analysis")
    print("=" * 50)
    print(f"Strikes: {ic.strikes}")
    print(f"Premiums: {ic.premiums}")
    print(f"Max Profit: ${metrics['max_profit']:.2f}")
    print(f"Max Loss: ${metrics['max_loss']:.2f}")
    print(f"Breakeven Points: {metrics['breakeven_points']}")
    print(f"Deltas: {[f'{d:.4f}' for d in metrics['deltas']]}")
    
    # Test Black-Scholes pricing
    print("\n" + "=" * 50)
    print("Black-Scholes Option Pricing Test")
    print("=" * 50)
    S = 100  # Spot price
    K = 100  # Strike price
    sigma = 0.2  # Volatility (20%)
    T = 0.25  # 3 months to expiry
    r = 0.01  # Interest rate (1%)
    
    call_price = black_scholes_price(S, K, sigma, T, r)
    print(f"Spot Price: ${S}")
    print(f"Strike Price: ${K}")
    print(f"Volatility: {sigma*100}%")
    print(f"Time to Expiry: {T} years")
    print(f"Interest Rate: {r*100}%")
    print(f"Call Option Price: ${call_price:.4f}")