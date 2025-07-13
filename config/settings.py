import os
import json
from pathlib import Path

# Base directory
BASE_DIR = Path(__file__).parent.parent

# Load config from JSON
def load_config():
    config_path = BASE_DIR / "config.json"
    if config_path.exists():
        with open(config_path, 'r') as f:
            return json.load(f)
    return {}

config = load_config()

# Bot settings
BOT_TOKEN = config.get('bot_token', os.getenv('BOT_TOKEN', ''))
ALLOWED_USERS = config.get('allowed_users', [])
ADMIN_USER_ID = config.get('admin_user_id', None)

# MT5 settings
MT5_SYMBOLS = [
    "EURUSD", "GBPUSD", "USDJPY", "USDCHF", "AUDUSD", 
    "USDCAD", "NZDUSD", "EURGBP", "EURJPY", "GBPJPY"
]

# Trading settings
DEFAULT_LOT_SIZE = 0.01
MAX_LOT_SIZE = 10.0
MIN_LOT_SIZE = 0.01

# Logging settings
LOG_LEVEL = "INFO"
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
LOG_FILE = BASE_DIR / "logs" / "trading_bot.log"

# Message templates
MESSAGES = {
    "welcome": "🤖 **MetaTrader 5 Trading Bot**\n\nWelcome! I can help you manage your trades.",
    "unauthorized": "❌ You are not authorized to use this bot.",
    "error": "❌ An error occurred: {error}",
    "success": "✅ {message}",
    "account_info": "📊 **Account Information**\n\nBalance: ${balance}\nEquity: ${equity}\nProfit: ${profit}\nMargin: ${margin}",
    "trade_opened": "✅ **Trade Opened Successfully**\n\nSymbol: {symbol}\nType: {type}\nLots: {lots}\nPrice: {price}\nTicket: {ticket}",
    "trade_closed": "✅ **Trade Closed Successfully**\n\nTicket: {ticket}\nProfit: ${profit}",
    "no_trades": "📭 No open trades found.",
    "trades_list": "📋 **Open Trades**\n\n{trades}",
    "select_symbol": "Select trading symbol:",
    "select_lots": "Enter lot size (0.01 - 10.0):",
    "invalid_lots": "❌ Invalid lot size. Please enter a value between 0.01 and 10.0.",
    "manual_lot_input": "✏️ **Manual Lot Size Input**\n\nPlease enter your desired lot size.\n**Valid range:** 0.01 - 10.0\n**Examples:** 0.01, 0.1, 1.5, 2.0\n\nType your lot size now:",
    "invalid_symbol": "❌ Invalid symbol. Please select from the available symbols.",
    "back_to_main": "🔙 Back to main menu"
}

# Keyboard layouts
KEYBOARDS = {
    "main_menu": [
        ["📊 Account Info", "📈 Open Trade"],
        ["📋 My Trades", "❌ Close Trade"],
        ["📊 Market Info", "⚙️ Settings"]
    ],
    "symbols": [
        ["EURUSD", "GBPUSD", "USDJPY"],
        ["USDCHF", "AUDUSD", "USDCAD"],
        ["NZDUSD", "EURGBP", "EURJPY"],
        ["GBPJPY", "🔙 Back"]
    ],
    "trade_types": [
        ["🟢 BUY", "🔴 SELL"],
        ["🔙 Back"]
    ],
    "lots": [
        ["0.01", "0.1", "1.0"],
        ["0.05", "0.5", "5.0"],
        ["🔙 Back"]
    ]
} 