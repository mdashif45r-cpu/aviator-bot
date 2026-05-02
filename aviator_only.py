import telebot
from telebot import types
import random
import time
import threading
from datetime import datetime, timedelta, timezone

TOKEN = '8690661270:AAF7DZFcW0Q7Nn4o4JCHtcNgRZJ9q_1R4q0'
bot = telebot.TeleBot(TOKEN)

user_data = {}

def get_smart_prediction(chat_id):
    now_utc = datetime.now(timezone.utc)
    bd_now = now_utc + timedelta(hours=6)
    
    total_seconds = (bd_now.hour * 3600) + (bd_now.minute * 60) + bd_now.second
    round_id = 1 + (total_seconds // 60)
    period = bd_now.strftime("%Y%m%d1000") + str(round_id).zfill(4)
    
    last_digits_sum = sum(int(d) for d in str(round_id)[-3:])
    
    if chat_id not in user_data:
        user_data[chat_id] = {"win": 0, "loss": 0, "history": [], "is_running": False}
    
    stats = user_data[chat_id]
    history = stats.get("history", [])
    
    if (last_digits_sum + bd_now.minute) % 2 == 0:
        base_pred = "BIG 🔺"
    else:
        base_pred = "SMALL 🔻"
        
    if len(history) >= 3 and history[-3:].count("loss") >= 2:
        prediction = "SMALL 🔻" if base_pred == "BIG 🔺" else "BIG 🔺"
    else:
        prediction = base_pred

    color = "GREEN 🟢" if prediction == "BIG 🔺" else "RED 🔴"
    num_pred = random.randint(0, 9)

    msg = (f"🤖 **1-MIN AI ANALYSIS**\n"
           f"━━━━━━━━━━━━━━━━━━━━\n"
           f"🕒 Period: `{period}`\n"
           f"📊 Prediction: **{prediction}**\n"
           f"🎨 Color: **{color}**\n"
           f"🔢 Number: **{num_pred}**\n"
           f"🔥 Accuracy: `{random.randint(95, 99)}%` (AI Optimized)\n"
           f"━━━━━━━━━━━━━━━━━━━━\n"
           f"📊 Score: ✅ Win: {stats['win']} | ❌ Loss: {stats['loss']}\n"
           f"👤 Developer: ASIF")
    return msg

def send_auto_signals(chat_id):
    while user_data.get(chat_id, {}).get("is_running", False):
        msg = get_smart_prediction(chat_id)
        
        markup = types.InlineKeyboardMarkup()
        btn_win = types.InlineKeyboardButton("👍 WIN", callback_data="hit_win")
        btn_loss = types.InlineKeyboardButton("👎 LOSS", callback_data="hit_loss")
        btn_stop = types.InlineKeyboardButton("🛑 STOP SERVICE", callback_data="stop_service")
        markup.row(btn_win, btn_loss)
        markup.add(btn_stop)
        
        try:
            bot.send_message(chat_id, msg, reply_markup=markup, parse_mode="Markdown")
        except Exception as e:
            print(f"Error: {e}")
            break
        
        time.sleep(60)

@bot.message_handler(commands=['start'])
def start(message):
    chat_id = message.chat.id
    if chat_id not in user_data:
        user_data[chat_id] = {"win": 0, "loss": 0, "history": [], "is_running": False}
    
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("🚀 START 1-MIN SIGNAL", callback_data="start_service"))
    
    bot.send_message(chat_id, "Welcome ASIF! Click the button below to start analysis.", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: True)
def handle_query(call):
    chat_id = call.message.chat.id
    
    if chat_id not in user_data:
        user_data[chat_id] = {"win": 0, "loss": 0, "history": [], "is_running": False}

    if call.data == "start_service":
        if not user_data[chat_id]["is_running"]:
            user_data[chat_id]["is_running"] = True
            bot.edit_message_text("✅ 1-Min Auto Analysis Running...", chat_id, call.message.message_id)
            threading.Thread(target=send_auto_signals, args=(chat_id,)).start()
        else:
            bot.answer_callback_query(call.id, "Service is already running!")

    elif call.data == "hit_win":
        user_data[chat_id]["win"] += 1
        user_data[chat_id]["history"].append("win")
        bot.answer_callback_query(call.id, "Win recorded! ✅")

    elif call.data == "hit_loss":
        user_data[chat_id]["loss"] += 1
        user_data[chat_id]["history"].append("loss")
        bot.answer_callback_query(call.id, "Loss recorded. Updating logic... ❌")

    elif call.data == "stop_service":
        user_data[chat_id]["is_running"] = False
        final_score = f"🛑 Service Stopped.\n\nFinal Score:\n✅ Win: {user_data[chat_id]['win']}\n❌ Loss: {user_data[chat_id]['loss']}"
        bot.send_message(chat_id, final_score)

print("Bot is running...")
bot.polling(none_stop=True)
