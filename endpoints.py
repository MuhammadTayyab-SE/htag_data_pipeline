import calendar
from datetime import date


def _months_before(value, months):
    """Return value shifted back by the requested number of calendar months."""
    month_index = value.year * 12 + value.month - 1 - months
    year, zero_based_month = divmod(month_index, 12)
    month = zero_based_month + 1
    day = min(value.day, calendar.monthrange(year, month)[1])
    return value.replace(year=year, month=month, day=day)


_TODAY = date.today()
PERIOD_END_MIN = _months_before(_TODAY.replace(day=1), 13).isoformat()
PERIOD_END_MAX = _TODAY.isoformat()


ENDPOINTS = [
    {
        "path": "/markets/trends/price", 
        "table": "market_trends_price",
        "params":{ 
            "limit": "1000",
            "offset": "0",
            "area_id":[],
            "level": "suburb",
            "period_end_min": PERIOD_END_MIN,
            "period_end_max": PERIOD_END_MAX
        },
        "on_conflict": ["area_id","period_end","property_type"]
    },

    {
        "path": "/markets/trends/rent", 
        "table": "market_trends_rent",
        "params":{ 
            "limit": "1000",
            "offset": "0",
            "area_id":[],
            "level": "suburb",
            "period_end_min": PERIOD_END_MIN,
            "period_end_max": PERIOD_END_MAX
        },
        "on_conflict": ["area_id","period_end","property_type"]

    },

    {
        "path": "/markets/trends/yield", 
        "table": "market_trends_yield",
        "params":{ 
            "limit": "1000",
            "offset": "0",
            "area_id":[],
            "level": "suburb",
            "period_end_min": PERIOD_END_MIN,
            "period_end_max": PERIOD_END_MAX
        },
        "on_conflict": ["area_id","period_end","property_type"]

    },
    

    {
        "path": "/markets/trends/demand-profile", 
        "table": "market_trends_demand_profile",
        "params":{ 
            "limit": "1000",
            "offset": "0",
            "area_id":[],
            "level": "suburb",
            "period_end_min": PERIOD_END_MIN,
            "period_end_max": PERIOD_END_MAX
        },  
        "on_conflict": ["area_id","period_end"]

    },

    {
        "path": "/markets/demand", 
        "table": "market_demand",
        "params":{ 
            "limit": "1000",
            "offset": "0",
            "area_id":[],
            "level": "suburb",
            "period_end_min": PERIOD_END_MIN,
            "period_end_max": PERIOD_END_MAX
        },   
        "on_conflict": ["area_id","period_end","property_type"]
    
    },

    {
        "path": "/markets/supply", 
        "table": "market_supply",
        "params":{ 
            "limit": "1000",
            "offset": "0",
            "area_id":[],
            "level": "suburb",
            "period_end_min": PERIOD_END_MIN,
            "period_end_max": PERIOD_END_MAX
        },     
        "on_conflict": ["area_id","period_end","property_type"]

    },
        
    {
        "path": "/markets/trends/days-on-market", 
        "table": "market_supply",
        "params":{ 
            "limit": "1000",
            "offset": "0",
            "area_id":[],
            "level": "suburb",
            "period_end_min": PERIOD_END_MIN,
            "period_end_max": PERIOD_END_MAX
        },     
        "on_conflict": ["area_id","period_end","property_type"]

    }


]
