#!/usr/bin/env python3
"""
MetaTrader 5 Trading Bot - Main Entry Point
A Telegram bot for managing MT5 trades on Windows
"""

from pathlib import Path
import sys
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters
from bot.handlers import BotHandlers
from bot.utils import setup_logging
from config.settings import BOT_TOKEN

# Add project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

logger = setup_logging()

if __name__ == "__main__":
    if not BOT_TOKEN:
        logger.error("Bot token not found! Please set BOT_TOKEN in config.json or environment variable.")
        sys.exit(1)

    application = Application.builder().token(BOT_TOKEN).build()
    handlers = BotHandlers()
    
    # Command handlers
    application.add_handler(CommandHandler("start", handlers.start_command))
    application.add_handler(CommandHandler("help", handlers.help_command))
    application.add_handler(CommandHandler("account", handlers.account_command))
    application.add_handler(CommandHandler("trade", handlers.trade_command))
    application.add_handler(CommandHandler("trades", handlers.trades_command))
    application.add_handler(CommandHandler("close", handlers.close_command))
    application.add_handler(CommandHandler("market", handlers.market_command))
    application.add_handler(CommandHandler("settings", handlers.settings_command))
    application.add_handler(CommandHandler("status", handlers.status_command))
    application.add_handler(CommandHandler("quick", handlers.quick_command))
    application.add_handler(CommandHandler("quick_buy", handlers.quick_buy_command))
    application.add_handler(CommandHandler("quick_sell", handlers.quick_sell_command))
    application.add_handler(CommandHandler("quick_close", handlers.quick_close_command))
    
    # Callback query handler for inline buttons
    application.add_handler(CallbackQueryHandler(handlers.handle_callback_query))
    
    # Message handler for text input (risk-based trading)
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handlers.handle_text_input))

    logger.info("Starting MetaTrader 5 Trading Bot...")
    logger.info("Bot is ready! Send /start to begin.")
    application.run_polling(drop_pending_updates=True) 