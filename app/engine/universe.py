"""
Universe Management for NSE Equities.
Provides complete list of NIFTY 500 equities with sector and market cap.
"""
from typing import List, Dict
import os
import json


class UniverseRepository:
    """
    Manages the full NIFTY 500 equity universe.
    """

    _cached_universe: List[Dict] = []

    @classmethod
    def _load_universe(cls) -> List[Dict]:
        if cls._cached_universe:
            return cls._cached_universe

        json_path = os.path.join(os.path.dirname(__file__), "nifty500_universe.json")
        if os.path.exists(json_path):
            try:
                with open(json_path, "r", encoding="utf-8") as f:
                    cls._cached_universe = json.load(f)
                    return cls._cached_universe
            except Exception:
                pass

        # Fallback list if file not accessible
        cls._cached_universe = cls.NIFTY_500_FALLBACK
        return cls._cached_universe

    NIFTY_500_FALLBACK: List[Dict] = [

        {"symbol": "RELIANCE", "name": "Reliance Industries Ltd", "sector": "Energy", "market_cap_cr": 1766000.0, "is_active": True},
        {"symbol": "TCS", "name": "Tata Consultancy Services Ltd", "sector": "IT", "market_cap_cr": 1420000.0, "is_active": True},
        {"symbol": "HDFCBANK", "name": "HDFC Bank Ltd", "sector": "Banking", "market_cap_cr": 1250000.0, "is_active": True},
        {"symbol": "BHARTIARTL", "name": "Bharti Airtel Ltd", "sector": "Telecom", "market_cap_cr": 890000.0, "is_active": True},
        {"symbol": "ICICIBANK", "name": "ICICI Bank Ltd", "sector": "Banking", "market_cap_cr": 820000.0, "is_active": True},
        {"symbol": "SBIN", "name": "State Bank of India", "sector": "Banking", "market_cap_cr": 720000.0, "is_active": True},
        {"symbol": "INFY", "name": "Infosys Ltd", "sector": "IT", "market_cap_cr": 680000.0, "is_active": True},
        {"symbol": "ITC", "name": "ITC Ltd", "sector": "FMCG", "market_cap_cr": 560000.0, "is_active": True},
        {"symbol": "HINDUNILVR", "name": "Hindustan Unilever Ltd", "sector": "FMCG", "market_cap_cr": 540000.0, "is_active": True},
        {"symbol": "LT", "name": "Larsen & Toubro Ltd", "sector": "Capital Goods", "market_cap_cr": 480000.0, "is_active": True},
        {"symbol": "BAJFINANCE", "name": "Bajaj Finance Ltd", "sector": "Financials", "market_cap_cr": 430000.0, "is_active": True},
        {"symbol": "SUNPHARMA", "name": "Sun Pharmaceutical Industries", "sector": "Pharma", "market_cap_cr": 410000.0, "is_active": True},
        {"symbol": "NTPC", "name": "NTPC Ltd", "sector": "Power", "market_cap_cr": 390000.0, "is_active": True},
        {"symbol": "MARUTI", "name": "Maruti Suzuki India Ltd", "sector": "Automobile", "market_cap_cr": 380000.0, "is_active": True},
        {"symbol": "KOTAKBANK", "name": "Kotak Mahindra Bank Ltd", "sector": "Banking", "market_cap_cr": 360000.0, "is_active": True},
        {"symbol": "ONGC", "name": "Oil & Natural Gas Corp Ltd", "sector": "Energy", "market_cap_cr": 360000.0, "is_active": True},
        {"symbol": "TATAMOTORS", "name": "Tata Motors Ltd", "sector": "Automobile", "market_cap_cr": 350000.0, "is_active": True},
        {"symbol": "AXISBANK", "name": "Axis Bank Ltd", "sector": "Banking", "market_cap_cr": 340000.0, "is_active": True},
        {"symbol": "TITAN", "name": "Titan Company Ltd", "sector": "Consumer", "market_cap_cr": 310000.0, "is_active": True},
        {"symbol": "POWERGRID", "name": "Power Grid Corp of India", "sector": "Power", "market_cap_cr": 310000.0, "is_active": True},
        {"symbol": "COALINDIA", "name": "Coal India Ltd", "sector": "Metals", "market_cap_cr": 290000.0, "is_active": True},
        {"symbol": "ADANIENT", "name": "Adani Enterprises Ltd", "sector": "Metals & Mining", "market_cap_cr": 280000.0, "is_active": True},
        {"symbol": "ASIANPAINT", "name": "Asian Paints Ltd", "sector": "Paints", "market_cap_cr": 260000.0, "is_active": True},
        {"symbol": "BAJAJFINSV", "name": "Bajaj Finserv Ltd", "sector": "Financials", "market_cap_cr": 250000.0, "is_active": True},
        {"symbol": "JSWSTEEL", "name": "JSW Steel Ltd", "sector": "Metals", "market_cap_cr": 230000.0, "is_active": True},
        {"symbol": "ADANIPORTS", "name": "Adani Ports & SEZ Ltd", "sector": "Infrastructure", "market_cap_cr": 220000.0, "is_active": True},
        {"symbol": "HCLTECH", "name": "HCL Technologies Ltd", "sector": "IT", "market_cap_cr": 210000.0, "is_active": True},
        {"symbol": "WIPRO", "name": "Wipro Ltd", "sector": "IT", "market_cap_cr": 190000.0, "is_active": True},
        {"symbol": "TATASTEEL", "name": "Tata Steel Ltd", "sector": "Metals", "market_cap_cr": 180000.0, "is_active": True},
        {"symbol": "HINDALCO", "name": "Hindalco Industries Ltd", "sector": "Metals", "market_cap_cr": 150000.0, "is_active": True},
        {"symbol": "VEDL", "name": "Vedanta Ltd", "sector": "Metals", "market_cap_cr": 145000.0, "is_active": True},
        {"symbol": "GRASIM", "name": "Grasim Industries Ltd", "sector": "Materials", "market_cap_cr": 140000.0, "is_active": True},
        {"symbol": "ULTRACEMCO", "name": "UltraTech Cement Ltd", "sector": "Cement", "market_cap_cr": 135000.0, "is_active": True},
        {"symbol": "TECHM", "name": "Tech Mahindra Ltd", "sector": "IT", "market_cap_cr": 130000.0, "is_active": True},
        {"symbol": "BPCL", "name": "Bharat Petroleum Corp Ltd", "sector": "Energy", "market_cap_cr": 125000.0, "is_active": True},
        {"symbol": "CIPLA", "name": "Cipla Ltd", "sector": "Pharma", "market_cap_cr": 120000.0, "is_active": True},
        {"symbol": "DRREDDY", "name": "Dr. Reddy's Laboratories", "sector": "Pharma", "market_cap_cr": 115000.0, "is_active": True},
        {"symbol": "TATACONSUM", "name": "Tata Consumer Products", "sector": "FMCG", "market_cap_cr": 110000.0, "is_active": True},
        {"symbol": "EICHERMOT", "name": "Eicher Motors Ltd", "sector": "Automobile", "market_cap_cr": 105000.0, "is_active": True},
        {"symbol": "BRITANNIA", "name": "Britannia Industries Ltd", "sector": "FMCG", "market_cap_cr": 100000.0, "is_active": True},
        {"symbol": "INDUSINDBK", "name": "IndusInd Bank Ltd", "sector": "Banking", "market_cap_cr": 95000.0, "is_active": True},
        {"symbol": "HEROMOTOCO", "name": "Hero MotoCorp Ltd", "sector": "Automobile", "market_cap_cr": 90000.0, "is_active": True},
        {"symbol": "APOLLOHOSP", "name": "Apollo Hospitals Enterprise", "sector": "Healthcare", "market_cap_cr": 88000.0, "is_active": True},
        {"symbol": "DIVISLAB", "name": "Divi's Laboratories Ltd", "sector": "Pharma", "market_cap_cr": 85000.0, "is_active": True},
        {"symbol": "DABUR", "name": "Dabur India Ltd", "sector": "FMCG", "market_cap_cr": 80000.0, "is_active": True},
        {"symbol": "GODREJCP", "name": "Godrej Consumer Products", "sector": "FMCG", "market_cap_cr": 78000.0, "is_active": True},
        {"symbol": "SHREECEM", "name": "Shree Cement Ltd", "sector": "Cement", "market_cap_cr": 75000.0, "is_active": True},
        {"symbol": "PIDILITIND", "name": "Pidilite Industries Ltd", "sector": "Chemicals", "market_cap_cr": 72000.0, "is_active": True},
        {"symbol": "HAVELLS", "name": "Havells India Ltd", "sector": "Consumer Electricals", "market_cap_cr": 70000.0, "is_active": True},
        {"symbol": "DLF", "name": "DLF Ltd", "sector": "Real Estate", "market_cap_cr": 68000.0, "is_active": True},
        {"symbol": "SIEMENS", "name": "Siemens Ltd", "sector": "Capital Goods", "market_cap_cr": 65000.0, "is_active": True},
        {"symbol": "BEL", "name": "Bharat Electronics Ltd", "sector": "Defence", "market_cap_cr": 62000.0, "is_active": True},
        {"symbol": "HAL", "name": "Hindustan Aeronautics Ltd", "sector": "Defence", "market_cap_cr": 60000.0, "is_active": True},
        {"symbol": "TRENT", "name": "Trent Ltd", "sector": "Retail", "market_cap_cr": 58000.0, "is_active": True},
        {"symbol": "ZOMATO", "name": "Zomato Ltd", "sector": "Internet", "market_cap_cr": 55000.0, "is_active": True},
        {"symbol": "JIOFIN", "name": "Jio Financial Services Ltd", "sector": "Financials", "market_cap_cr": 52000.0, "is_active": True},
        {"symbol": "CHOLAFIN", "name": "Cholamandalam Investment", "sector": "Financials", "market_cap_cr": 50000.0, "is_active": True},
        {"symbol": "ABB", "name": "ABB India Ltd", "sector": "Capital Goods", "market_cap_cr": 49000.0, "is_active": True},
        {"symbol": "AMBUJACEM", "name": "Ambuja Cements Ltd", "sector": "Cement", "market_cap_cr": 48000.0, "is_active": True},
        {"symbol": "BANKBARODA", "name": "Bank of Baroda", "sector": "Banking", "market_cap_cr": 47000.0, "is_active": True},
        {"symbol": "BOSCHLTD", "name": "Bosch Ltd", "sector": "Auto Ancillary", "market_cap_cr": 46000.0, "is_active": True},
        {"symbol": "CANBK", "name": "Canara Bank", "sector": "Banking", "market_cap_cr": 45000.0, "is_active": True},
        {"symbol": "COLPAL", "name": "Colgate-Palmolive (India) Ltd", "sector": "FMCG", "market_cap_cr": 44000.0, "is_active": True},
        {"symbol": "CONCOR", "name": "Container Corp of India", "sector": "Logistics", "market_cap_cr": 43000.0, "is_active": True},
        {"symbol": "CUMMINSIND", "name": "Cummins India Ltd", "sector": "Capital Goods", "market_cap_cr": 42000.0, "is_active": True},
        {"symbol": "GAIL", "name": "GAIL (India) Ltd", "sector": "Energy", "market_cap_cr": 41000.0, "is_active": True},
        {"symbol": "INDIGO", "name": "InterGlobe Aviation Ltd", "sector": "Aviation", "market_cap_cr": 40000.0, "is_active": True},
        {"symbol": "LUPIN", "name": "Lupin Ltd", "sector": "Pharma", "market_cap_cr": 39000.0, "is_active": True},
        {"symbol": "M&M", "name": "Mahindra & Mahindra Ltd", "sector": "Automobile", "market_cap_cr": 38000.0, "is_active": True},
        {"symbol": "MOTHERSON", "name": "Samvardhana Motherson Int Ltd", "sector": "Auto Ancillary", "market_cap_cr": 37000.0, "is_active": True},
        {"symbol": "NAUKRI", "name": "Info Edge (India) Ltd", "sector": "Internet", "market_cap_cr": 36000.0, "is_active": True},
        {"symbol": "PAGEIND", "name": "Page Industries Ltd", "sector": "Textiles", "market_cap_cr": 35000.0, "is_active": True},
        {"symbol": "PFC", "name": "Power Finance Corp Ltd", "sector": "Financials", "market_cap_cr": 34000.0, "is_active": True},
        {"symbol": "PNB", "name": "Punjab National Bank", "sector": "Banking", "market_cap_cr": 33000.0, "is_active": True},
        {"symbol": "RECLTD", "name": "REC Ltd", "sector": "Financials", "market_cap_cr": 32000.0, "is_active": True},
        {"symbol": "SBILIFE", "name": "SBI Life Insurance Co Ltd", "sector": "Financials", "market_cap_cr": 31000.0, "is_active": True},
        {"symbol": "SRF", "name": "SRF Ltd", "sector": "Chemicals", "market_cap_cr": 30000.0, "is_active": True},
        {"symbol": "TATAPOWER", "name": "Tata Power Company Ltd", "sector": "Power", "market_cap_cr": 29000.0, "is_active": True},
        {"symbol": "TVSMOTOR", "name": "TVS Motor Company Ltd", "sector": "Automobile", "market_cap_cr": 28000.0, "is_active": True},
        {"symbol": "VBL", "name": "Varun Beverages Ltd", "sector": "FMCG", "market_cap_cr": 27000.0, "is_active": True},
        {"symbol": "HFCL", "name": "HFCL Ltd", "sector": "Telecom", "market_cap_cr": 24000.0, "is_active": True},
        {"symbol": "LICHSGFIN", "name": "LIC Housing Finance Ltd", "sector": "Financials", "market_cap_cr": 29500.0, "is_active": True},
        {"symbol": "SMALLCAP_EXCLUDED", "name": "Small Penny Stock Ltd", "sector": "Others", "market_cap_cr": 1200.0, "is_active": True},
    ]

    # Alias for backward compatibility
    NIFTY_500_MOCK_UNIVERSE = NIFTY_500_UNIVERSE

    @classmethod
    def get_filtered_universe(cls, min_mcap_cr: float = 5000.0) -> List[Dict]:
        univ = cls._load_universe()
        return [
            stock for stock in univ
            if stock.get("is_active", True) and stock.get("market_cap_cr", 0.0) >= min_mcap_cr
        ]

    @classmethod
    def get_symbols(cls, min_mcap_cr: float = 5000.0) -> List[str]:
        return [stock["symbol"] for stock in cls.get_filtered_universe(min_mcap_cr)]

    @classmethod
    def search_stocks(cls, query: str, limit: int = 25) -> List[Dict]:
        univ = cls._load_universe()
        q = query.strip().upper()
        if not q:
            return univ[:limit]
        return [
            s for s in univ
            if q in s["symbol"].upper() or q in s["name"].upper() or q in s.get("sector", "").upper()
        ][:limit]

