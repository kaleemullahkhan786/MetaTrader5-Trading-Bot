import logging
import asyncio
from typing import Optional, Dict, Any
from config.settings import MESSAGES, MIN_LOT_SIZE, MAX_LOT_SIZE, MT5_SYMBOLS

# Setup logging
def setup_logging():
    """Setup logging configuration"""
    from config.settings import LOG_LEVEL, LOG_FORMAT, LOG_FILE
    
    # Ensure logs directory exists
    LOG_FILE.parent.mkdir(exist_ok=True)
    
    logging.basicConfig(
        level=getattr(logging, LOG_LEVEL),
        format=LOG_FORMAT,
        handlers=[
            logging.FileHandler(LOG_FILE),
            logging.StreamHandler()
        ]
    )
    return logging.getLogger(__name__)

def validate_lot_size(lots: str) -> Optional[float]:
    """Validate lot size input"""
    try:
        lot_size = float(lots)
        if MIN_LOT_SIZE <= lot_size <= MAX_LOT_SIZE:
            return lot_size
        return None
    except ValueError:
        return None

def validate_symbol(symbol: str) -> bool:
    """Validate trading symbol"""
    return symbol.upper() in MT5_SYMBOLS

def format_account_info(account_info: Dict[str, Any]) -> str:
    """Format account information for display"""
    balance = account_info.get('balance', 0)
    equity = account_info.get('equity', 0)
    profit = account_info.get('profit', 0)
    margin = account_info.get('margin', 0)
    
    return MESSAGES["account_info"].format(
        balance=f"{balance:,.2f}",
        equity=f"{equity:,.2f}",
        profit=f"{profit:,.2f}",
        margin=f"{margin:,.2f}"
    )

def format_trade_info(trade: Dict[str, Any]) -> str:
    """Format individual trade information"""
    symbol = trade.get('symbol', 'Unknown')
    type_str = trade.get('type', 'Unknown')
    lots = trade.get('lots', 0)
    price = trade.get('price', 0)
    ticket = trade.get('ticket', 'Unknown')
    profit = trade.get('profit', 0)
    
    return f"🎯 **{symbol}** {type_str}\n" \
           f"📊 Lots: {lots}\n" \
           f"💰 Price: {price}\n" \
           f"🎫 Ticket: {ticket}\n" \
           f"💵 Profit: ${profit:,.2f}\n"

def format_trades_list(trades: list) -> str:
    """Format list of trades for display"""
    if not trades:
        return MESSAGES["no_trades"]
    
    trades_text = ""
    for i, trade in enumerate(trades, 1):
        trades_text += f"{i}. {format_trade_info(trade)}\n"
    
    return MESSAGES["trades_list"].format(trades=trades_text)

def get_message_text(update) -> Optional[str]:
    """Extract text from update (message or callback query)"""
    if update.message and update.message.text:
        return update.message.text
    elif update.callback_query and update.callback_query.message:
        return update.callback_query.message.text
    return None

def get_user_id(update) -> Optional[int]:
    """Extract user ID from update"""
    if update.message and update.message.from_user:
        return update.message.from_user.id
    elif update.callback_query and update.callback_query.from_user:
        return update.callback_query.from_user.id
    return None

def get_chat_id(update) -> Optional[int]:
    """Extract chat ID from update"""
    if update.message and update.message.chat:
        return update.message.chat.id
    elif update.callback_query and update.callback_query.message:
        return update.callback_query.message.chat.id
    return None

async def safe_reply(update, context, text: str, reply_markup=None):
    """Safely reply to update (works for both messages and callback queries)"""
    try:
        if update.callback_query:
            await update.callback_query.edit_message_text(
                text=text,
                reply_markup=reply_markup,
                parse_mode='Markdown'
            )
        elif update.message:
            await update.message.reply_text(
                text=text,
                reply_markup=reply_markup,
                parse_mode='Markdown'
            )
    except Exception as e:
        logging.error(f"Error in safe_reply: {e}")
        # Fallback: try to send new message
        try:
            chat_id = get_chat_id(update)
            if chat_id:
                await context.bot.send_message(
                    chat_id=chat_id,
                    text=text,
                    reply_markup=reply_markup,
                    parse_mode='Markdown'
                )
        except Exception as fallback_error:
            logging.error(f"Fallback reply also failed: {fallback_error}")

def is_authorized_user(user_id: int) -> bool:
    """Check if user is authorized to use the bot"""
    from config.settings import ALLOWED_USERS, ADMIN_USER_ID
    
    if not ALLOWED_USERS and not ADMIN_USER_ID:
        return True  # Allow all users if no restrictions set
    
    if user_id in ALLOWED_USERS or user_id == ADMIN_USER_ID:
        return True
    
    return False

def parse_callback_data(data: str) -> tuple:
    """Parse callback data into action and parameters"""
    # Handle specific patterns first
    if data.startswith('trade_type_'):
        trade_type = data.replace('trade_type_', '')
        return 'trade_type', trade_type
    
    # Handle compound actions that should not be split
    compound_actions = [
        'lot_settings', 'risk_settings', 'sl_settings', 'notification_settings',
        'back_to_main', 'back_to_symbols', 'back_to_trade_type', 'back_to_settings',
        'back_to_lots', 'back_to_advanced', 'account_info', 'open_trade', 'my_trades',
        'close_trade', 'market_info', 'settings', 'advanced_trade',
        'set_sl_tp', 'set_breakeven', 'modify_trade'
    ]
    
    # Check if it's a compound action without parameters
    if data in compound_actions:
        return data, None
    
    # Handle actions with parameters (like symbol_EURUSD, lots_0.1, etc.)
    parts = data.split('_', 1)
    if len(parts) == 1:
        return parts[0], None
    return parts[0], parts[1] 