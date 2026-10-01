import logging
import os
from pathlib import Path
from typing import Any, Dict, List, Optional
import yaml

logger = logging.getLogger(__name__)

# Search paths for instruments.yaml
_CONFIG_PATHS = [
    Path("config/instruments.yaml"),
    Path("../config/instruments.yaml"),
    Path(__file__).resolve().parent.parent.parent / "config" / "instruments.yaml",
    Path(__file__).resolve().parent.parent.parent.parent / "config" / "instruments.yaml",
]

_DEFAULT_UNIVERSE = {
    "version": "1.0",
    "asset_classes": {
        "stocks": {"name": "Equities / Stocks", "description": "Exchange-traded equity shares."},
        "mutual_funds": {"name": "Mutual Funds / ETFs", "description": "Broad-market index funds."},
        "bonds": {"name": "Fixed Income / Bonds", "description": "Sovereign/corporate bonds."},
        "gold": {"name": "Precious Metals / Gold", "description": "Gold ETFs and commodities."},
        "cash": {"name": "Cash & Liquid Reserves", "description": "Liquid cash equivalents."},
    },
    "instruments": [
        {"symbol": "RELIANCE.NS", "name": "Reliance Industries Limited", "asset_class": "stocks", "is_yahoo_supported": True},
        {"symbol": "TCS.NS", "name": "Tata Consultancy Services Ltd", "asset_class": "stocks", "is_yahoo_supported": True},
        {"symbol": "HDFCBANK.NS", "name": "HDFC Bank Limited", "asset_class": "stocks", "is_yahoo_supported": True},
        {"symbol": "INFY.NS", "name": "Infosys Limited", "asset_class": "stocks", "is_yahoo_supported": True},
        {"symbol": "ICICIBANK.NS", "name": "ICICI Bank Limited", "asset_class": "stocks", "is_yahoo_supported": True},
        {"symbol": "NIFTYBEES.NS", "name": "Nippon India ETF Nifty 50 BeES", "asset_class": "mutual_funds", "is_yahoo_supported": True},
        {"symbol": "JUNIORBEES.NS", "name": "Nippon India ETF Junior BeES", "asset_class": "mutual_funds", "is_yahoo_supported": True},
        {"symbol": "GOLDBEES.NS", "name": "Nippon India ETF Gold BeES", "asset_class": "gold", "is_yahoo_supported": True},
        {"symbol": "SETF10GILT.NS", "name": "SBI ETF 10 Year Gilt", "asset_class": "bonds", "is_yahoo_supported": True},
        {"symbol": "LIQUIDBEES.NS", "name": "Nippon India ETF Liquid BeES", "asset_class": "cash", "is_yahoo_supported": True},
        {"symbol": "INR_CASH", "name": "Indian Rupee Cash Reserve", "asset_class": "cash", "is_yahoo_supported": False, "fixed_annual_yield": 0.055},
    ],
}

_CACHED_UNIVERSE: Optional[Dict[str, Any]] = None


def load_instruments_config(force_reload: bool = False) -> Dict[str, Any]:
    """
    Load the instrument universe from YAML configuration file.
    Falls back to built-in default universe if YAML file cannot be read.
    """
    global _CACHED_UNIVERSE
    if _CACHED_UNIVERSE is not None and not force_reload:
        return _CACHED_UNIVERSE

    for path in _CONFIG_PATHS:
        try:
            if path.is_file():
                with open(path, "r", encoding="utf-8") as f:
                    data = yaml.safe_load(f)
                    if data and "instruments" in data:
                        logger.info(f"Loaded {len(data['instruments'])} instruments from {path}")
                        _CACHED_UNIVERSE = data
                        return _CACHED_UNIVERSE
        except Exception as exc:
            logger.warning(f"Error loading instruments config from {path}: {exc}")

    logger.info("Using default in-memory instrument universe configuration")
    _CACHED_UNIVERSE = _DEFAULT_UNIVERSE
    return _CACHED_UNIVERSE


def get_all_instruments() -> List[Dict[str, Any]]:
    """Returns list of all configured instruments."""
    config = load_instruments_config()
    return config.get("instruments", [])


def get_all_asset_classes() -> Dict[str, Any]:
    """Returns map of supported conceptual asset classes."""
    config = load_instruments_config()
    return config.get("asset_classes", {})


def get_yahoo_supported_symbols() -> List[str]:
    """Returns list of ticker symbols that can be fetched via Yahoo Finance."""
    instruments = get_all_instruments()
    return [
        inst["symbol"]
        for inst in instruments
        if inst.get("is_yahoo_supported", True)
    ]


def get_instrument_metadata(symbol: str) -> Optional[Dict[str, Any]]:
    """Get metadata for a specific instrument by symbol."""
    clean_sym = symbol.strip().upper()
    for inst in get_all_instruments():
        if inst["symbol"].strip().upper() == clean_sym:
            return inst
    return None


def get_asset_class_for_symbol(symbol: str) -> str:
    """Return the asset class for a given symbol, defaulting to 'stocks'."""
    inst = get_instrument_metadata(symbol)
    if inst and "asset_class" in inst:
        return inst["asset_class"]
    return "stocks"


def get_instruments_by_asset_class(asset_class: str) -> List[Dict[str, Any]]:
    """Filter configured instruments by conceptual asset class."""
    clean_ac = asset_class.strip().lower()
    return [
        inst for inst in get_all_instruments()
        if inst.get("asset_class", "").lower() == clean_ac
    ]
