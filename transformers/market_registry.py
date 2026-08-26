from .market_demand import load_transform_save_market_demand
from .market_supply import load_transform_save_market_supply
from .market_trends_days_on_market import load_transform_save_market_trends_days_on_market
from .market_trends_demand_profile import load_transform_save_market_trends_demand_profile
from .market_trends_price import load_transform_save_market_trends_price
from .market_trends_rent import load_transform_save_market_trends_rent
from .market_trends_yield import load_transform_save_market_trends_yield


MARKET_ENDPOINT_TRANSFORMERS = {
    "/markets/trends/price": load_transform_save_market_trends_price,
    "/markets/trends/rent": load_transform_save_market_trends_rent,
    "/markets/trends/yield": load_transform_save_market_trends_yield,
    "/markets/trends/demand-profile": load_transform_save_market_trends_demand_profile,
    "/markets/demand": load_transform_save_market_demand,
    "/markets/supply": load_transform_save_market_supply,
    "/markets/trends/days-on-market": load_transform_save_market_trends_days_on_market,
}


def get_market_endpoint_transformer(endpoint):
    endpoint_path = endpoint.get("path") if isinstance(endpoint, dict) else endpoint
    try:
        return MARKET_ENDPOINT_TRANSFORMERS[endpoint_path]
    except KeyError as error:
        raise ValueError(f"No transformer is registered for endpoint: {endpoint_path}") from error
