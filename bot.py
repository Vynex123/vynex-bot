# VYNEX IPTV Bot - Professional Customer Service Bot
# Version 2.0 - Production Ready

import os
import logging
import urllib.parse
from datetime import datetime
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes
from telegram.constants import ParseMode

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# ===== CONFIGURATION =====
BOT_TOKEN = "8725271848:AAGiUAKiAaEK1F6buJ_wD6l1Xis9zdSXKmE"
CHANNEL_ID = "@vynexiptv"
ADMIN_IDS = [1821933706, 1638296842]  # Haithem, Aissa

# Storage
users_data = {}
pending_orders = {}

# ===== TRANSLATIONS =====
texts = {
    'ar': {
        'welcome': "👋 أهلاً بك في VYNEX IPTV!\n\n📢 يجب الانضمام للقناة أولاً:",
        'join_channel': "📢 انضم للقناة",
        'check_join': "✅ تحقق من الاشتراك",
        'joined': "✅ تم التحقق! مرحباً بك 👋",
        'confirm_data': "📋 تأكيد بياناتك",
        'choose_payment': "💳 اختر طريقة الدفع:",
        'paypal': "🅿️ PayPal",
        'binance': "💰 Binance",
        'redotpay': "🔴 RedotPay",
        'ccp': "🏦 CCP (الجزائر)",
        'order_sent': "✅ تم إرسال طلبك!\nسيتواصل المشرفون معك قريباً 📞\n\n💬 يمكنك مراسلتنا هنا مباشرة",
        'support': "💬 الدعم الفني",
        'language': "🌐 تغيير اللغة",
        'confirm': "✅ تأكيد الطلب",
        'cancel': "❌ إلغاء",
        'admin_only': "⛔ هذا الأمر للمشرفين فقط!",
        'admin_panel': "🔧 لوحة تحكم المشرف",
        'new_order': "🛒 طلب جديد وارد!",
    },
    'en': {
        'welcome': "👋 Welcome to VYNEX IPTV!\n\n📢 Please join our channel first:",
        'join_channel': "📢 Join Channel",
        'check_join': "✅ Check Subscription",
        'joined': "✅ Verified! Welcome 👋",
        'confirm_data': "📋 Confirm Your Data",
        'choose_payment': "💳 Choose Payment:",
        'paypal': "🅿️ PayPal",
        'binance': "💰 Binance",
        'redotpay': "🔴 RedotPay",
        'ccp': "🏦 CCP (Algeria)",
        'order_sent': "✅ Order sent!\nAdmins will contact you soon 📞\n\n💬 You can message us here directly",
        'support': "💬 Support",
        'language': "🌐 Language",
        'confirm': "✅ Confirm Order",
        'cancel': "❌ Cancel",
        'admin_only': "⛔ Admins only!",
        'admin_panel': "🔧 Admin Panel",
        'new_order': "🛒 New Order!",
    }
}

def get_text(user_id, key):
    lang = users_data.get(user_id, {}).get('lang', 'ar')
    return texts.get(lang, texts['ar']).get(key, key)

# ===== START COMMAND =====
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    user_id = user.id
    args = context.args
    
    user_data = {
        'user_id': user_id,
        'username': user.username,
        'first_name': user.first_name,
        'lang': 'ar',
        'joined_at': datetime.now().isoformat(),
        'orders': []
    }
    
    # Parse deep linking parameters
    if args:
        try:
            param_str = args[0]
            params = {}
            current_key = None
            current_value = []
            parts = param_str.split('_')
            i = 0
            while i < len(parts):
                part = parts[i]
                if part in ['lang', 'plan', 'name', 'email', 'country', 'device']:
                    if current_key:
                        params[current_key] = ' '.join(current_value)
                    current_key = part
                    current_value = []
                else:
                    current_value.append(part)
                i += 1
            if current_key:
                params[current_key] = ' '.join(current_value)
            
            if 'lang' in params:
                user_data['lang'] = params['lang']
            if 'plan' in params:
                user_data['plan'] = params['plan']
            if 'name' in params:
                user_data['full_name'] = params['name']
            if 'email' in params:
                user_data['email'] = params['email']
            if 'country' in params:
                user_data['country'] = params['country']
            if 'device' in params:
                user_data['device'] = params['device']
        except Exception as e:
            logger.error(f"Error parsing params: {e}")
    
    users_data[user_id] = user_data
    await check_membership(update, context)

