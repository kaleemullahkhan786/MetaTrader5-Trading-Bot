from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from config.settings import KEYBOARDS, MT5_SYMBOLS

def get_main_menu_keyboard():
    """Create main menu keyboard"""
    keyboard = []
    for row in KEYBOARDS["main_menu"]:
        keyboard_row = []
        for button_text in row:
            if button_text == "📊 Account Info":
                keyboard_row.append(InlineKeyboardButton(button_text, callback_data="account_info"))
            elif button_text == "📈 Open Trade":
                keyboard_row.append(InlineKeyboardButton(button_text, callback_data="open_trade"))
            elif button_text == "📋 My Trades":
                keyboard_row.append(InlineKeyboardButton(button_text, callback_data="my_trades"))
            elif button_text == "❌ Close Trade":
                keyboard_row.append(InlineKeyboardButton(button_text, callback_data="close_trade"))
            elif button_text == "📊 Market Info":
                keyboard_row.append(InlineKeyboardButton(button_text, callback_data="market_info"))
            elif button_text == "⚙️ Settings":
                keyboard_row.append(InlineKeyboardButton(button_text, callback_data="settings"))
        keyboard.append(keyboard_row)
    return InlineKeyboardMarkup(keyboard)

def get_symbols_keyboard():
    """Create symbols selection keyboard"""
    keyboard = []
    symbols = MT5_SYMBOLS.copy()
    
    # Create rows of 3 symbols each
    for i in range(0, len(symbols), 3):
        row = []
        for j in range(3):
            if i + j < len(symbols):
                symbol = symbols[i + j]
                row.append(InlineKeyboardButton(symbol, callback_data=f"symbol_{symbol}"))
        keyboard.append(row)
    
    # Add back button
    keyboard.append([InlineKeyboardButton("🔙 Back", callback_data="back_to_main")])
    return InlineKeyboardMarkup(keyboard)

def get_trade_type_keyboard():
    """Create trade type selection keyboard"""
    keyboard = [
        [InlineKeyboardButton("🟢 BUY", callback_data="trade_type_BUY")],
        [InlineKeyboardButton("🔴 SELL", callback_data="trade_type_SELL")],
        [InlineKeyboardButton("💰 Risk-Based BUY", callback_data="risk_based_trade_BUY")],
        [InlineKeyboardButton("💰 Risk-Based SELL", callback_data="risk_based_trade_SELL")],
        [InlineKeyboardButton("🔙 Back", callback_data="back_to_symbols")]
    ]
    return InlineKeyboardMarkup(keyboard)

def get_lots_keyboard():
    """Create lot size selection keyboard"""
    keyboard = []
    for row in KEYBOARDS["lots"]:
        keyboard_row = []
        for button_text in row:
            if button_text == "🔙 Back":
                keyboard_row.append(InlineKeyboardButton(button_text, callback_data="back_to_trade_type"))
            else:
                keyboard_row.append(InlineKeyboardButton(button_text, callback_data=f"lots_{button_text}"))
        keyboard.append(keyboard_row)
    
    # Add manual input option
    keyboard.append([InlineKeyboardButton("✏️ Manual Lot Size", callback_data="manual_lot_input")])
    
    return InlineKeyboardMarkup(keyboard)

def get_trades_keyboard(trades):
    """Create trades list keyboard with close buttons"""
    keyboard = []
    for trade in trades:
        ticket = trade.get('ticket', 'Unknown')
        symbol = trade.get('symbol', 'Unknown')
        type_str = trade.get('type', 'Unknown')
        lots = trade.get('lots', 0)
        
        button_text = f"{symbol} {type_str} {lots}L"
        keyboard.append([InlineKeyboardButton(button_text, callback_data=f"close_trade_{ticket}")])
    
    keyboard.append([InlineKeyboardButton("🔙 Back", callback_data="back_to_main")])
    return InlineKeyboardMarkup(keyboard)

def get_back_keyboard(callback_data="back_to_main"):
    """Create simple back button keyboard"""
    keyboard = [[InlineKeyboardButton("🔙 Back", callback_data=callback_data)]]
    return InlineKeyboardMarkup(keyboard)

def get_confirm_keyboard(action, data):
    """Create confirmation keyboard"""
    keyboard = [
        [
            InlineKeyboardButton("✅ Confirm", callback_data=f"confirm_{action}_{data}"),
            InlineKeyboardButton("❌ Cancel", callback_data="back_to_main")
        ]
    ]
    return InlineKeyboardMarkup(keyboard) 

def get_settings_keyboard():
    """Create settings menu keyboard"""
    keyboard = [
        [InlineKeyboardButton("📊 Default Lot Size", callback_data="lot_settings")],
        [InlineKeyboardButton("⚠️ Risk Management", callback_data="risk_settings")],
        [InlineKeyboardButton("🛡️ Auto Stop Loss", callback_data="sl_settings")],
        [InlineKeyboardButton("🔔 Notifications", callback_data="notification_settings")],
        [InlineKeyboardButton("🔙 Back", callback_data="back_to_main")]
    ]
    return InlineKeyboardMarkup(keyboard)

def get_lot_settings_keyboard():
    """Create lot size settings keyboard"""
    keyboard = [
        [InlineKeyboardButton("0.01", callback_data="update_default_lots_0.01")],
        [InlineKeyboardButton("0.05", callback_data="update_default_lots_0.05")],
        [InlineKeyboardButton("0.1", callback_data="update_default_lots_0.1")],
        [InlineKeyboardButton("0.5", callback_data="update_default_lots_0.5")],
        [InlineKeyboardButton("1.0", callback_data="update_default_lots_1.0")],
        [InlineKeyboardButton("🔙 Back", callback_data="back_to_settings")]
    ]
    return InlineKeyboardMarkup(keyboard)

