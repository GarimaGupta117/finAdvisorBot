from telegram import Update, ReplyKeyboardMarkup, BotCommand
from telegram.ext import (
    ApplicationBuilder, CommandHandler, MessageHandler,
    ContextTypes, filters
)

import yfinance as yf
import ta
import numpy as np
import os

TOKEN = "8500788722:AAGd5qkDBqD0I53e6gVPZoNHlaVuwjoRry0"


# -------- ANALYSIS -------- #
def analyze_stock(symbol):
    stock = yf.Ticker(symbol + ".NS")
    hist = stock.history(period="1mo")

    if hist.empty:
        return "❌ Stock not found"

    close = hist["Close"]
    volume = hist["Volume"]

    last_price = close.iloc[-1]
    ma20 = close.rolling(20).mean().iloc[-1]
    rsi = ta.momentum.RSIIndicator(close).rsi().iloc[-1]

    avg_vol = volume.mean()
    latest_vol = volume.iloc[-1]

    score = 0

    if last_price > ma20:
        trend = "Bullish 📈"
        score += 1
    else:
        trend = "Bearish 📉"

    if 40 < rsi < 65:
        momentum = "Healthy"
        score += 1
    elif rsi >= 70:
        momentum = "Overbought"
    else:
        momentum = "Weak"

    if latest_vol > avg_vol:
        volume_signal = "High 🔥"
        score += 1
    else:
        volume_signal = "Normal"

    if score >= 2:
        signal = "Moderate Bullish"
        confidence = "7/10"
    else:
        signal = "Cautious"
        confidence = "4/10"

    return f"""
📊 {symbol.upper()}

Price: ₹{round(last_price,2)}

Trend: {trend}
RSI: {round(rsi,1)} ({momentum})
Volume: {volume_signal}

📌 Signal: {signal}
🔎 Confidence: {confidence}

⚠️ Not financial advice
"""


# -------- OPPORTUNITIES -------- #
def advanced_score(symbol):
    stock = yf.Ticker(symbol + ".NS")
    hist = stock.history(period="1mo")

    if hist.empty:
        return None

    close = hist["Close"]
    volume = hist["Volume"]

    last_price = close.iloc[-1]
    prev_price = close.iloc[-2]

    ma20 = close.rolling(20).mean().iloc[-1]
    rsi = ta.momentum.RSIIndicator(close).rsi().iloc[-1]

    avg_vol = volume.mean()
    latest_vol = volume.iloc[-1]

    change = ((last_price - prev_price) / prev_price) * 100
    volatility = close.pct_change().std()

    score = 0
    reasons = []

    if last_price > ma20:
        score += 1
        reasons.append("Above MA20")

    if 40 < rsi < 65:
        score += 1
        reasons.append("Healthy RSI")

    if latest_vol > avg_vol:
        score += 1
        reasons.append("High Volume")

    if change > 0:
        score += 1
        reasons.append("Positive Momentum")

    if volatility < 0.02:
        score += 1
        reasons.append("Stable")

    return {
        "symbol": symbol,
        "price": last_price,
        "score": score,
        "reasons": reasons
    }


def get_best_opportunities():
    stocks = ["TCS", "INFY", "RELIANCE", "HDFCBANK", "ICICIBANK"]

    results = []

    for s in stocks:
        data = advanced_score(s)
        if data and data["score"] >= 3:
            results.append(data)

    results = sorted(results, key=lambda x: x["score"], reverse=True)

    if not results:
        return "❌ No strong opportunities today"

    text = "🔥 Top Opportunities Today\n\n"

    for s in results:
        text += f"• {s['symbol']} – ₹{round(s['price'],2)}\n"
        text += f"Score: {s['score']}/5\n"
        text += f"Signals: {', '.join(s['reasons'])}\n\n"

    text += "⚠️ Based on multi-factor analysis"

    return text


# -------- HEDGE -------- #
def find_hedge(symbol):
    stocks = ["TCS", "INFY", "RELIANCE", "HDFCBANK", "ICICIBANK"]

    base = yf.Ticker(symbol + ".NS").history(period="1mo")["Close"]

    best_pair = None
    lowest_corr = 1

    for s in stocks:
        if s == symbol:
            continue

        other = yf.Ticker(s + ".NS").history(period="1mo")["Close"]

        if len(other) != len(base):
            continue

        corr = np.corrcoef(base, other)[0][1]

        if corr < lowest_corr:
            lowest_corr = corr
            best_pair = s

    return best_pair, lowest_corr


def hedge_output(symbol):
    pair, corr = find_hedge(symbol)

    if not pair:
        return "❌ Could not find hedge"

    return f"""
🛡 Hedge for {symbol.upper()}

Pair: {pair}
Correlation: {round(corr,2)}

📌 Lower correlation = better diversification

⚠️ Not a perfect hedge
"""


# -------- MENU -------- #
def get_menu():
    return ReplyKeyboardMarkup(
        [
            ["📊 Analyze"],
            ["🔥 Opportunities"],
            ["🛡 Hedge"]
        ],
        resize_keyboard=True
    )


# -------- START -------- #
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "📊 FinAdvisor Bot Ready 🚀\nChoose an option:",
        reply_markup=get_menu()
    )


# -------- MENU HANDLER -------- #
async def menu_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text

    if text == "📊 Analyze":
        await update.message.reply_text("Use: /analyze TCS")

    elif text == "🔥 Opportunities":
        await update.message.reply_text(get_best_opportunities())

    elif text == "🛡 Hedge":
        await update.message.reply_text("Use: /hedge TCS")


# -------- COMMANDS -------- #
async def analyze(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("Example: /analyze TCS")
        return

    symbol = context.args[0]
    await update.message.reply_text(analyze_stock(symbol))


async def hedge(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("Example: /hedge TCS")
        return

    symbol = context.args[0]
    await update.message.reply_text(hedge_output(symbol))


# -------- MAIN -------- #
app = ApplicationBuilder().token(TOKEN).build()

# Set Telegram menu (≡ button)
app.bot.set_my_commands([
    BotCommand("start", "Start bot"),
    BotCommand("analyze", "Analyze stock"),
    BotCommand("hedge", "Hedge suggestion"),
])

app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("analyze", analyze))
app.add_handler(CommandHandler("hedge", hedge))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, menu_handler))

app.run_polling()
