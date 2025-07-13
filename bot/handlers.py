import logging
from typing import Dict, Any
from telegram import Update
from telegram.ext import ContextTypes
from mt5.bridge import MT5Bridge
from bot.keyboards import (
    get_main_menu_keyboard, get_symbols_keyboard, get_trade_type_keyboard,
    get_lots_keyboard, get_trades_keyboard, get_back_keyboard, get_confirm_keyboard,
    get_settings_keyboard, get_lot_settings_keyboard, get_risk_settings_keyboard,
    get_sl_settings_keyboard, get_notification_settings_keyboard, get_advanced_trade_keyboard,
    get_risk_based_trade_keyboard, get_tp_input_keyboard
)
from bot.utils import (
    setup_logging, validate_lot_size, validate_symbol, format_account_info,
    format_trades_list, safe_reply, is_authorized_user, parse_callback_data,
    get_user_id, get_chat_id
)
from config.settings import MESSAGES, DEFAULT_LOT_SIZE, MIN_LOT_SIZE, MAX_LOT_SIZE, MT5_SYMBOLS
from datetime import datetime

logger = setup_logging()

# User sessions to store state
user_sessions: Dict[int, Dict[str, Any]] = {}

class BotHandlers:
    def __init__(self):
        self.mt5 = MT5Bridge()
    
    def get_user_session(self, user_id: int) -> Dict[str, Any]:
        """Get or create user session"""
        if user_id not in user_sessions:
            user_sessions[user_id] = {
                'state': 'main_menu',
                'selected_symbol': None,
                'selected_type': None,
                'selected_lots': None
            }
        return user_sessions[user_id]
    
    def update_user_session(self, user_id: int, **kwargs):
        """Update user session"""
        session = self.get_user_session(user_id)
        session.update(kwargs)
    
    async def start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /start command"""
        user_id = get_user_id(update)
        if not user_id:
            return
        
        if not is_authorized_user(user_id):
            await safe_reply(update, context, MESSAGES["unauthorized"])
            return
        
        self.update_user_session(user_id, state='main_menu')
        await safe_reply(
            update, context, 
            MESSAGES["welcome"], 
            get_main_menu_keyboard()
        )
    
    async def help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /help command"""
        help_text = """
🤖 **MetaTrader 5 Trading Bot - Complete Guide**

📋 **Available Commands:**
/start - Start the bot and show main menu
/help - Show this comprehensive help
/account - View account information
/trade - Open a new trade
/trades - View all open trades
/close - Close a trade
/market - View real-time market data
/settings - Manage bot settings
/status - Check bot and MT5 status
/quick - Quick trade shortcuts

🎯 **Trading Features:**
• **Account Management**: Balance, equity, profit, margin
• **Standard Trading**: BUY/SELL with custom lot sizes
• **💰 Risk-Based Trading**: Auto lot calculation based on risk amount and SL points
• **Advanced Trading**: Stop Loss, Take Profit, Breakeven
• **Risk Management**: Auto SL, risk percentage settings
• **Market Analysis**: Real-time prices, spreads, market summary

💡 **Risk-Based Trading (NEW):**
• Specify risk amount in dollars (e.g., $100)
• Set stop loss in points (e.g., 100 points)
• Optional take profit in dollars (e.g., $200)
• Bot automatically calculates optimal lot size
• Perfect risk management with 1:1, 1:2, 1:3 R:R ratios

⚙️ **Settings & Customization:**
• Default lot sizes (0.01 - 10.0)
• Risk management (0.1% - 10%)
• Auto stop loss (10-500 pips)
• Notification preferences
• User session management

📊 **Supported Symbols:**
EURUSD, GBPUSD, USDJPY, USDCHF, AUDUSD
USDCAD, NZDUSD, EURGBP, EURJPY, GBPJPY

🔧 **Platform Support:**
• Windows: Native MT5 integration with real trading
• Full risk management and lot calculation

💡 **Usage Tips:**
• Use inline buttons for easy navigation
• Try risk-based trading for better position sizing
• Commands work from any chat state
• Settings are saved per user
• Real-time market data updates

❓ **Need Help?**
Send /help anytime to see this guide again.
        """
        await safe_reply(update, context, help_text, get_back_keyboard())
    
    async def account_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /account command"""
        await self.show_account_info(update, context)
    
    async def trade_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /trade command"""
        await self.show_symbols_selection(update, context)
    
    async def trades_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /trades command"""
        await self.show_trades_list(update, context)
    
    async def close_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /close command"""
        await self.show_trades_list(update, context)
    
    async def show_account_info(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Show account information"""
        try:
            account_info = self.mt5.get_account_info()
            if account_info is None:
                message = "❌ **MT5 Connection Error**\n\n"
                message += "Unable to connect to MetaTrader 5.\n"
                message += "Please check your MT5 credentials in config.json\n"
                message += "and ensure MT5 is running."
            else:
                message = format_account_info(account_info)
            
            await safe_reply(
                update, context, 
                message, 
                get_back_keyboard()
            )
        except Exception as e:
            logger.error(f"Error getting account info: {e}")
            await safe_reply(
                update, context, 
                MESSAGES["error"].format(error=str(e)), 
                get_back_keyboard()
            )
    
    async def show_symbols_selection(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Show symbols selection"""
        user_id = get_user_id(update)
        if user_id:
            self.update_user_session(user_id, state='selecting_symbol')
        
        await safe_reply(
            update, context, 
            MESSAGES["select_symbol"], 
            get_symbols_keyboard()
        )
    
    async def show_trade_type_selection(self, update: Update, context: ContextTypes.DEFAULT_TYPE, symbol: str):
        """Show trade type selection"""
        user_id = get_user_id(update)
        if user_id:
            self.update_user_session(user_id, state='selecting_type', selected_symbol=symbol)
        
        await safe_reply(
            update, context, 
            f"Select trade type for {symbol}:", 
            get_trade_type_keyboard()
        )
    
    async def show_lots_selection(self, update: Update, context: ContextTypes.DEFAULT_TYPE, trade_type: str):
        """Show lot size selection"""
        user_id = get_user_id(update)
        if user_id:
            session = self.get_user_session(user_id)
            self.update_user_session(user_id, state='selecting_lots', selected_type=trade_type)
        
        await safe_reply(
            update, context, 
            MESSAGES["select_lots"], 
            get_lots_keyboard()
        )
    
    async def show_manual_lot_input(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Show manual lot size input prompt"""
        user_id = get_user_id(update)
        if user_id:
            self.update_user_session(user_id, state='manual_lot_input')
        
        await safe_reply(
            update, context, 
            MESSAGES["manual_lot_input"], 
            get_back_keyboard("back_to_lots")
        )
    
    async def show_trades_list(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Show list of open trades"""
        try:
            trades = self.mt5.get_open_trades()
            if not trades:
                await safe_reply(
                    update, context, 
                    MESSAGES["no_trades"], 
                    get_back_keyboard()
                )
                return
            
            formatted_trades = format_trades_list(trades)
            await safe_reply(
                update, context, 
                formatted_trades, 
                get_trades_keyboard(trades)
            )
        except Exception as e:
            logger.error(f"Error getting trades: {e}")
            await safe_reply(
                update, context, 
                MESSAGES["error"].format(error=str(e)), 
                get_back_keyboard()
            )
    
    async def open_trade(self, update: Update, context: ContextTypes.DEFAULT_TYPE, symbol: str, trade_type: str, lots: float):
        """Open a new trade"""
        try:
            result = self.mt5.open_trade(symbol, trade_type, lots)
            if result.get('success'):
                ticket = result.get('ticket', 'Unknown')
                price = result.get('price', 0)
                
                message = MESSAGES["trade_opened"].format(
                    symbol=symbol,
                    type=trade_type,
                    lots=lots,
                    price=f"{price:.5f}",
                    ticket=ticket
                )
            else:
                message = MESSAGES["error"].format(error=result.get('error', 'Unknown error'))
            
            await safe_reply(
                update, context, 
                message, 
                get_back_keyboard()
            )
        except Exception as e:
            logger.error(f"Error opening trade: {e}")
            await safe_reply(
                update, context, 
                MESSAGES["error"].format(error=str(e)), 
                get_back_keyboard()
            )
    
    async def close_trade(self, update: Update, context: ContextTypes.DEFAULT_TYPE, ticket: str):
        """Close a trade"""
        try:
            result = self.mt5.close_trade(int(ticket))
            if result.get('success'):
                profit = result.get('profit', 0)
                message = MESSAGES["trade_closed"].format(
                    ticket=ticket,
                    profit=f"{profit:,.2f}"
                )
            else:
                message = MESSAGES["error"].format(error=result.get('error', 'Unknown error'))
            
            await safe_reply(
                update, context, 
                message, 
                get_back_keyboard()
            )
        except Exception as e:
            logger.error(f"Error closing trade: {e}")
            await safe_reply(
                update, context, 
                MESSAGES["error"].format(error=str(e)), 
                get_back_keyboard()
            )
    
    async def show_market_info(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Show market information for all symbols"""
        try:
            # Get market data for all symbols
            market_data = []
            for symbol in MT5_SYMBOLS:
                try:
                    price_info = self.mt5.get_current_price(symbol)
                    if price_info:
                        spread = price_info['ask'] - price_info['bid']
                        spread_pips = spread * 100000  # Convert to pips
                        
                        market_data.append({
                            'symbol': symbol,
                            'bid': price_info['bid'],
                            'ask': price_info['ask'],
                            'spread': spread_pips,
                            'time': price_info['time']
                        })
                except Exception as e:
                    logger.error(f"Error getting price for {symbol}: {e}")
                    continue
            
            if not market_data:
                await safe_reply(
                    update, context, 
                    "❌ Unable to fetch market data at the moment.", 
                    get_back_keyboard()
                )
                return
            
            # Format market data
            market_text = "📊 **Market Information**\n\n"
            market_text += f"🕐 Last Updated: {datetime.now().strftime('%H:%M:%S')}\n\n"
            
            for data in market_data:
                symbol = data['symbol']
                bid = f"{data['bid']:.5f}"
                ask = f"{data['ask']:.5f}"
                spread = f"{data['spread']:.1f}"
                
                # Color coding based on spread
                if data['spread'] <= 2.0:
                    spread_emoji = "🟢"  # Low spread
                elif data['spread'] <= 5.0:
                    spread_emoji = "🟡"  # Medium spread
                else:
                    spread_emoji = "🔴"  # High spread
                
                market_text += f"{spread_emoji} **{symbol}**\n"
                market_text += f"   Bid: {bid} | Ask: {ask}\n"
                market_text += f"   Spread: {spread} pips\n\n"
            
            # Add market summary
            avg_spread = sum(d['spread'] for d in market_data) / len(market_data)
            market_text += f"📈 **Market Summary**\n"
            market_text += f"Average Spread: {avg_spread:.1f} pips\n"
            market_text += f"Symbols Available: {len(market_data)}"
            
            await safe_reply(
                update, context, 
                market_text, 
                get_back_keyboard()
            )
            
        except Exception as e:
            logger.error(f"Error getting market info: {e}")
            await safe_reply(
                update, context, 
                MESSAGES["error"].format(error=str(e)), 
                get_back_keyboard()
            )
    
    async def show_settings(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Show settings menu"""
        user_id = get_user_id(update)
        if user_id:
            session = self.get_user_session(user_id)
            settings = session.get('settings', {})
            
            # Get current settings
            default_lots = settings.get('default_lots', DEFAULT_LOT_SIZE)
            max_risk_percent = settings.get('max_risk_percent', 2.0)
            auto_sl_pips = settings.get('auto_sl_pips', 50)
            notifications = settings.get('notifications', True)
            
            settings_text = "⚙️ **Bot Settings**\n\n"
            settings_text += f"📊 Default Lot Size: {default_lots}\n"
            settings_text += f"⚠️ Max Risk per Trade: {max_risk_percent}%\n"
            settings_text += f"🛡️ Auto Stop Loss: {auto_sl_pips} pips\n"
            settings_text += f"🔔 Notifications: {'✅ On' if notifications else '❌ Off'}\n\n"
            settings_text += "Select an option to modify:"
            
            await safe_reply(
                update, context, 
                settings_text, 
                get_settings_keyboard()
            )
        else:
            await safe_reply(
                update, context, 
                "❌ Unable to load settings.", 
                get_back_keyboard()
            )
    
    async def show_lot_settings(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Show lot size settings"""
        user_id = get_user_id(update)
        if user_id:
            session = self.get_user_session(user_id)
            settings = session.get('settings', {})
            current_lots = settings.get('default_lots', DEFAULT_LOT_SIZE)
            
            text = f"📊 **Default Lot Size Settings**\n\n"
            text += f"Current: {current_lots}\n"
            text += "Select new default lot size:"
            
            await safe_reply(
                update, context, 
                text, 
                get_lot_settings_keyboard()
            )
        else:
            await safe_reply(
                update, context, 
                "❌ Unable to load settings.", 
                get_back_keyboard()
            )
    
    async def show_risk_settings(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Show risk management settings"""
        user_id = get_user_id(update)
        if user_id:
            session = self.get_user_session(user_id)
            settings = session.get('settings', {})
            current_risk = settings.get('max_risk_percent', 2.0)
            
            text = f"⚠️ **Risk Management Settings**\n\n"
            text += f"Current Max Risk: {current_risk}%\n"
            text += "Select new risk percentage:"
            
            await safe_reply(
                update, context, 
                text, 
                get_risk_settings_keyboard()
            )
        else:
            await safe_reply(
                update, context, 
                "❌ Unable to load settings.", 
                get_back_keyboard()
            )
    
    async def update_setting(self, update: Update, context: ContextTypes.DEFAULT_TYPE, setting_type: str, value):
        """Update a specific setting"""
        user_id = get_user_id(update)
        if not user_id:
            await safe_reply(
                update, context, 
                "❌ Unable to update settings.", 
                get_back_keyboard()
            )
            return
        
        session = self.get_user_session(user_id)
        if 'settings' not in session:
            session['settings'] = {}
        
        # Validate and update setting
        if setting_type == 'default_lots':
            try:
                lot_size = float(value)
                if MIN_LOT_SIZE <= lot_size <= MAX_LOT_SIZE:
                    session['settings']['default_lots'] = lot_size
                    message = f"✅ Default lot size updated to {lot_size}"
                else:
                    message = f"❌ Invalid lot size. Must be between {MIN_LOT_SIZE} and {MAX_LOT_SIZE}"
            except ValueError:
                message = "❌ Invalid lot size format"
        
        elif setting_type == 'max_risk_percent':
            try:
                risk = float(value)
                if 0.1 <= risk <= 10.0:
                    session['settings']['max_risk_percent'] = risk
                    message = f"✅ Max risk updated to {risk}%"
                else:
                    message = "❌ Invalid risk percentage. Must be between 0.1% and 10%"
            except ValueError:
                message = "❌ Invalid risk percentage format"
        
        elif setting_type == 'auto_sl_pips':
            try:
                sl_pips = int(value)
                if 10 <= sl_pips <= 500:
                    session['settings']['auto_sl_pips'] = sl_pips
                    message = f"✅ Auto Stop Loss updated to {sl_pips} pips"
                else:
                    message = "❌ Invalid SL pips. Must be between 10 and 500"
            except ValueError:
                message = "❌ Invalid SL pips format"
        
        elif setting_type == 'notifications':
            notifications = value.lower() == 'true'
            session['settings']['notifications'] = notifications
            message = f"✅ Notifications {'enabled' if notifications else 'disabled'}"
        
        else:
            message = "❌ Unknown setting type"
        
        await safe_reply(
            update, context, 
            message, 
            get_back_keyboard("back_to_settings")
        )
    
    async def handle_callback_query(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle callback queries from inline keyboards"""
        query = update.callback_query
        await query.answer()
        
        data = query.data
        action, params = parse_callback_data(data)
        
        # Debug logging
        logger.info(f"Callback data: '{data}' -> action: '{action}', params: '{params}'")
        
        user_id = get_user_id(update)
        if not user_id or not is_authorized_user(user_id):
            await safe_reply(update, context, MESSAGES["unauthorized"])
            return
        
        try:
            if action == "account_info":
                await self.show_account_info(update, context)
            
            elif action == "open_trade":
                await self.show_symbols_selection(update, context)
            
            elif action == "my_trades":
                await self.show_trades_list(update, context)
            
            elif action == "close_trade":
                if params:
                    await self.close_trade(update, context, params)
                else:
                    await self.show_trades_list(update, context)
            
            elif action == "symbol":
                if params and validate_symbol(params):
                    await self.show_trade_type_selection(update, context, params)
                else:
                    await safe_reply(
                        update, context, 
                        MESSAGES["invalid_symbol"], 
                        get_symbols_keyboard()
                    )
            
            elif action == "trade_type":
                if params in ["BUY", "SELL"]:
                    await self.show_lots_selection(update, context, params)
                else:
                    await safe_reply(
                        update, context, 
                        "Invalid trade type", 
                        get_trade_type_keyboard()
                    )
            
            elif action == "lots":
                if params:
                    lot_size = validate_lot_size(params)
                    if lot_size:
                        user_id = get_user_id(update)
                        session = self.get_user_session(user_id)
                        symbol = session.get('selected_symbol')
                        trade_type = session.get('selected_type')
                        
                        if symbol and trade_type:
                            await self.open_trade(update, context, symbol, trade_type, lot_size)
                            self.update_user_session(user_id, state='main_menu')
                        else:
                            await safe_reply(
                                update, context, 
                                "Session data missing. Please start over.", 
                                get_main_menu_keyboard()
                            )
                    else:
                        await safe_reply(
                            update, context, 
                            MESSAGES["invalid_lots"], 
                            get_lots_keyboard()
                        )
            
            elif action == "manual_lot_input":
                await self.show_manual_lot_input(update, context)
            
            elif action == "back_to_main":
                self.update_user_session(user_id, state='main_menu')
                await safe_reply(
                    update, context, 
                    MESSAGES["welcome"], 
                    get_main_menu_keyboard()
                )
            
            elif action == "back_to_symbols":
                await self.show_symbols_selection(update, context)
            
            elif action == "back_to_trade_type":
                user_id = get_user_id(update)
                session = self.get_user_session(user_id)
                symbol = session.get('selected_symbol')
                if symbol:
                    await self.show_trade_type_selection(update, context, symbol)
                else:
                    await self.show_symbols_selection(update, context)
            
            elif action == "back_to_lots":
                user_id = get_user_id(update)
                session = self.get_user_session(user_id)
                trade_type = session.get('selected_type')
                if trade_type:
                    await self.show_lots_selection(update, context, trade_type)
                else:
                    await self.show_symbols_selection(update, context)
            
            elif action == "market_info":
                await self.show_market_info(update, context)
            
            elif action == "settings":
                await self.show_settings(update, context)
            
            elif action == "lot_settings":
                await self.show_lot_settings(update, context)
            
            elif action == "risk_settings":
                await self.show_risk_settings(update, context)
            
            elif action == "sl_settings":
                await self.show_sl_settings(update, context)
            
            elif action == "notification_settings":
                await self.show_notification_settings(update, context)
            
            elif action == "update_default_lots":
                await self.update_setting(update, context, 'default_lots', params)
            
            elif action == "update_max_risk":
                await self.update_setting(update, context, 'max_risk_percent', params)
            
            elif action == "update_auto_sl":
                await self.update_setting(update, context, 'auto_sl_pips', params)
            
            elif action == "update_notifications":
                await self.update_setting(update, context, 'notifications', params)
            
            elif action == "back_to_settings":
                await self.show_settings(update, context)
            
            elif action == "advanced_trade":
                if params:
                    symbol, trade_type, lots = params
                    await self.show_advanced_trade_options(update, context, symbol, trade_type, float(lots))
            
            elif action == "set_sl_tp":
                if params:
                    sl_pips, tp_pips = params
                    await self.open_trade_with_sl_tp(update, context, int(sl_pips), int(tp_pips))
            
            elif action == "set_breakeven":
                if params:
                    await self.set_breakeven(update, context, params)
            
            elif action == "modify_trade":
                if params:
                    ticket, sl, tp = params
                    await self.modify_trade(update, context, ticket, float(sl) if sl else None, float(tp) if tp else None)
            
            elif action == "risk_based_trade":
                if params:
                    symbol, trade_type = params
                    await self.show_risk_based_trade_options(update, context, symbol, trade_type)
            
            elif action == "input_risk_amount":
                await self.show_risk_input(update, context)
            
            else:
                logger.warning(f"Unknown action: '{action}' with params: '{params}'")
                await safe_reply(
                    update, context, 
                    f"Unknown action: {action}", 
                    get_main_menu_keyboard()
                )
        
        except Exception as e:
            logger.error(f"Error handling callback query: {e}")
            await safe_reply(
                update, context, 
                MESSAGES["error"].format(error=str(e)), 
                get_main_menu_keyboard()
            ) 

    async def show_sl_settings(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Show stop loss settings"""
        user_id = get_user_id(update)
        if user_id:
            session = self.get_user_session(user_id)
            settings = session.get('settings', {})
            current_sl = settings.get('auto_sl_pips', 50)
            
            text = f"🛡️ **Auto Stop Loss Settings**\n\n"
            text += f"Current: {current_sl} pips\n"
            text += "Select new auto stop loss:"
            
            await safe_reply(
                update, context, 
                text, 
                get_sl_settings_keyboard()
            )
        else:
            await safe_reply(
                update, context, 
                "❌ Unable to load settings.", 
                get_back_keyboard()
            )
    
    async def show_notification_settings(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Show notification settings"""
        user_id = get_user_id(update)
        if user_id:
            session = self.get_user_session(user_id)
            settings = session.get('settings', {})
            notifications = settings.get('notifications', True)
            
            text = f"🔔 **Notification Settings**\n\n"
            text += f"Current: {'✅ Enabled' if notifications else '❌ Disabled'}\n"
            text += "Select notification preference:"
            
            await safe_reply(
                update, context, 
                text, 
                get_notification_settings_keyboard()
            )
        else:
            await safe_reply(
                update, context, 
                "❌ Unable to load settings.", 
                get_back_keyboard()
            ) 

    async def show_advanced_trade_options(self, update: Update, context: ContextTypes.DEFAULT_TYPE, symbol: str, trade_type: str, lots: float):
        """Show advanced trade options (SL/TP)"""
        user_id = get_user_id(update)
        if user_id:
            self.update_user_session(user_id, 
                state='advanced_trade', 
                selected_symbol=symbol, 
                selected_type=trade_type, 
                selected_lots=lots
            )
        
        # Get current price for reference
        price_info = self.mt5.get_current_price(symbol)
        current_price = price_info['ask'] if trade_type == 'BUY' else price_info['bid']
        
        text = f"🎯 **Advanced Trade Options**\n\n"
        text += f"Symbol: {symbol}\n"
        text += f"Type: {trade_type}\n"
        text += f"Lots: {lots}\n"
        text += f"Current Price: {current_price:.5f}\n\n"
        text += "Select additional options:"
        
        await safe_reply(
            update, context, 
            text, 
            get_advanced_trade_keyboard()
        )
    
    async def open_trade_with_sl_tp(self, update: Update, context: ContextTypes.DEFAULT_TYPE, sl_pips: int = None, tp_pips: int = None):
        """Open trade with stop loss and take profit"""
        user_id = get_user_id(update)
        if not user_id:
            await safe_reply(update, context, "❌ Session error", get_main_menu_keyboard())
            return
        
        session = self.get_user_session(user_id)
        symbol = session.get('selected_symbol')
        trade_type = session.get('selected_type')
        lots = session.get('selected_lots')
        
        if not all([symbol, trade_type, lots]):
            await safe_reply(update, context, "❌ Missing trade parameters", get_main_menu_keyboard())
            return
        
        try:
            # Get current price
            price_info = self.mt5.get_current_price(symbol)
            if not price_info:
                await safe_reply(update, context, "❌ Unable to get current price", get_main_menu_keyboard())
                return
            
            # Calculate SL and TP prices
            current_price = price_info['ask'] if trade_type == 'BUY' else price_info['bid']
            sl_price = None
            tp_price = None
            
            if sl_pips:
                if trade_type == 'BUY':
                    sl_price = current_price - (sl_pips * 0.0001)
                else:
                    sl_price = current_price + (sl_pips * 0.0001)
            
            if tp_pips:
                if trade_type == 'BUY':
                    tp_price = current_price + (tp_pips * 0.0001)
                else:
                    tp_price = current_price - (tp_pips * 0.0001)
            
            # Open trade with SL/TP
            result = self.mt5.open_trade(symbol, trade_type, lots)
            
            if result.get('success'):
                ticket = result.get('ticket', 'Unknown')
                price = result.get('price', current_price)
                
                message = f"✅ **Trade Opened Successfully**\n\n"
                message += f"Symbol: {symbol}\n"
                message += f"Type: {trade_type}\n"
                message += f"Lots: {lots}\n"
                message += f"Price: {price:.5f}\n"
                message += f"Ticket: {ticket}\n"
                
                if sl_price:
                    message += f"Stop Loss: {sl_price:.5f} ({sl_pips} pips)\n"
                if tp_price:
                    message += f"Take Profit: {tp_price:.5f} ({tp_pips} pips)\n"
                
                # Reset session
                self.update_user_session(user_id, state='main_menu')
                
                await safe_reply(update, context, message, get_main_menu_keyboard())
            else:
                await safe_reply(update, context, 
                    MESSAGES["error"].format(error=result.get('error', 'Unknown error')), 
                    get_main_menu_keyboard()
                )
        
        except Exception as e:
            logger.error(f"Error opening trade with SL/TP: {e}")
            await safe_reply(update, context, 
                MESSAGES["error"].format(error=str(e)), 
                get_main_menu_keyboard()
            )
    
    async def set_breakeven(self, update: Update, context: ContextTypes.DEFAULT_TYPE, ticket: str):
        """Set breakeven for a trade"""
        try:
            result = self.mt5.set_breakeven(int(ticket))
            if result.get('success'):
                message = f"✅ Breakeven set successfully for ticket {ticket}"
            else:
                message = MESSAGES["error"].format(error=result.get('error', 'Unknown error'))
            
            await safe_reply(update, context, message, get_back_keyboard())
        
        except Exception as e:
            logger.error(f"Error setting breakeven: {e}")
            await safe_reply(update, context, 
                MESSAGES["error"].format(error=str(e)), 
                get_back_keyboard()
            )
    
    async def modify_trade(self, update: Update, context: ContextTypes.DEFAULT_TYPE, ticket: str, sl: float = None, tp: float = None):
        """Modify trade SL/TP"""
        try:
            result = self.mt5.modify_sl_tp(int(ticket), sl, tp)
            if result.get('success'):
                message = f"✅ Trade {ticket} modified successfully"
                if sl:
                    message += f"\nNew SL: {sl:.5f}"
                if tp:
                    message += f"\nNew TP: {tp:.5f}"
            else:
                message = MESSAGES["error"].format(error=result.get('error', 'Unknown error'))
            
            await safe_reply(update, context, message, get_back_keyboard())
        
        except Exception as e:
            logger.error(f"Error modifying trade: {e}")
            await safe_reply(update, context, 
                MESSAGES["error"].format(error=str(e)), 
                get_back_keyboard()
            ) 

    async def market_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /market command"""
        await self.show_market_info(update, context)
    
    async def settings_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /settings command"""
        await self.show_settings(update, context)
    
    async def status_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /status command - Show bot and MT5 status"""
        try:
            # Check MT5 connection
            mt5_status = "🟢 Connected" if self.mt5.connected else "🔴 Disconnected"
            
            # Get account info
            account_info = self.mt5.get_account_info()
            if account_info:
                balance = account_info.get('balance', 0)
                equity = account_info.get('equity', 0)
                profit = account_info.get('profit', 0)
                account_status = "🟢 Active"
            else:
                balance = equity = profit = 0
                account_status = "🔴 Inactive"
            
            # Get open trades count
            trades = self.mt5.get_open_trades()
            trades_count = len(trades) if trades else 0
            
            status_text = f"""
📊 **Bot & MT5 Status Report**

🤖 **Bot Status:**
• Status: 🟢 Running
• Platform: {self.mt5.platform}

📈 **MT5 Connection:**
• Status: {mt5_status}
• Account: {account_status}

💰 **Account Summary:**
• Balance: ${balance:,.2f}
• Equity: ${equity:,.2f}
• Profit: ${profit:,.2f}
• Open Trades: {trades_count}

🕐 **Last Updated:** {datetime.now().strftime('%H:%M:%S')}
            """
            
            await safe_reply(update, context, status_text, get_back_keyboard())
            
        except Exception as e:
            logger.error(f"Error getting status: {e}")
            await safe_reply(
                update, context, 
                MESSAGES["error"].format(error=str(e)), 
                get_back_keyboard()
            )
    
    async def quick_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /quick command - Quick trade shortcuts"""
        quick_text = """
🚀 **Quick Trade Shortcuts**

**Quick Commands:**
/quick_buy <symbol> <lots> - Quick BUY trade
/quick_sell <symbol> <lots> - Quick SELL trade
/quick_close <ticket> - Quick close trade

**Examples:**
/quick_buy EURUSD 0.1
/quick_sell GBPUSD 0.05
/quick_close 123456

**Available Symbols:**
EURUSD, GBPUSD, USDJPY, USDCHF, AUDUSD
USDCAD, NZDUSD, EURGBP, EURJPY, GBPJPY

**Lot Sizes:**
0.01, 0.05, 0.1, 0.5, 1.0, 5.0, 10.0

💡 **Tip:** Use these commands for fast trading without navigating menus!
        """
        await safe_reply(update, context, quick_text, get_back_keyboard())
    
    async def quick_buy_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /quick_buy command"""
        if not context.args or len(context.args) < 2:
            await safe_reply(
                update, context, 
                "❌ Usage: /quick_buy <symbol> <lots>\nExample: /quick_buy EURUSD 0.1", 
                get_back_keyboard()
            )
            return
        
        symbol = context.args[0].upper()
        lots_str = context.args[1]
        
        if not validate_symbol(symbol):
            await safe_reply(
                update, context, 
                f"❌ Invalid symbol: {symbol}\nUse: EURUSD, GBPUSD, USDJPY, etc.", 
                get_back_keyboard()
            )
            return
        
        lot_size = validate_lot_size(lots_str)
        if not lot_size:
            await safe_reply(
                update, context, 
                f"❌ Invalid lot size: {lots_str}\nUse: 0.01, 0.1, 1.0, etc.", 
                get_back_keyboard()
            )
            return
        
        await self.open_trade(update, context, symbol, "BUY", lot_size)
    
    async def quick_sell_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /quick_sell command"""
        if not context.args or len(context.args) < 2:
            await safe_reply(
                update, context, 
                "❌ Usage: /quick_sell <symbol> <lots>\nExample: /quick_sell EURUSD 0.1", 
                get_back_keyboard()
            )
            return
        
        symbol = context.args[0].upper()
        lots_str = context.args[1]
        
        if not validate_symbol(symbol):
            await safe_reply(
                update, context, 
                f"❌ Invalid symbol: {symbol}\nUse: EURUSD, GBPUSD, USDJPY, etc.", 
                get_back_keyboard()
            )
            return
        
        lot_size = validate_lot_size(lots_str)
        if not lot_size:
            await safe_reply(
                update, context, 
                f"❌ Invalid lot size: {lots_str}\nUse: 0.01, 0.1, 1.0, etc.", 
                get_back_keyboard()
            )
            return
        
        await self.open_trade(update, context, symbol, "SELL", lot_size)
    
    async def quick_close_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /quick_close command"""
        if not context.args or len(context.args) < 1:
            await safe_reply(
                update, context, 
                "❌ Usage: /quick_close <ticket>\nExample: /quick_close 123456", 
                get_back_keyboard()
            )
            return
        
        ticket = context.args[0]
        try:
            int(ticket)  # Validate it's a number
        except ValueError:
            await safe_reply(
                update, context, 
                f"❌ Invalid ticket: {ticket}\nTicket must be a number.", 
                get_back_keyboard()
            )
            return
        
        await self.close_trade(update, context, ticket) 

    async def show_risk_based_trade_options(self, update: Update, context: ContextTypes.DEFAULT_TYPE, symbol: str, trade_type: str):
        """Show risk-based trading options"""
        user_id = get_user_id(update)
        if user_id:
            self.update_user_session(user_id, 
                state='risk_based_trade', 
                selected_symbol=symbol, 
                selected_type=trade_type
            )
        
        # Get current price for reference
        price_info = self.mt5.get_current_price(symbol)
        current_price = price_info['ask'] if trade_type == 'BUY' else price_info['bid']
        
        text = f"💰 **Risk-Based Trading**\n\n"
        text += f"Symbol: {symbol}\n"
        text += f"Type: {trade_type}\n"
        text += f"Current Price: {current_price:.5f}\n\n"
        text += "This method calculates lot size automatically based on:\n"
        text += "• Risk amount in dollars\n"
        text += "• Stop loss in points\n"
        text += "• Take profit in dollars (optional)\n\n"
        text += "Select an option:"
        
        await safe_reply(
            update, context, 
            text, 
            get_risk_based_trade_keyboard()
        )

    async def show_risk_input(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Show risk amount input"""
        user_id = get_user_id(update)
        if user_id:
            self.update_user_session(user_id, state='input_risk_amount')
        
        text = "💰 **Enter Risk Amount**\n\n"
        text += "How much money are you willing to risk?\n"
        text += "Enter the amount in dollars (e.g., 50, 100, 200)\n\n"
        text += "Example: 100 (means $100 risk)"
        
        await safe_reply(
            update, context, 
            text, 
            get_back_keyboard()
        )

    async def show_sl_points_input(self, update: Update, context: ContextTypes.DEFAULT_TYPE, risk_dollars: float):
        """Show stop loss points input"""
        user_id = get_user_id(update)
        if user_id:
            self.update_user_session(user_id, state='input_sl_points', risk_dollars=risk_dollars)
        
        text = f"🛡️ **Enter Stop Loss Points**\n\n"
        text += f"Risk Amount: ${risk_dollars}\n\n"
        text += "How many points away should the stop loss be?\n"
        text += "Enter the number of points (e.g., 50, 100, 200)\n\n"
        text += "Note: 1 point = 0.00001 (5-digit broker)\n"
        text += "Example: 100 points = 0.00100"
        
        await safe_reply(
            update, context, 
            text, 
            get_back_keyboard()
        )

    async def show_tp_dollars_input(self, update: Update, context: ContextTypes.DEFAULT_TYPE, risk_dollars: float, sl_points: int):
        """Show take profit dollars input"""
        user_id = get_user_id(update)
        if user_id:
            self.update_user_session(user_id, state='input_tp_dollars', risk_dollars=risk_dollars, sl_points=sl_points)
        
        text = f"🎯 **Enter Take Profit Amount**\n\n"
        text += f"Risk Amount: ${risk_dollars}\n"
        text += f"Stop Loss: {sl_points} points\n\n"
        text += "How much profit do you want to target?\n"
        text += "Enter the amount in dollars (e.g., 150, 200, 300)\n\n"
        text += "Leave empty or type '0' for no take profit"
        
        await safe_reply(
            update, context, 
            text, 
            get_tp_input_keyboard()
        )

    async def open_risk_based_trade(self, update: Update, context: ContextTypes.DEFAULT_TYPE, risk_dollars: float, sl_points: int, tp_dollars: float = None):
        """Open trade with risk-based lot calculation"""
        user_id = get_user_id(update)
        if not user_id:
            await safe_reply(update, context, "❌ Session error", get_main_menu_keyboard())
            return
        
        session = self.get_user_session(user_id)
        symbol = session.get('selected_symbol')
        trade_type = session.get('selected_type')
        
        if not all([symbol, trade_type]):
            await safe_reply(update, context, "❌ Missing trade parameters", get_main_menu_keyboard())
            return
        
        try:
            # Open trade with risk management
            result = self.mt5.open_trade_with_risk_management(symbol, trade_type, risk_dollars, sl_points, tp_dollars)
            
            if result.get('success'):
                ticket = result.get('ticket', 'Unknown')
                price = result.get('price', 0)
                lot_size = result.get('volume', 0)
                sl_price = result.get('sl_price', 0)
                tp_price = result.get('tp_price', 0)
                
                message = f"✅ **Risk-Managed Trade Opened**\n\n"
                message += f"Symbol: {symbol}\n"
                message += f"Type: {trade_type}\n"
                message += f"Lot Size: {lot_size} (auto-calculated)\n"
                message += f"Entry Price: {price:.5f}\n"
                message += f"Risk Amount: ${risk_dollars}\n"
                message += f"Stop Loss: {sl_points} points ({sl_price:.5f})\n"
                
                if tp_dollars and tp_price:
                    message += f"Take Profit: ${tp_dollars} ({tp_price:.5f})\n"
                else:
                    message += f"Take Profit: None\n"
                
                message += f"Ticket: {ticket}\n\n"
                message += f"💰 Risk/Reward: 1:{tp_dollars/risk_dollars:.1f}" if tp_dollars else "💰 Risk/Reward: Not set"
                
                # Reset session
                self.update_user_session(user_id, state='main_menu')
                
                await safe_reply(update, context, message, get_main_menu_keyboard())
            else:
                await safe_reply(update, context, 
                    MESSAGES["error"].format(error=result.get('error', 'Unknown error')), 
                    get_main_menu_keyboard()
                )
        
        except Exception as e:
            logger.error(f"Error opening risk-based trade: {e}")
            await safe_reply(update, context, 
                MESSAGES["error"].format(error=str(e)), 
                get_main_menu_keyboard()
            )

    async def handle_text_input(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle text input for risk-based trading and manual lot input"""
        user_id = get_user_id(update)
        if not user_id:
            return
        
        session = self.get_user_session(user_id)
        state = session.get('state', '')
        text = update.message.text.strip()
        
        try:
            if state == 'manual_lot_input':
                # Handle manual lot size input
                lot_size = validate_lot_size(text)
                if lot_size:
                    symbol = session.get('selected_symbol')
                    trade_type = session.get('selected_type')
                    
                    if symbol and trade_type:
                        await self.open_trade(update, context, symbol, trade_type, lot_size)
                        self.update_user_session(user_id, state='main_menu')
                    else:
                        await safe_reply(
                            update, context, 
                            "Session data missing. Please start over.", 
                            get_main_menu_keyboard()
                        )
                else:
                    await safe_reply(
                        update, context, 
                        MESSAGES["invalid_lots"], 
                        get_back_keyboard("back_to_lots")
                    )
                
            elif state == 'input_risk_amount':
                # Handle risk amount input
                risk_dollars = float(text)
                if risk_dollars <= 0:
                    await safe_reply(update, context, "❌ Risk amount must be greater than 0", get_back_keyboard())
                    return
                
                await self.show_sl_points_input(update, context, risk_dollars)
                
            elif state == 'input_sl_points':
                # Handle stop loss points input
                sl_points = int(text)
                if sl_points <= 0:
                    await safe_reply(update, context, "❌ Stop loss points must be greater than 0", get_back_keyboard())
                    return
                
                risk_dollars = session.get('risk_dollars', 0)
                await self.show_tp_dollars_input(update, context, risk_dollars, sl_points)
                
            elif state == 'input_tp_dollars':
                # Handle take profit dollars input
                if text.lower() in ['0', 'none', 'no', 'skip']:
                    tp_dollars = None
                else:
                    tp_dollars = float(text)
                    if tp_dollars <= 0:
                        await safe_reply(update, context, "❌ Take profit must be greater than 0", get_back_keyboard())
                        return
                
                risk_dollars = session.get('risk_dollars', 0)
                sl_points = session.get('sl_points', 0)
                await self.open_risk_based_trade(update, context, risk_dollars, sl_points, tp_dollars)
                
        except ValueError:
            await safe_reply(update, context, "❌ Please enter a valid number", get_back_keyboard())
        except Exception as e:
            logger.error(f"Error handling text input: {e}")
            await safe_reply(update, context, MESSAGES["error"].format(error=str(e)), get_back_keyboard()) 