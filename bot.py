from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
import yfinance as yf
import ta
import os

TOKEN = "8500788722:AAGd5qkDBqD0I53e6gVPZoNHlaVuwjoRry0"

# -------- STOCK ANALYSIS -------- #
def analyze_stock(symbol):
    stock = yf.Ticker(symbol + ".NS")
    hist = stock.history(period="1mo")

    if hist.empty:
        return "❌ Stock not found"

    close = hist["Close"]
    volume = hist["Volume"]

    last_price = close.iloc[-1]

    # Indicators
    ma20 = close.rolling(window=20).mean().iloc[-1]
    rsi = ta.momentum.RSIIndicator(close).rsi().iloc[-1]

    avg_vol = volume.mean()
    latest_vol = volume.iloc[-1]

    # Logic
    score = 0

    if last_price > ma20:
        trend = "Bullish 📈"
        score += 1
    else:
        trend = "Bearish 📉"

    if 40 < rsi < 70:
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

    # Final signal
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


# -------- START -------- #
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "📊 Welcome to FinAdvisor Bot\n\n"
        "Use:\n"
        "/analyze TCS\n"
        "/analyze INFY"
    )


# -------- ANALYZE COMMAND -------- #
async def analyze(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("❌ Please provide stock name\nExample: /analyze TCS")
        return

    symbol = context.args[0]

    result = analyze_stock(symbol)

    await update.message.reply_text(result)


# -------- MAIN -------- #
app = ApplicationBuilder().token(TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("analyze", analyze))

app.run_polling()