async def check_membership(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    try:
        member = await context.bot.get_chat_member(CHANNEL_ID, user_id)
        if member.status in ['member', 'administrator', 'creator']:
            await show_main_menu(update, context)
        else:
            raise Exception("Not a member")
    except:
        keyboard = [
            [InlineKeyboardButton(get_text(user_id, 'join_channel'), url=f"https://t.me/{CHANNEL_ID[1:]}")],
            [InlineKeyboardButton(get_text(user_id, 'check_join'), callback_data='check_join')]
        ]
        await update.message.reply_text(
            get_text(user_id, 'welcome'),
            reply_markup=InlineKeyboardMarkup(keyboard)
        )

async def show_main_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    user_data = users_data.get(user_id, {})
    
    if 'plan' in user_data:
        await show_order_confirmation(update, context)
    else:
        keyboard = [
            [InlineKeyboardButton(get_text(user_id, 'support'), callback_data='open_support')],
            [InlineKeyboardButton(get_text(user_id, 'language'), callback_data='change_lang')]
        ]
        text = f"{get_text(user_id, 'main_menu')}\n\n👤 {user_data.get('first_name', 'User')}"
        if update.message:
            await update.message.reply_text(text, reply_markup=InlineKeyboardMarkup(keyboard))
        else:
            await update.callback_query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(keyboard))

async def show_order_confirmation(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = update.effective_user.id
    user_data = users_data.get(user_id, {})
    
    text = f"""
📋 {get_text(user_id, 'confirm_data')}

👤 الاسم: {user_data.get('full_name', 'N/A')}
📧 الإيميل: {user_data.get('email', 'N/A')}
🌍 الدولة: {user_data.get('country', 'N/A')}
📱 الجهاز: {user_data.get('device', 'N/A')}
📦 الباقة: {user_data.get('plan', 'N/A')}

✅ اضغط "تأكيد" للمتابعة
"""
    keyboard = [
        [InlineKeyboardButton(get_text(user_id, 'confirm'), callback_data='confirm_order')],
        [InlineKeyboardButton(get_text(user_id, 'cancel'), callback_data='cancel_order')]
    ]
    if query:
        await query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(keyboard))
    else:
        await update.message.reply_text(text, reply_markup=InlineKeyboardMarkup(keyboard))

# ===== CALLBACKS =====
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data
    user_id = update.effective_user.id
    
    if data == 'check_join':
        await check_membership(update, context)
    elif data == 'confirm_order':
        await show_payment_options(update, context)
    elif data.startswith('pay_'):
        await process_order(update, context, data.split('_')[1])
    elif data == 'open_support':
        users_data[user_id]['support_active'] = True
        await query.edit_message_text("💬 تم تفعيل الدردشة\nاكتب رسالتك الآن..." if users_data[user_id].get('lang') == 'ar' else "💬 Chat activated\nType your message...")
    elif data == 'change_lang':
        keyboard = [
            [InlineKeyboardButton("🇦🇪 العربية", callback_data='setlang_ar')],
            [InlineKeyboardButton("🇬🇧 English", callback_data='setlang_en')]
        ]
        await query.edit_message_text("🌐 اختر اللغة / Choose language:", reply_markup=InlineKeyboardMarkup(keyboard))
    elif data.startswith('setlang_'):
        users_data[user_id]['lang'] = data.split('_')[1]
        await show_main_menu(update, context)
    elif data.startswith('reply_'):
        context.user_data['replying_to'] = int(data.split('_')[1])
        await query.edit_message_text("✍️ اكتب ردك الآن:" if users_data[user_id].get('lang') == 'ar' else "✍️ Type your reply:")
    elif data == 'admin_stats':
        await show_stats(update, context)

