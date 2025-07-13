#!/usr/bin/env python3
"""
MT5 Bridge - Windows Only (Real MetaTrader 5 Trading Interface)
This module provides real MT5 functionality for trading on Windows only.
"""

import sys
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

class MT5Bridge:
    """Windows-only MT5 bridge for live trading"""
    def __init__(self):
        self.connected = False
        self.platform = sys.platform
        self.mt5 = None
        self._init_mt5()

    def _init_mt5(self):
        if not self.platform.startswith('win'):
            logger.error("This bot only works on Windows with MetaTrader 5 installed.")
            raise SystemExit("❌ This bot only works on Windows with MetaTrader 5 installed and the MetaTrader5 Python package.")
        try:
            import MetaTrader5 as mt5
            self.mt5 = mt5
            self._connect_mt5()
        except ImportError:
            logger.error("MetaTrader5 Python package not found. Please install: pip install MetaTrader5")
            raise SystemExit("❌ MetaTrader5 Python package not found. Please install it on Windows: pip install MetaTrader5")

    def _connect_mt5(self):
        from config.settings import config
        mt5_login = config.get('mt5_login')
        mt5_password = config.get('mt5_password')
        mt5_server = config.get('mt5_server')
        if not mt5_login or not mt5_password or not mt5_server:
            logger.error("MT5 credentials not found in config.json")
            raise SystemExit("❌ MT5 credentials not found in config.json")
        logger.info(f"Initializing MT5 connection to {mt5_server}")
        if not self.mt5.initialize():
            logger.error(f"MT5 initialize() failed: {self.mt5.last_error()}")
            raise SystemExit(f"❌ MT5 initialize() failed: {self.mt5.last_error()}")
        if not self.mt5.login(login=mt5_login, password=mt5_password, server=mt5_server):
            logger.error(f"MT5 login failed: {self.mt5.last_error()}")
            raise SystemExit(f"❌ MT5 login failed: {self.mt5.last_error()}")
        self.connected = True
        logger.info("MT5 connection established successfully")

    def initialize(self):
        if not self.connected and self.mt5:
            self._connect_mt5()
        return self.connected

    def get_account_info(self):
        if not self.connected:
            self.initialize()
        info = self.mt5.account_info()
        if info:
            return {
                'balance': info.balance,
                'equity': info.equity,
                'margin': info.margin,
                'free_margin': info.margin_free,
                'currency': getattr(info, 'currency', 'USD'),
                'profit': info.profit
            }
        else:
            logger.error(f"MT5 account_info() failed: {self.mt5.last_error()}")
            return None

    def get_symbol_info(self, symbol):
        info = self.mt5.symbol_info(symbol)
        if info:
            return {
                'point': info.point,
                'digits': info.digits,
                'spread': info.spread,
                'trade_mode': info.trade_mode,
                'volume_min': info.volume_min,
                'volume_max': info.volume_max,
                'volume_step': info.volume_step
            }
        else:
            logger.error(f"MT5 symbol_info() failed for {symbol}: {self.mt5.last_error()}")
            return None

    def get_current_price(self, symbol):
        tick = self.mt5.symbol_info_tick(symbol)
        if tick:
            return {
                'bid': tick.bid,
                'ask': tick.ask,
                'last': tick.last,
                'time': datetime.fromtimestamp(tick.time)
            }
        else:
            logger.error(f"MT5 symbol_info_tick() failed for {symbol}: {self.mt5.last_error()}")
            return None

    def calculate_lot_size(self, symbol, risk_percent, sl_pips, account_balance):
        try:
            symbol_info = self.get_symbol_info(symbol)
            if not symbol_info:
                return None
            risk_amount = account_balance * (risk_percent / 100)
            pip_value = symbol_info['point'] * 10
            sl_distance = sl_pips * pip_value
            lot_size = risk_amount / (sl_distance * 100000)
            lot_size = round(lot_size / symbol_info['volume_step']) * symbol_info['volume_step']
            lot_size = max(symbol_info['volume_min'], min(lot_size, symbol_info['volume_max']))
            return lot_size
        except Exception as e:
            logger.error(f"Error calculating lot size: {e}")
            return None

    def calculate_lot_size_by_risk(self, symbol, risk_dollars, sl_points):
        """
        Calculate lot size based on risk in dollars and stop loss in points
        
        Args:
            symbol: Trading symbol (e.g., 'EURUSD')
            risk_dollars: Maximum risk amount in dollars
            sl_points: Stop loss distance in points (1 point = 0.00001 for 5-digit brokers)
        
        Returns:
            float: Calculated lot size
        """
        try:
            # Get symbol information
            symbol_info = self.get_symbol_info(symbol)
            if not symbol_info:
                logger.error(f"Unable to get symbol info for {symbol}")
                return None
            
            # Get current price for pip value calculation
            price_info = self.get_current_price(symbol)
            if not price_info:
                logger.error(f"Unable to get current price for {symbol}")
                return None
            
            current_price = price_info['ask']  # Use ask price for calculation
            
            # Calculate pip value
            # For most forex pairs: 1 pip = 0.0001 (4th decimal)
            # For JPY pairs: 1 pip = 0.01 (2nd decimal)
            pip_size = 0.0001 if 'JPY' not in symbol else 0.01
            
            # Calculate point value (1 point = 0.00001 for 5-digit brokers)
            point_size = 0.00001 if 'JPY' not in symbol else 0.001
            
            # Calculate point value per lot
            # For standard lot (100,000 units): 1 point = $1 for most pairs
            # For JPY pairs: 1 point = $0.1 for standard lot
            if 'JPY' in symbol:
                point_value_per_lot = 0.1  # $0.1 per point per standard lot for JPY pairs
            else:
                point_value_per_lot = 1.0  # $1 per point per standard lot for other pairs
            
            # Calculate lot size based on risk
            # Formula: Lot Size = Risk Amount / (SL Points × Point Value per Lot)
            lot_size = risk_dollars / (sl_points * point_value_per_lot)
            
            # Round to valid lot step
            lot_size = round(lot_size / symbol_info['volume_step']) * symbol_info['volume_step']
            
            # Ensure lot size is within valid range
            lot_size = max(symbol_info['volume_min'], min(lot_size, symbol_info['volume_max']))
            
            logger.info(f"Calculated lot size: {lot_size} for {symbol} with ${risk_dollars} risk and {sl_points} points SL")
            return lot_size
            
        except Exception as e:
            logger.error(f"Error calculating lot size by risk: {e}")
            return None

    def calculate_tp_price(self, symbol, trade_type, entry_price, tp_dollars, lot_size):
        """
        Calculate take profit price based on dollar amount
        
        Args:
            symbol: Trading symbol
            trade_type: 'BUY' or 'SELL'
            entry_price: Entry price of the trade
            tp_dollars: Take profit amount in dollars
            lot_size: Lot size of the trade
        
        Returns:
            float: Take profit price
        """
        try:
            # Get symbol information
            symbol_info = self.get_symbol_info(symbol)
            if not symbol_info:
                return None
            
            # Calculate point value per lot (same as in lot calculation)
            if 'JPY' in symbol:
                point_value_per_lot = 0.1  # $0.1 per point per standard lot for JPY pairs
            else:
                point_value_per_lot = 1.0  # $1 per point per standard lot for other pairs
            
            # Calculate points needed for TP
            points_needed = tp_dollars / (lot_size * point_value_per_lot)
            
            # Calculate TP price
            point_size = 0.00001 if 'JPY' not in symbol else 0.001
            if trade_type == 'BUY':
                tp_price = entry_price + (points_needed * point_size)
            else:  # SELL
                tp_price = entry_price - (points_needed * point_size)
            
            return tp_price
            
        except Exception as e:
            logger.error(f"Error calculating TP price: {e}")
            return None

    def open_trade(self, symbol, trade_type, lots):
        """
        Open a basic trade without SL/TP
        
        Args:
            symbol: Trading symbol
            trade_type: 'BUY' or 'SELL'
            lots: Lot size
        
        Returns:
            dict: Trade result
        """
        if not self.connected:
            self.initialize()
        
        try:
            # Get current price
            price_info = self.get_current_price(symbol)
            if not price_info:
                return {'success': False, 'error': 'Unable to get current price'}
            
            # Determine entry price and order type
            if trade_type == 'BUY':
                order_type = self.mt5.ORDER_TYPE_BUY
                entry_price = price_info['ask']
            else:
                order_type = self.mt5.ORDER_TYPE_SELL
                entry_price = price_info['bid']
            
            # Prepare order request
            request = {
                "action": self.mt5.TRADE_ACTION_DEAL,
                "symbol": symbol,
                "volume": lots,
                "type": order_type,
                "price": entry_price,
                "deviation": 10,
                "magic": 234000,
                "comment": "TelegramBot Trade",
                "type_time": self.mt5.ORDER_TIME_GTC,
                "type_filling": self.mt5.ORDER_FILLING_IOC,
            }
            
            # Send order
            result = self.mt5.order_send(request)
            if result and result.retcode == self.mt5.TRADE_RETCODE_DONE:
                logger.info(f"Trade opened: {symbol} {trade_type} {lots} lots")
                return {
                    'success': True,
                    'ticket': result.order,
                    'price': entry_price,
                    'volume': lots,
                    'symbol': symbol,
                    'type': trade_type
                }
            else:
                error_msg = f"Order failed: {result.retcode} - {result.comment}" if result else "Unknown error"
                logger.error(f"Trade opening failed: {error_msg}")
                return {'success': False, 'error': error_msg}
                
        except Exception as e:
            logger.error(f"Error opening trade: {e}")
            return {'success': False, 'error': str(e)}

    def open_trade_with_risk_management(self, symbol, trade_type, risk_dollars, sl_points, tp_dollars=None):
        """
        Open trade with risk-based lot calculation and dollar-based TP
        
        Args:
            symbol: Trading symbol
            trade_type: 'BUY' or 'SELL'
            risk_dollars: Maximum risk amount in dollars
            sl_points: Stop loss distance in points
            tp_dollars: Take profit amount in dollars (optional)
        
        Returns:
            dict: Trade result
        """
        if not self.connected:
            self.initialize()
        
        try:
            # Calculate lot size based on risk
            lot_size = self.calculate_lot_size_by_risk(symbol, risk_dollars, sl_points)
            if not lot_size:
                return {'success': False, 'error': 'Unable to calculate lot size'}
            
            # Get current price
            price_info = self.get_current_price(symbol)
            if not price_info:
                return {'success': False, 'error': 'Unable to get current price'}
            
            # Determine entry price
            if trade_type == 'BUY':
                order_type = self.mt5.ORDER_TYPE_BUY
                entry_price = price_info['ask']
            else:
                order_type = self.mt5.ORDER_TYPE_SELL
                entry_price = price_info['bid']
            
            # Calculate SL price
            point_size = 0.00001 if 'JPY' not in symbol else 0.001
            if trade_type == 'BUY':
                sl_price = entry_price - (sl_points * point_size)
            else:
                sl_price = entry_price + (sl_points * point_size)
            
            # Calculate TP price if specified
            tp_price = None
            if tp_dollars:
                tp_price = self.calculate_tp_price(symbol, trade_type, entry_price, tp_dollars, lot_size)
            
            # Prepare order request
            request = {
                "action": self.mt5.TRADE_ACTION_DEAL,
                "symbol": symbol,
                "volume": lot_size,
                "type": order_type,
                "price": entry_price,
                "sl": sl_price,
                "tp": tp_price,
                "deviation": 10,
                "magic": 234000,
                "comment": f"RiskBot: ${risk_dollars} risk, {sl_points} pts SL",
                "type_time": self.mt5.ORDER_TIME_GTC,
                "type_filling": self.mt5.ORDER_FILLING_IOC,
            }
            
            # Send order
            result = self.mt5.order_send(request)
            if result and result.retcode == self.mt5.TRADE_RETCODE_DONE:
                logger.info(f"Risk-managed trade opened: {symbol} {trade_type} {lot_size} lots, ${risk_dollars} risk")
                return {
                    'success': True,
                    'ticket': result.order,
                    'price': entry_price,
                    'volume': lot_size,
                    'symbol': symbol,
                    'type': trade_type,
                    'sl_price': sl_price,
                    'tp_price': tp_price,
                    'risk_dollars': risk_dollars,
                    'sl_points': sl_points,
                    'tp_dollars': tp_dollars
                }
            else:
                error_msg = f"Order failed: {result.retcode} - {result.comment}" if result else "Unknown error"
                logger.error(f"Risk-managed trade opening failed: {error_msg}")
                return {'success': False, 'error': error_msg}
                
        except Exception as e:
            logger.error(f"Error opening risk-managed trade: {e}")
            return {'success': False, 'error': str(e)}

    def close_trade(self, ticket):
        if not self.connected:
            self.initialize()
        try:
            positions = self.mt5.positions_get(ticket=int(ticket))
            if not positions:
                return {'success': False, 'error': 'Position not found'}
            position = positions[0]
            if position.type == self.mt5.POSITION_TYPE_BUY:
                order_type = self.mt5.ORDER_TYPE_SELL
                price = self.get_current_price(position.symbol)['bid']
            else:
                order_type = self.mt5.ORDER_TYPE_BUY
                price = self.get_current_price(position.symbol)['ask']
            request = {
                "action": self.mt5.TRADE_ACTION_DEAL,
                "symbol": position.symbol,
                "volume": position.volume,
                "type": order_type,
                "position": position.ticket,
                "price": price,
                "deviation": 10,
                "magic": 234000,
                "comment": "TelegramBot Close",
                "type_time": self.mt5.ORDER_TIME_GTC,
                "type_filling": self.mt5.ORDER_FILLING_IOC,
            }
            result = self.mt5.order_send(request)
            if result and result.retcode == self.mt5.TRADE_RETCODE_DONE:
                logger.info(f"Trade closed successfully: Ticket {ticket}")
                return {
                    'success': True, 
                    'profit': position.profit,
                    'ticket': ticket
                }
            else:
                error_msg = f"Close failed: {result.retcode} - {result.comment}" if result else "Unknown error"
                logger.error(f"Trade closing failed: {error_msg}")
                return {'success': False, 'error': error_msg}
        except Exception as e:
            logger.error(f"Error closing trade: {e}")
            return {'success': False, 'error': str(e)}

    def get_open_trades(self):
        if not self.connected:
            self.initialize()
        positions = self.mt5.positions_get()
        trades = []
        if positions:
            for pos in positions:
                trades.append({
                    'ticket': pos.ticket,
                    'symbol': pos.symbol,
                    'type': 'BUY' if pos.type == self.mt5.POSITION_TYPE_BUY else 'SELL',
                    'lots': pos.volume,
                    'price': pos.price_open,
                    'profit': pos.profit,
                    'swap': pos.swap,
                    'time': datetime.fromtimestamp(pos.time)
                })
        return trades

    def set_breakeven(self, ticket):
        if not self.connected:
            return False, "MT5 not connected"
        try:
            positions = self.mt5.positions_get(ticket=int(ticket))
            if not positions:
                return False, "Position not found"
            position = positions[0]
            request = {
                "action": self.mt5.TRADE_ACTION_SLTP,
                "symbol": position.symbol,
                "position": position.ticket,
                "sl": position.price_open,
                "tp": position.tp
            }
            result = self.mt5.order_send(request)
            if result and result.retcode == self.mt5.TRADE_RETCODE_DONE:
                logger.info(f"Breakeven set for ticket: {ticket}")
                return True, "Breakeven set successfully"
            else:
                error_msg = f"Breakeven failed: {result.retcode} - {result.comment}" if result else "Unknown error"
                return False, error_msg
        except Exception as e:
            logger.error(f"Error setting breakeven: {e}")
            return False, f"Error: {str(e)}"

    def modify_sl_tp(self, ticket, sl=None, tp=None):
        if not self.connected:
            return False, "MT5 not connected"
        try:
            positions = self.mt5.positions_get(ticket=int(ticket))
            if not positions:
                return False, "Position not found"
            position = positions[0]
            request = {
                "action": self.mt5.TRADE_ACTION_SLTP,
                "symbol": position.symbol,
                "position": position.ticket,
                "sl": sl if sl is not None else position.sl,
                "tp": tp if tp is not None else position.tp
            }
            result = self.mt5.order_send(request)
            if result and result.retcode == self.mt5.TRADE_RETCODE_DONE:
                logger.info(f"SL/TP modified for ticket: {ticket}")
                return True, "SL/TP modified successfully"
            else:
                error_msg = f"Modify failed: {result.retcode} - {result.comment}" if result else "Unknown error"
                return False, error_msg
        except Exception as e:
            logger.error(f"Error modifying SL/TP: {e}")
            return False, f"Error: {str(e)}"