def get_risk_settings_keyboard():
    """Create risk management settings keyboard"""
    keyboard = [
        [InlineKeyboardButton("0.5%", callback_data="update_max_risk_0.5")],
        [InlineKeyboardButton("1.0%", callback_data="update_max_risk_1.0")],
        [InlineKeyboardButton("2.0%", callback_data="update_max_risk_2.0")],
        [InlineKeyboardButton("3.0%", callback_data="update_max_risk_3.0")],
        [InlineKeyboardButton("5.0%", callback_data="update_max_risk_5.0")],
        [InlineKeyboardButton("🔙 Back", callback_data="back_to_settings")]
    ]
    return InlineKeyboardMarkup(keyboard)

def get_sl_settings_keyboard():
    """Create stop loss settings keyboard"""
    keyboard = [
        [InlineKeyboardButton("20 pips", callback_data="update_auto_sl_20")],
        [InlineKeyboardButton("50 pips", callback_data="update_auto_sl_50")],
        [InlineKeyboardButton("100 pips", callback_data="update_auto_sl_100")],
        [InlineKeyboardButton("200 pips", callback_data="update_auto_sl_200")],
        [InlineKeyboardButton("🔙 Back", callback_data="back_to_settings")]
    ]
    return InlineKeyboardMarkup(keyboard)

def get_notification_settings_keyboard():
    """Create notification settings keyboard"""
    keyboard = [
        [InlineKeyboardButton("✅ Enable", callback_data="update_notifications_true")],
        [InlineKeyboardButton("❌ Disable", callback_data="update_notifications_false")],
        [InlineKeyboardButton("🔙 Back", callback_data="back_to_settings")]
    ]
    return InlineKeyboardMarkup(keyboard) 

def get_advanced_trade_keyboard():
    """Create advanced trade options keyboard"""
    keyboard = [
        [InlineKeyboardButton("🛡️ Add Stop Loss", callback_data="add_sl")],
        [InlineKeyboardButton("🎯 Add Take Profit", callback_data="add_tp")],
        [InlineKeyboardButton("⚖️ Add Both SL & TP", callback_data="add_sl_tp")],
        [InlineKeyboardButton("🚀 Open Trade Now", callback_data="open_trade_now")],
        [InlineKeyboardButton("🔙 Back", callback_data="back_to_lots")]
    ]
    return InlineKeyboardMarkup(keyboard)

def get_sl_options_keyboard():
    """Create stop loss options keyboard"""
    keyboard = [
        [InlineKeyboardButton("20 pips", callback_data="sl_20")],
        [InlineKeyboardButton("50 pips", callback_data="sl_50")],
        [InlineKeyboardButton("100 pips", callback_data="sl_100")],
        [InlineKeyboardButton("200 pips", callback_data="sl_200")],
        [InlineKeyboardButton("🔙 Back", callback_data="back_to_advanced")]
    ]
    return InlineKeyboardMarkup(keyboard)

def get_tp_options_keyboard():
    """Create take profit options keyboard"""
    keyboard = [
        [InlineKeyboardButton("50 pips", callback_data="tp_50")],
        [InlineKeyboardButton("100 pips", callback_data="tp_100")],
        [InlineKeyboardButton("200 pips", callback_data="tp_200")],
        [InlineKeyboardButton("500 pips", callback_data="tp_500")],
        [InlineKeyboardButton("🔙 Back", callback_data="back_to_advanced")]
    ]
    return InlineKeyboardMarkup(keyboard)

def get_risk_based_trade_keyboard():
    """Create risk-based trading options keyboard"""
    keyboard = [
        [InlineKeyboardButton("💰 Enter Risk Amount", callback_data="input_risk_amount")],
        [InlineKeyboardButton("🔙 Back", callback_data="back_to_trade_type")]
    ]
    return InlineKeyboardMarkup(keyboard)

def get_tp_input_keyboard():
    """Create take profit input keyboard"""
    keyboard = [
        [InlineKeyboardButton("🎯 Enter TP Amount", callback_data="input_tp_amount")],
        [InlineKeyboardButton("❌ No Take Profit", callback_data="no_tp")],
        [InlineKeyboardButton("🔙 Back", callback_data="back_to_sl_input")]
    ]
    return InlineKeyboardMarkup(keyboard)

def get_trade_management_keyboard(trades):
    """Create trade management keyboard with advanced options"""
    keyboard = []
    for trade in trades:
        ticket = trade.get('ticket', 'Unknown')
        symbol = trade.get('symbol', 'Unknown')
        type_str = trade.get('type', 'Unknown')
        lots = trade.get('lots', 0)
        
        # Main trade button
        button_text = f"{symbol} {type_str} {lots}L"
        keyboard.append([InlineKeyboardButton(button_text, callback_data=f"manage_trade_{ticket}")])
    
    # Management options
    keyboard.append([InlineKeyboardButton("🛡️ Set Breakeven", callback_data="breakeven_all")])
    keyboard.append([InlineKeyboardButton("📊 Modify SL/TP", callback_data="modify_all")])
    keyboard.append([InlineKeyboardButton("🔙 Back", callback_data="back_to_main")])
    
    return InlineKeyboardMarkup(keyboard) 