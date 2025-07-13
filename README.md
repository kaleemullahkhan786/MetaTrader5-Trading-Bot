# 🤖 MetaTrader 5 Trading Bot

<div align="center">

![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)
![Telegram](https://img.shields.io/badge/Telegram-Bot-blue.svg)
![MT5](https://img.shields.io/badge/MetaTrader-5-green.svg)
![Windows](https://img.shields.io/badge/Windows-Only-red.svg)
![License](https://img.shields.io/badge/License-MIT-yellow.svg)

**Professional Telegram Bot for Real MetaTrader 5 Trading with Advanced Risk Management**

[🚀 Features](#-features) • [💻 Installation](#-installation) • [⚙️ Setup](#️-setup) • [📱 Usage](#-usage) • [🔒 Security](#-security)

</div>

---

## 🎯 **Project Overview**

This is a **professional-grade Telegram bot** that provides **real MetaTrader 5 trading capabilities** with advanced risk management features. The bot allows users to execute real trades, manage positions, and implement sophisticated risk management strategies directly through Telegram.

### 🌟 **Key Highlights**
- ✅ **Real MT5 Integration** - Execute actual trades with real money
- ✅ **Advanced Risk Management** - Professional position sizing and risk calculation
- ✅ **Multiple Trading Methods** - Standard, risk-based, and quick trading
- ✅ **Live Market Data** - Real-time prices, spreads, and market analysis
- ✅ **Professional UI** - Modern Telegram interface with inline keyboards

---

## 🚀 **Features**

### 📊 **Trading Capabilities**
- **Real Trade Execution** - BUY/SELL orders with actual MT5 integration
- **Multiple Trading Methods**:
  - Standard trading with manual lot selection
  - Risk-based trading with automatic lot calculation
  - Quick trading commands for fast execution
- **Advanced Order Types** - Stop Loss, Take Profit, Breakeven
- **Position Management** - View, modify, and close trades

### 💰 **Risk Management**
- **Dollar-Based Risk** - Specify exact dollar amount to risk
- **Automatic Lot Calculation** - Professional position sizing
- **Risk/Reward Ratios** - Easy 1:1, 1:2, 1:3 setups
- **Stop Loss Management** - Point-based and price-based SL
- **Take Profit Targets** - Dollar-based profit targets

### 📱 **User Interface**
- **Modern Telegram Bot** - Professional inline keyboards
- **Real-time Updates** - Live account and trade information
- **Session Management** - User state tracking
- **Error Handling** - Comprehensive error management
- **Multi-language Support** - Ready for internationalization

### 🔧 **Technical Features**
- **Windows Native** - Full MT5 integration
- **Real-time Data** - Live market prices and spreads
- **Account Management** - Balance, equity, profit tracking
- **Logging System** - Professional logging for debugging
- **Security Features** - User authorization and input validation

---

## 💻 **Installation**

### 📋 **Prerequisites**
- **Windows 10/11** (MT5 integration requires Windows)
- **Python 3.8+**
- **MetaTrader 5 Terminal** (demo or live account)
- **Telegram Bot Token** (from @BotFather)

### 🛠️ **Setup Instructions**

#### 1. **Clone Repository**
```bash
git clone https://github.com/kaleemullahkhan786/MetaTrader5-Trading-Bot.git
cd MetaTrader5-Trading-Bot
```

#### 2. **Create Virtual Environment**
```bash
python -m venv venv
venv\Scripts\activate  # Windows
```

#### 3. **Install Dependencies**
```bash
pip install -r requirements.txt
```

#### 4. **Configure Bot**
```bash
# Copy sample config
cp config.sample.json config.json

# Edit config.json with your credentials
notepad config.json
```

#### 5. **Configure MT5**
- Install MetaTrader 5 from [official website](https://www.metatrader5.com/en/download)
- Create demo or live account
- Note your login, password, and server details

---

## ⚙️ **Configuration**

### 📝 **config.json Setup**
```json
{
    "bot_token": "YOUR_BOT_TOKEN_HERE",
    "bot_username": "YOUR_BOT_USERNAME",
    "mt5_login": YOUR_MT5_LOGIN,
    "mt5_password": "YOUR_MT5_PASSWORD",
    "mt5_server": "YOUR_MT5_SERVER",
    "allowed_users": [],
    "admin_user_id": null,
    "alert_channel_id": "@your_alert_channel",
    "alert_group_id": "@your_alert_group",
    "enable_alerts": true,
    "enable_notifications": true
}
```

### 🔑 **Getting Bot Token**
1. Message [@BotFather](https://t.me/BotFather) on Telegram
2. Send `/newbot`
3. Follow instructions to create your bot
4. Copy the token to `config.json`

### 📊 **MT5 Account Setup**
1. **Demo Account** (Recommended for testing):
   - Free to create
   - No real money risk
   - Full trading functionality

2. **Live Account** (For real trading):
   - Requires real money deposit
   - Higher risk - use with caution
   - Professional trading capabilities

### 📢 **Alert Channel Setup** (Optional)
1. **Create Telegram Channel/Group**:
   - Create a new channel or group in Telegram
   - Add your bot as admin with send message permissions
   - Copy the channel/group username (e.g., @my_trading_alerts)

2. **Configure Alerts**:
   - Set `alert_channel_id` or `alert_group_id` in config.json
   - Enable alerts with `enable_alerts: true`
   - All trades will be automatically posted to your channel/group

---

## 📱 **Usage**

### 🎯 **Bot Commands**

#### **Main Commands**
| Command | Description |
|---------|-------------|
| `/start` | Start the bot and show main menu |
| `/help` | Show comprehensive help guide |
| `/account` | View account information |
| `/trade` | Open a new trade |
| `/trades` | View open trades |
| `/close` | Close a trade |
| `/market` | View market data |
| `/settings` | Manage bot settings |

#### **Quick Commands**
| Command | Example | Description |
|---------|---------|-------------|
| `/quick_buy` | `/quick_buy EURUSD 0.1` | Quick BUY trade |
| `/quick_sell` | `/quick_sell GBPUSD 0.05` | Quick SELL trade |
| `/quick_close` | `/quick_close 123456` | Quick close trade |

### 💰 **Trading Methods**

#### **1. 🎯 Interactive Workflow** ⭐ **NEW & RECOMMENDED**
```
Symbol Input → Trade Type → SL Points → Risk % → TP Multiplier → Execute
```
- **Manual Symbol Input** - Type any trading symbol (EURUSD, XAUUSD, BTCUSD, etc.)
- **Manual SL Points** - Custom stop loss distance in points
- **Manual Risk %** - Custom risk percentage (1%, 2%, 3%, etc.)
- **Manual TP Multiplier** - Custom take profit multiplier (1x, 2x, 3x SL)
- **Quick Options** - Predefined buttons for fast selection
- **Real-time Alerts** - Channel/group notifications for all trades
- **Auto Lot Calculation** - Professional position sizing based on risk

#### **2. Standard Trading**
```
Symbol → BUY/SELL → Lot Size → Execute
```
- Manual lot selection
- Optional SL/TP in pips
- Direct trade execution

#### **3. Risk-Based Trading**
```
Symbol → Risk-Based → Risk Amount → SL Points → TP Amount → Execute
```
- Automatic lot calculation
- Dollar-based risk management
- Professional position sizing
- Perfect risk/reward ratios

#### **4. Quick Trading**
```
/quick_buy EURUSD 0.1
/quick_sell GBPUSD 0.05
```
- Fast execution
- Direct commands
- Immediate trade placement

### 📊 **Supported Symbols**
- **💱 Major Forex**: EURUSD, GBPUSD, USDJPY, USDCHF, AUDUSD, USDCAD, NZDUSD
- **💱 Minor Forex**: EURGBP, EURJPY, EURCHF, EURCAD, EURAUD, EURNZD, GBPJPY, GBPCHF, GBPCAD, GBPAUD, GBPNZD
- **💱 Exotic Pairs**: USDNOK, USDSEK, USDDKK, USDTRY, USDZAR, USDBRL, USDINR, USDRUB, USDCNH
- **🪙 Commodities**: XAUUSD, XAGUSD, XAUGBP, XAUJPY, XAUCHF, XAGGBP, XAGJPY, XAGCHF
- **⛽ Energy**: USOIL, UKOIL, NATGAS, BRENT, WTI
- **📈 Indices**: US30, US500, NAS100, GER30, UK100, FRA40, JPN225, HK50, CHN50
- **₿ Crypto**: BTCUSD, ETHUSD, LTCUSD, XRPUSD, BCHUSD, ADAUSD, DOTUSD, LINKUSD, UNIUSD, SOLUSD, MATICUSD, AVAXUSD
- **📊 Stocks**: AAPL, MSFT, GOOGL, AMZN, TSLA, META, NVDA, NFLX, AMD, INTC, ORCL, CRM, ADBE, PYPL, NKE
- **🔥 Popular**: EURUSD, GBPUSD, USDJPY, XAUUSD, BTCUSD, USOIL, US500, AAPL, TSLA

**Note**: Symbol availability depends on your MT5 broker. You can also manually type any symbol in the new interactive workflow.

---

## 🔒 **Security & Risk Management**

### ⚠️ **Important Warnings**
- **Real Money Trading** - This bot executes real trades with real money
- **Risk of Loss** - Trading involves substantial risk of loss
- **Demo First** - Always test with demo account before live trading
- **Proper Risk Management** - Never risk more than you can afford to lose

### 🛡️ **Security Features**
- **User Authorization** - Configurable user access control
- **Input Validation** - All inputs validated for security
- **Error Handling** - Comprehensive error management
- **Logging** - Professional logging for monitoring

### 💡 **Risk Management Tips**
- Use risk-based trading for better position sizing
- Set appropriate stop losses for every trade
- Consider risk/reward ratios (1:2, 1:3)
- Monitor your trades regularly
- Start with small position sizes

---

## 🐛 **Troubleshooting**

### 🔧 **Common Issues**

#### **Connection Problems**
```bash
# Check MT5 credentials
# Verify internet connection
# Ensure MT5 terminal is running
```

#### **Trade Execution Issues**
```bash
# Check account balance
# Verify market hours
# Ensure symbol is available
```

#### **Bot Not Responding**
```bash
# Check bot token
# Verify Python installation
# Check log files
```

### 📋 **Log Files**
- Location: `logs/trading_bot.log`
- Contains: Error messages, trade logs, debug information
- Use for: Troubleshooting and monitoring

---

## 🤝 **Support & Contributing**

### 📞 **Getting Help**
1. **Check Logs** - Review `logs/trading_bot.log`
2. **Test Demo** - Use demo account for testing
3. **Verify Setup** - Ensure all requirements met
4. **Contact Support** - For technical issues

### 🔄 **Contributing**
- Fork the repository
- Create feature branch
- Make changes
- Submit pull request

### 📄 **License**
This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## ⚖️ **Disclaimer**

**⚠️ IMPORTANT: This software is for educational and trading purposes only.**

- Trading involves substantial risk of loss
- Past performance does not guarantee future results
- Use at your own risk
- Always practice proper risk management
- Consider consulting a financial advisor

**The developers are not responsible for any financial losses incurred through the use of this software.**

---

<div align="center">

**Made with ❤️ for Professional Traders**

[⭐ Star this repo](https://github.com/kaleemullahkhan786/MetaTrader5-Trading-Bot) • [🐛 Report Issues](https://github.com/kaleemullahkhan786/MetaTrader5-Trading-Bot/issues) • [📧 Contact](mailto:contact@example.com)

</div> 