async def show_payment_options(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = update.effective_user.id
    keyboard = [
        [InlineKeyboardButton(get_text(user_id, 'paypal'), callback_data='pay_paypal')],
        [InlineKeyboardButton(get_text(user_id, 'binance'), callback_data='pay_binance')],
        [InlineKeyboardButton(get_text(user_id, 'redotpay'), callback_data='pay_redotpay')],
        [InlineKeyboardButton(get_text(user_id, 'ccp'), callback_data='pay_ccp')]
    ]
    await query.edit_message_text(get_text(user_id, 'choose_payment'), reply_markup=InlineKeyboardMarkup(keyboard))

async def process_order(update: Update, context: ContextTypes.DEFAULT_TYPE, payment: str):
    query = update.callback_query
    user_id = update.effective_user.id
    user_data = users_data.get(user_id, {})
    
    order_id = f"ORD{datetime.now().strftime('%y%m%d%H%M%S')}{user_id}"
    order = {
        'id': order_id,
        'user_id': user_id,
        'username': user_data.get('username'),
        'name': user_data.get('full_name'),
        'email': user_data.get('email'),
        'country': user_data.get('country'),
        'device': user_data.get('device'),
        'plan': user_data.get('plan'),
        'payment': payment,
        'time': datetime.now().strftime('%Y-%m-%d %H:%M')
    }
    
    pending_orders[order_id] = order
    user_data['orders'].append(order_id)
    
    # Notify admins
    text = f"""
🛒 {get_text(user_id, 'new_order')}

🆔 Order: `{order_id}`
👤 Name: {order['name']}
📧 Email: {order['email']}
🌍 Country: {order['country']}
📱 Device: {order['device']}
📦 Plan: {order['plan']}
💳 Payment: {order['payment']}
⏰ Time: {order['time']}

👤 @{order['username']} | 🆔 `{user_id}`
"""
    keyboard = [[InlineKeyboardButton("📩 رد على الزبون", callback_data=f"reply_{user_id}")]]
    
    for admin_id in ADMIN_IDS:
        try:
            await context.bot.send_message(admin_id, text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode=ParseMode.MARKDOWN)
        except Exception as e:
            logger.error(f"Notify failed: {e}")
    
    await query.edit_message_text(get_text(user_id, 'order_sent'))

# ===== MESSAGES =====
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    text = update.message.text
    
    # Admin replying
    if 'replying_to' in context.user_data:
        target = context.user_data['replying_to']
        try:
            await context.bot.send_message(target, f"📩 رد من الدعم:\n\n{text}")
            await update.message.reply_text("✅ تم إرسال الرد!")
        except Exception as e:
            await update.message.reply_text(f"❌ فشل: {e}")
        del context.user_data['replying_to']
        return
    
    # Customer message
    if users_data.get(user_id, {}).get('support_active') or users_data.get(user_id, {}).get('orders'):
        user_data = users_data.get(user_id, {})
        name = user_data.get('full_name') or user_data.get('first_name') or f"User_{user_id}"
        
        msg_text = f"""
📩 رسالة جديدة

👤 {name}
🆔 `{user_id}`
📦 {user_data.get('plan', 'N/A')}

💬 {text}
"""
        keyboard = [[InlineKeyboardButton("📩 رد", callback_data=f"reply_{user_id}")]]
        
        for admin_id in ADMIN_IDS:
            try:
                await context.bot.send_message(admin_id, msg_text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode=ParseMode.MARKDOWN)
            except Exception as e:
                logger.error(f"Forward failed: {e}")
        
        await update.message.reply_text("✅ تم إرسال رسالتك للمشرفين" if user_data.get('lang') == 'ar' else "✅ Message sent to admins")

# ===== ADMIN =====
async def admin_panel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id not in ADMIN_IDS:
        await update.message.reply_text(get_text(user_id, 'admin_only'))
        return
    
    keyboard = [
        [InlineKeyboardButton(get_text(user_id, 'stats'), callback_data='admin_stats')]
    ]
    await update.message.reply_text(get_text(user_id, 'admin_panel'), reply_markup=InlineKeyboardMarkup(keyboard))

async def show_stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    total_users = len(users_data)
    total_orders = len(pending_orders)
    text = f"📊 الإحصائيات\n\n👥 المستخدمون: {total_users}\n🛒 الطلبات: {total_orders}\n🕐 {datetime.now().strftime('%H:%M:%S')}"
    await query.edit_message_text(text)

# ===== MAIN =====
def main():
    app = Application.builder().token(BOT_TOKEN).build()
    
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("admin", admin_panel))
    app.add_handler(CallbackQueryHandler(button_handler))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    print("🤖 VYNEX Bot Starting...")
    app.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == '__main__':
    main()
