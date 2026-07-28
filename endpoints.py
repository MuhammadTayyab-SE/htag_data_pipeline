ENDPOINTS = [
    {
        "path": "/markets/trends/price", 
        "table": "market_trend_price",
        "params":{ 
            "limit": "1000",
            "offset": "0",
            "area_id":[],
            "level": "suburb"
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
            "level": "suburb"
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
            "level": "suburb"
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
            "level": "suburb"
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
            "level": "suburb"
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
            "level": "suburb"
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
            "level": "suburb"
        },     
        "on_conflict": ["area_id","period_end","property_type"]

    }


]
