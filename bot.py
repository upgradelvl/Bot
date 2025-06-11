import telebot
import os
from telebot import types
import json
from bot_config import TOKEN, CHANNELS, ADMIN_USERNAME

bot = telebot.TeleBot(TOKEN)

# data.json faylini ochish va o‘qish
with open("data.json", "r", encoding="utf-8") as f:
    data = json.load(f)

# invited maydoni mavjud emasligini tekshirib qo‘shish
for uid in data['users']:
    if 'invited' not in data['users'][uid]:
        data['users'][uid]['invited'] = 0

# O'zgartirilgan ma'lumotlarni qayta saqlash
with open("data.json", "w", encoding="utf-8") as f:
    json.dump(data, f, ensure_ascii=False, indent=4)

# Shu yerda siz menyuni yuborasiz:
def send_main_menu(message):
    with open('data.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
    user_id = str(message.chat.id)
    name = data['users'][user_id]['first_name']
    
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add("1️⃣ Profil", "2️⃣ Taklif qog'ozi")
    markup.add("3️⃣ Yordam", "4️⃣ Reyting", "5️⃣ Foydalanuvchilar")

    bot.send_message(message.chat.id, f"Asosiy menyu, {name}", reply_markup=markup)



# Foydalanuvchini saqlash
def save_user(user_id, first_name, ref_id):
    try:
        with open("data.json", "r", encoding="utf-8") as f:
            data = json.load(f)
    except FileNotFoundError:
        data = {}
    except json.JSONDecodeError:
        data = {}

    # ... sizning foydalanuvchi saqlash kodingiz ...
    
    with open("data.json", "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

# Start komandasi
@bot.message_handler(commands=['start'])
def start_handler(message):
    user_id = message.from_user.id
    first_name = message.from_user.first_name
    args = message.text.split()

    ref_id = args[1] if len(args) > 1 else None
    save_user(user_id, first_name, ref_id)

    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add("✅ Obunani tekshirish")
    bot.send_message(message.chat.id,
        f"Sizning ID: {user_id}\nIltimos ismingizni kiriting:", reply_markup=markup)
    bot.register_next_step_handler(message, ask_channels)

def ask_channels(message):
    name = message.text
    markup = types.InlineKeyboardMarkup()
    for ch in CHANNELS:
        markup.add(types.InlineKeyboardButton(f"➕ {ch}", url=f"https://t.me/{ch[1:]}"))
    markup.add(types.InlineKeyboardButton("✅ Tekshirish", callback_data='check_subs'))
    bot.send_message(message.chat.id, "Quyidagi kanallarga obuna bo'ling:", reply_markup=markup)

# Obuna tekshirish
@bot.callback_query_handler(func=lambda call: call.data == 'check_subs')
def check_subs(call):
    user_id = call.from_user.id
    result = True
    for ch in CHANNELS:
        try:
            status = bot.get_chat_member(ch, user_id).status
            if status in ['left', 'kicked']:
                result = False
        except:
            result = False

    if result:
        send_main_menu(call.message)
    else:
        bot.answer_callback_query(call.id, "Iltimos, barcha kanallarga obuna bo'ling!")

#profil
@bot.message_handler(func=lambda m: m.text == "1️⃣ Profil")
def show_profile(message):
    with open('data.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
    user = data['users'][str(message.chat.id)]
    bot.send_message(message.chat.id, f"🆔 ID: {message.chat.id}\n👤 Ism: {user['first_name']}\n👥 Taklif qilganlar soni: {user['invited']}\n📊 Reyting: hisoblanmoqda")

# Taklif qog'ozi
@bot.message_handler(func=lambda m: m.text == "2️⃣ Taklif qog'ozi")
def referral_card(message):
    user_id = message.chat.id
    link = f"https://t.me/YOUR_BOT_USERNAME?start={user_id}"
    with open('data.json', 'r') as f:
        data = json.load(f)
    referrals = len(data['referrals'].get(str(user_id), []))
    bot.send_message(message.chat.id, f"Sizning taklif havolangiz:\n{link}\nTaklif qilganlar: {referrals} ta")

# Yordam paneli
@bot.message_handler(func=lambda m: m.text == "3️⃣ Yordam")
def help_panel(message):
    bot.send_message(message.chat.id, f"❓Savolingiz bo'lsa {ADMIN_USERNAME} ga murojaat qiling.")

# Reyting
@bot.message_handler(func=lambda m: m.text == "4️⃣ Reyting")
def rating_handler(message):
 with open("data.json", "w", encoding="utf-8") as f:
    json.dump(data, f, ensure_ascii=False, indent=4)


    users = data['users']
    sorted_users = sorted(users.items(), key=lambda x: x[1]['invited'], reverse=True)
    text = "🏆 Reyting:\n\n"
    for i, (uid, info) in enumerate(sorted_users[:10], start=1):
        text += f"{i}. {info['first_name']} - {info['invited']} ta taklif\n"
    bot.send_message(message.chat.id, text)

# Foydalanuvchilar soni
@bot.message_handler(func=lambda m: m.text == "5️⃣ Foydalanuvchilar")
def users_list(message):
  with open("data.json", "r", encoding="utf-8") as f:
    data = json.load(f)
    users = data['users']
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("👥 Ro'yxat", callback_data="user_list"))
    bot.send_message(message.chat.id, f"Botdagi foydalanuvchilar soni: {len(users)}", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data == "user_list")
def show_user_list(call):
    with open('data.json', 'r') as f:
        data = json.load(f)
    sorted_users = sorted(data['users'].items(), key=lambda x: x[1]['invited'], reverse=True)
    text = "👤 Foydalanuvchilar ro'yxati:\n\n"
    for uid, info in sorted_users:
        text += f"{info['name']} - {info['invited']} ta taklif\n"
    bot.send_message(call.message.chat.id, text)

# Bot ishga tushadi
bot.polling()
