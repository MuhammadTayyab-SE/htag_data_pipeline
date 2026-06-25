from .market_cycle import load_transform_save_market_cycle
from .market_demand import load_transform_save_market_demand
from .market_fundamentals import load_transform_save_market_fundamentals
from .market_growth_cumulative import load_transform_save_market_growth_cumulative
from .market_risk import load_transform_save_market_risk
from .market_scores import load_transform_save_market_scores
from .market_supply import load_transform_save_market_supply
from .market_supply_ls import load_transform_save_market_supply_ls
from .market_supply_ss import load_transform_save_market_supply_ss
from .market_trends_demand_profile import load_transform_save_market_trends_demand_profile
from .market_trends_growth_rates import load_transform_save_market_trends_growth_rates
from .market_trends_price import load_transform_save_market_trends_price
from .market_trends_rent import load_transform_save_market_trends_rent
from .market_trends_years_to_own import load_transform_save_market_trends_years_to_own
from .market_trends_yield import load_transform_save_market_trends_yield


MARKET_ENDPOINT_TRANSFORMERS = {
    "/markets/trends/price": load_transform_save_market_trends_price,
    "/markets/trends/rent": load_transform_save_market_trends_rent,
    "/markets/trends/yield": load_transform_save_market_trends_yield,
    "/markets/trends/growth-rates": load_transform_save_market_trends_growth_rates,
    "/markets/trends/years-to-own": load_transform_save_market_trends_years_to_own,
    "/markets/trends/demand-profile": load_transform_save_market_trends_demand_profile,
    "/markets/demand": load_transform_save_market_demand,
    "/markets/supply": load_transform_save_market_supply,
    "/markets/supply/ls": load_transform_save_market_supply_ls,
    "/markets/supply/ss": load_transform_save_market_supply_ss,
    "/markets/scores": load_transform_save_market_scores,
    "/markets/risk": load_transform_save_market_risk,
    "/markets/fundamentals": load_transform_save_market_fundamentals,
    "/markets/cycle": load_transform_save_market_cycle,
    "/markets/growth/cumulative": load_transform_save_market_growth_cumulative,
}


def get_market_endpoint_transformer(endpoint):
    endpoint_path = endpoint.get("path") if isinstance(endpoint, dict) else endpoint
    try:
        return MARKET_ENDPOINT_TRANSFORMERS[endpoint_path]
    except KeyError as error:
        raise ValueError(f"No transformer is registered for endpoint: {endpoint_path}") from error