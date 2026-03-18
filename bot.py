from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder, CommandHandler, CallbackQueryHandler, ContextTypes
)
import yfinance as yf
import ta
import os

TOKEN = "8500788722:AAGd5qkDBqD0I53e6gVPZoNHlaVuwjoRry0"


# -------- ANALYSIS FUNCTION -------- #
def analyze_stock(symbol):
    stock = yf.Ticker(symbol + ".NS")
    hist = stock.history(period="1mo")

    if hist.empty:
        return "❌ Stock not found"

    close = hist["Close"]
    volume = hist["Volume"]

    last_price = close.iloc[-1]

    ma20 = close.rolling(window=20).mean().iloc[-1]
    rsi = ta.momentum.RSIIndicator(close).rsi().iloc[-1]

    avg_vol = volume.mean()
    latest_vol = volume.iloc[-1]

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


# -------- TOP PICKS -------- #
def get_top_picks():
    stocks = ["TCS", "INFY", "RELIANCE", "HDFCBANK"]

    result = "📈 Top Stocks Today:\n\n"

    for s in stocks:
        result += analyze_stock(s) + "\n"

    return result


# -------- IPO -------- #
def get_ipo():
    return """
🚀 IPO Updates

• Tata Tech (Example)
• Strong interest expected

⚠️ Always check fundamentals before applying
"""


# -------- START -------- #
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):

    keyboard = [
        [InlineKeyboardButton("📊 Analyze Stock", callback_data="analyze")],
        [InlineKeyboardButton("📈 Top Picks Today", callback_data="top")],
        [InlineKeyboardButton("🚀 IPO Updates", callback_data="ipo")]
    ]

    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text(
        "📊 FinAdvisor Bot\n\nChoose an option 👇",
        reply_markup=reply_markup
    )


# -------- BUTTON HANDLER -------- #
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data == "analyze":
        await query.edit_message_text(
            "Type like:\n/analyze TCS"
        )

    elif query.data == "top":
        result = get_top_picks()
        await query.edit_message_text(result)

    elif query.data == "ipo":
        result = get_ipo()
        await query.edit_message_text(result)


# -------- ANALYZE COMMAND -------- #
async def analyze(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("Example: /analyze TCS")
        return

    symbol = context.args[0]
    result = analyze_stock(symbol)

    await update.message.reply_text(result)


# -------- MAIN -------- #
app = ApplicationBuilder().token(TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("analyze", analyze))
app.add_handler(CallbackQueryHandler(button_handler))

app.run_polling()
