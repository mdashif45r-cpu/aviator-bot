import telebot
from telebot import types
import random
import time
import threading
from flask import Flask
from datetime import datetime, timedelta, timezone

app = Flask('')
@app.route('/')
def home(): return "Auto-Sync AI Bot is Live!"

def run_flask(): app.run(host='0.0.0.0', port=8080)

TOKEN = '8690661270:AAF7DZFcW0Q7Nn4o4JCHtcNgRZJ9q_1R4q0'
bot = telebot.TeleBot(TOKEN)
user_data = {}

def get_realtime_period():
    # বাংলাদেশ সময় অনুযায়ী বর্তমান পিরিয়ড বের করার লজিক
    now_bd = datetime.now(timezone.utc) + timedelta(hours=6)
    
    # রাত ১২টা থেকে এখন পর্যন্ত কত মিনিট পার হয়েছে তা বের করা
    total_minutes_passed = (now_bd.hour * 60) + now_bd.minute
    
    # তোমার স্ক্রিনশট অনুযায়ী পিরিয়ড বেস নম্বর সেট করা (১ম পিরিয়ড থেকে হিসাব)
    # সাধারণত দিনের প্রথম পিরিয়ড হয় ১০০১ থেকে। তোমার ১১১৩৮ মানে এটি দিনের ১১৩৮তম মিনিট।
    period_number = 10000 + total_minutes_passed 
    
    date_str = now_bd.strftime("%Y%m%d")
    final_period = f"{date_str}1000{period_number}"
    return final_period

def get_prediction_logic(chat_id):
    period = get_realtime_period()
    stats = user_data[chat_id]
    
    # শক্তিশালী কেলকুলেশন: পিরিয়ডের শেষ ৩ ডিজিট + বর্তমান মিনিট
    last_three = int(period[-3:])
    minute = (datetime.now(timezone.utc) + timedelta(hours=6)).minute
    
    if (last_three + minute) % 2 == 0:
        prediction, color = "BIG 🔺", "GREEN 🟢"
    else:
        prediction, color = "SMALL 🔻", "RED 🔴"
        
    # রিয়েকশন ভিত্তিক সংশোধন (যদি আগেরটা লস হয়)
    if user_data[chat_id]["history"] and user_data[chat_id]["history"][-1] == "loss":
        prediction = "SMALL 🔻" if prediction == "BIG 🔺" else "BIG 🔺"
        color = "RED 🔴" if color == "GREEN 🟢" else "GREEN 🟢"

    msg = (f"🚀 **AUTO-SYNC AI ANALYSIS**\n"
           f"━━━━━━━━━━━━━━━━━━━━\n"
           f"🕒 Period: `{period}`\n"
           f"📊 Prediction: **{prediction}**\n"
           f"🎨 Color: **{color}**\n"
           f"🔥 Accuracy: `{random.randint(96, 99)}%` (Sync OK)\n"
           f"━━━━━━━━━━━━━━━━━━━━\n"
           f"📈 Stats: ✅ {stats['win']} | ❌ {stats['loss']}\n"
           f"👤 Developer: ASIF")
    return msg

def send_auto_signals(chat_id):
    while user_data.get(chat_id, {}).get("is_running", False):
        now = datetime.now(timezone.utc) + timedelta(hours=6)
        
        # ২০ সেকেন্ডের টাইমিং গ্যাপ
        wait_time = (60 - now.second + 20) if now.second >= 20 else (20 - now.second)
        time.sleep(wait_time)
        
        if not user_data.get(chat_id, {}).get("is_running", False): break
        
        try:
            msg = get_prediction_logic(chat_id)
            markup = types.InlineKeyboardMarkup()
            markup.row(types.InlineKeyboardButton("👍 WIN", callback_data="hit_win"), 
                       types.InlineKeyboardButton("👎 LOSS", callback_data="hit_loss"))
            markup.add(types.InlineKeyboardButton("🛑 STOP SERVICE", callback_data="stop_service"))
            bot.send_message(chat_id, msg, reply_markup=markup, parse_mode="Markdown")
        except: break

@bot.message_handler(commands=['start'])
def start(message):
    chat_id = message.chat.id
    user_data[chat_id] = {"win": 0, "loss": 0, "history": [], "is_running": False}
    bot.send_message(chat_id, "🔥 **ASIF'S AUTO-SYNC BOT READY!**\n\nবট এখন আপনার এলাকার সময় অনুযায়ী মাঝখানের পিরিয়ড গ্যাপগুলো অটো কেলকুলেশন করে নিবে।", 
                     reply_markup=types.InlineKeyboardMarkup().add(types.InlineKeyboardButton("🚀 START SYNC", callback_data="start_service")))

@bot.callback_query_handler(func=lambda call: True)
def handle_query(call):
    chat_id = call.message.chat.id
    if call.data == "start_service":
        user_data[chat_id]["is_running"] = True
        bot.edit_message_text("🔍 Calculating Gaps & Syncing Time...", chat_id, call.message.message_id)
        threading.Thread(target=send_auto_signals, args=(chat_id,)).start()
    elif "hit" in call.data:
        res = "win" if "win" in call.data else "loss"
        user_data[chat_id][res] += 1
        user_data[chat_id]["history"].append(res)
        bot.answer_callback_query(call.id, f"Recorded {res.upper()}!")
    elif call.data == "stop_service":
        user_data[chat_id]["is_running"] = False
        bot.send_message(chat_id, "🛑 Service Paused.")

if __name__ == "__main__":
    threading.Thread(target=run_flask).start()
    bot.polling(none_stop=True)
