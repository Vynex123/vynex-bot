# VYNEX IPTV Bot - Professional Ticket System
# Version 3.0 - Production Ready
# Built for VYNEX Company

import os
import logging
import asyncio
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, BotCommand
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes, ConversationHandler
from telegram.constants import ParseMode

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# ===== CONFIGURATION =====
BOT_TOKEN = os.environ.get("BOT_TOKEN", "8725271848:AAGiUAKiAaEK1F6buJ_wD6l1Xis9zdSXKmE")
CHANNEL_ID = os.environ.get("CHANNEL_ID", "@vynexiptv")

# Admin IDs (Haithem: 1821933706, Aissa: 1638296842)
ADMIN_IDS = [1821933706, 1638296842]
ADMIN_USERNAMES = {1821933706: "Haithem", 1638296842: "Aissa"}

# Ticket counter
ticket_counter = 1000

# Data storage (use database in production)
users_data: Dict[int, dict] = {}
tickets: Dict[str, dict] = {}
admin_sessions: Dict[int, dict] = {}

# FAQ Database
FAQ_DATA = {
    'en': {
        'what_is_neo': {
            'q': 'What is NEO 4K Pro?',
            'a': 'NEO 4K Pro is a premium IPTV server providing 20,000+ channels in 4K/FHD/HD quality. It includes live TV, sports, movies, and series (VOD).'
        },
        'how_to_subscribe': {
            'q': 'How do I subscribe?',
            'a': '1. Choose your plan on our website\n2. Complete the order in this bot\n3. Select payment method\n4. Our admin will confirm and activate your account within 5 minutes'
        },
        'trial': {
            'q': 'Do you offer a trial?',
            'a': 'Yes! We offer a 24-hour trial for $2. If you subscribe to a full plan, we deduct the $2 from your total price!'
        },
        'devices': {
            'q': 'What devices are supported?',
            'a': 'All devices: Android TV, Smart TV (Samsung/LG), Fire Stick, iPhone/iPad, Android phones, PC, and more. We provide recommended apps for each device.'
        },
        'payment_methods': {
            'q': 'What payment methods?',
            'a': 'We accept: RedotPay, PayPal, Binance (USDT), and CCP for Algeria.'
        },
        'activation_time': {
            'q': 'How long for activation?',
            'a': 'Instant! Once payment is confirmed, you receive your login credentials within 5 minutes maximum.'
        },
        'multiple_devices': {
            'q': 'Can I use on multiple devices?',
            'a': 'Standard plans support 1 device at a time. Family plans (multiple devices) are available - contact us for pricing.'
        },
        'vpn': {
            'q': 'Does it work with VPN?',
            'a': 'Yes! NEO 4K Pro works with all VPN services. We recommend using VPN if your ISP blocks IPTV.'
        },
        'channel_not_working': {
            'q': 'Channel not working?',
            'a': 'Try these steps:\n1. Check your internet connection\n2. Restart the app and device\n3. Try another channel\n4. Use VPN if needed\n5. Contact support if problem persists'
        },
        'renewal': {
            'q': 'How to renew?',
            'a': 'Contact us via this bot before expiry. We keep your credentials and extend your subscription instantly.'
        }
    },
    'ar': {
        'what_is_neo': {
            'q': 'ما هو NEO 4K Pro؟',
            'a': 'NEO 4K Pro هو سيرفر IPTV احترافي يقدم أكثر من 20,000 قناة بجودة 4K/FHD/HD. يشمل قنوات حية، رياضة، أفلام ومسلسلات (VOD).'
        },
        'how_to_subscribe': {
            'q': 'كيف أشترك؟',
            'a': '1. اختر باقتك من موقعنا\n2. أكمل الطلب في هذا البوت\n3. اختر طريقة الدفع\n4. سيقوم المشرف بتفعيل حسابك خلال 5 دقائق'
        },
        'trial': {
            'q': 'هل يوجد تجربة مجانية؟',
            'a': 'نعم! نقدم تجربة 24 ساعة مقابل 2 دولار. إذا اشتركت في باقة كاملة، نخصم الـ 2 دولار من السعر!'
        },
        'devices': {
            'q': 'ما الأجهزة المدعومة؟',
            'a': 'جميع الأجهزة: Android TV، Smart TV (Samsung/LG)، Fire Stick، iPhone/iPad، هواتف Android، PC، والمزيد. نقدم تطبيقات موصى بها لكل جهاز.'
        },
        'payment_methods': {
            'q': 'طرق الدفع المتوفرة؟',
            'a': 'نقبل: RedotPay، PayPal، Binance (USDT)، و CCP للجزائر.'
        },
        'activation_time': {
            'q': 'كم يستغرق التفعيل؟',
            'a': 'فوري! بمجرد تأكيد الدفع، تستلم بيانات الدخول خلال 5 دقائق كحد أقصى.'
        },
        'multiple_devices': {
            'q': 'هل يعمل على أكثر من جهاز؟',
            'a': 'الباقات العادية تدعم جهاز واحد في نفس الوقت. باقات العائلة (أجهزة متعددة) متوفرة - تواصل معنا للتفاصيل.'
        },
        'vpn': {
            'q': 'هل يدعم VPN؟',
            'a': 'نعم! يعمل NEO 4K Pro مع جميع خدمات VPN. نوصي باستخدام VPN إذا كان مزود الخدمة يحجب IPTV.'
        },
        'channel_not_working': {
            'q': 'القناة لا تعمل؟',
            'a': 'جرب هذه الخطوات:\n1. تأكد من اتصال الإنترنت\n2. أعد تشغيل التطبيق والجهاز\n3. جرب قناة أخرى\n4. استخدم VPN إذا لزم\n5. تواصل مع الدعم إذا استمرت المشكلة'
        },
        'renewal': {
            'q': 'كيف أجدد الاشتراك؟',
            'a': 'تواصل معنا عبر هذا البوت قبل انتهاء الاشتراك. نحتفظ ببياناتك ونمدد الاشتراك فوراً.'
        }
    }
}

# Conversation states
SELECTING_PLAN, ENTERING_NAME, ENTERING_EMAIL, ENTERING_COUNTRY, SELECTING_DEVICE, SELECTING_PAYMENT, SUPPORT_CHAT = range(7)

# Plans
PLANS = {
    'trial': {'name_en': '24 Hours Trial', 'name_ar': 'تجربة 24 ساعة', 'price': 2, 'duration': '24h'},
    '1m': {'name_en': '1 Month', 'name_ar': 'شهر واحد', 'price': 6.99, 'duration': '30 days'},
    '3m': {'name_en': '3 Months', 'name_ar': '3 أشهر', 'price': 14.99, 'duration': '90 days'},
    '6m': {'name_en': '6 Months', 'name_ar': '6 أشهر', 'price': 22.99, 'duration': '180 days'},
    '1y': {'name_en': '1 Year', 'name_ar': 'سنة كاملة', 'price': 35.99, 'duration': '365 days'}
}

DEVICES = {
    'android_tv': {'en': 'Android TV / Google TV', 'ar': 'Android TV / Google TV'},
    'samsung_lg': {'en': 'Samsung / LG Smart TV', 'ar': 'Samsung / LG Smart TV'},
    'firestick': {'en': 'Amazon Fire Stick', 'ar': 'Amazon Fire Stick'},
    'mobile': {'en': 'Mobile (Android/iOS)', 'ar': 'هاتف محمول (Android/iOS)'},
    'pc': {'en': 'PC / Laptop', 'ar': 'كمبيوتر / لابتوب'},
    'other': {'en': 'Other Device', 'ar': 'جهاز آخر'}
}

PAYMENT_METHODS = {
    'redotpay': {'en': '🔴 RedotPay', 'ar': '🔴 RedotPay'},
    'paypal': {'en': '🅿️ PayPal', 'ar': '🅿️ PayPal'},
    'binance': {'en': '💰 Binance (USDT)', 'ar': '💰 Binance (USDT)'},
    'ccp': {'en': '🏦 CCP (Algeria)', 'ar': '🏦 CCP (الجزائر)'}
}

# ===== HELPER FUNCTIONS =====

def get_text(user_id: int, key: str, lang: str = None) -> str:
    """Get text in user's language"""
    if not lang:
        lang = users_data.get(user_id, {}).get('lang', 'en')
    
    texts = {
        'en': {
            'welcome': "👋 Welcome to *VYNEX* - NEO 4K Pro Official Bot!\n\n🎬 Best IPTV Server with 4K Quality\n📡 20,000+ Channels | ⚽ Live Sports | 🎬 Movies & Series\n\nPlease select your language:",
            'main_menu': "🏠 Main Menu\n\nWhat would you like to do?",
            'new_order': "🛒 New Order",
            'my_tickets': "🎫 My Tickets",
            'faq': "❓ FAQ / Help",
            'support': "💬 Live Support",
            'language': "🌐 Language",
            'select_plan': "📦 Select your plan:",
            'enter_name': "👤 Please enter your *full name*:",
            'enter_email': "📧 Please enter your *email address*:",
            'enter_country': "🌍 Please enter your *country*:",
            'select_device': "📱 Select your *device type*:",
            'select_payment': "💳 Select *payment method*:",
            'order_summary': "📋 *Order Summary*\n\n👤 Name: {name}\n📧 Email: {email}\n🌍 Country: {country}\n📱 Device: {device}\n📦 Plan: {plan}\n💳 Payment: {payment}\n💰 Total: ${price}\n\n✅ Confirm to submit:",
            'order_confirmed': "✅ *Order Submitted Successfully!*\n\n🎫 Ticket ID: `{ticket_id}`\n\n⏳ Our team will contact you within minutes.\n💬 You can message here anytime for support.",
            'ticket_notification': "🆕 *NEW TICKET*\n\n🎫 Ticket: `{ticket_id}`\n👤 Customer: {name}\n📧 Email: {email}\n🌍 Country: {country}\n📱 Device: {device}\n📦 Plan: {plan}\n💳 Payment: {payment}\n💰 Amount: ${price}\n\n⏰ {time}",
            'support_welcome': "💬 *Live Support Activated*\n\nType your message and our team will reply shortly.\n\n⏰ Response time: Minutes (max 1 hour during peak)",
            'support_message_sent': "✅ Message sent to support team!",
            'admin_reply': "📩 *Reply from Support:*\n\n{message}",
            'faq_title': "❓ Frequently Asked Questions\n\nSelect a question:",
            'back': "🔙 Back",
            'confirm': "✅ Confirm",
            'cancel': "❌ Cancel",
            'processing': "⏳ Processing...",
            'invalid_email': "❌ Invalid email format. Please try again:",
            'ticket_closed': "✅ Ticket closed. Thank you!",
            'admin_panel': "🔧 *Admin Panel*\n\nSelect an option:",
            'stats': "📊 Statistics",
            'active_tickets': "🎫 Active Tickets",
            'broadcast': "📢 Broadcast Message",
            'no_permission': "⛔ You don't have permission!",
            'assign_to_me': "👤 Assign to Me",
            'close_ticket': "✅ Close Ticket",
            'reply_customer': "💬 Reply to Customer",
            'ticket_assigned': "✅ Ticket assigned to {admin}",
            'payment_info': "💳 *Payment Information*\n\nPlease complete payment via {payment} and send screenshot here.\n\nOur admin will verify and activate your account within 5 minutes.",
            'website_button': "🌐 Visit Website",
            'download_apps': "📲 Download Apps"
        },
        'ar': {
            'welcome': "👋 أهلاً بك في بوت *VYNEX* - NEO 4K Pro الرسمي!\n\n🎬 أفضل سيرفر IPTV بجودة 4K\n📡 أكثر من 20,000 قناة | ⚽ رياضة مباشرة | 🎬 أفلام ومسلسلات\n\nالرجاء اختيار اللغة:",
            'main_menu': "🏠 القائمة الرئيسية\n\nماذا تريد أن تفعل؟",
            'new_order': "🛒 طلب جديد",
            'my_tickets': "🎫 تذاكري",
            'faq': "❓ الأسئلة الشائعة",
            'support': "💬 دعم مباشر",
            'language': "🌐 اللغة",
            'select_plan': "📦 اختر باقتك:",
            'enter_name': "👤 الرجاء إدخال *الاسم الكامل*:",
            'enter_email': "📧 الرجاء إدخال *عنوان البريد الإلكتروني*:",
            'enter_country': "🌍 الرجاء إدخال *بلدك*:",
            'select_device': "📱 اختر *نوع الجهاز*:",
            'select_payment': "💳 اختر *طريقة الدفع*:",
            'order_summary': "📋 *ملخص الطلب*\n\n👤 الاسم: {name}\n📧 الإيميل: {email}\n🌍 الدولة: {country}\n📱 الجهاز: {device}\n📦 الباقة: {plan}\n💳 الدفع: {payment}\n💰 المجموع: ${price}\n\n✅ اضغط تأكيد لإرسال الطلب:",
            'order_confirmed': "✅ *تم إرسال الطلب بنجاح!*\n\n🎫 رقم التذكرة: `{ticket_id}`\n\n⏳ سيتواصل معك فريقنا خلال دقائق.\n💬 يمكنك مراسلتنا هنا في أي وقت للدعم.",
            'ticket_notification': "🆕 *تذكرة جديدة*\n\n🎫 التذكرة: `{ticket_id}`\n👤 الزبون: {name}\n📧 الإيميل: {email}\n🌍 الدولة: {country}\n📱 الجهاز: {device}\n📦 الباقة: {plan}\n💳 الدفع: {payment}\n💰 المبلغ: ${price}\n\n⏰ {time}",
            'support_welcome': "💬 *تم تفعيل الدعم المباشر*\n\nاكتب رسالتك وسيقوم فريقنا بالرد عليك قريباً.\n\n⏰ وقت الرد: دقائق (ساعة كحد أقصى في أوقات الذروة)",
            'support_message_sent': "✅ تم إرسال الرسالة لفريق الدعم!",
            'admin_reply': "📩 *رد من الدعم:*\n\n{message}",
            'faq_title': "❓ الأسئلة الشائعة\n\nاختر سؤالاً:",
            'back': "🔙 رجوع",
            'confirm': "✅ تأكيد",
            'cancel': "❌ إلغاء",
            'processing': "⏳ جاري المعالجة...",
            'invalid_email': "❌ صيغة البريد غير صحيحة. حاول مرة أخرى:",
            'ticket_closed': "✅ تم إغلاق التذكرة. شكراً لك!",
            'admin_panel': "🔧 *لوحة التحكم*\n\nاختر خياراً:",
            'stats': "📊 الإحصائيات",
            'active_tickets': "🎫 التذاكر النشطة",
            'broadcast': "📢 رسالة جماعية",
            'no_permission': "⛔ ليس لديك صلاحية!",
            'assign_to_me': "👤 اسند إلي",
            'close_ticket': "✅ أغلق التذكرة",
            'reply_customer': "💬 رد على الزبون",
            'ticket_assigned': "✅ تم إسناد التذكرة لـ {admin}",
            'payment_info': "💳 *معلومات الدفع*\n\nالرجاء إتمام الدفع عبر {payment} وإرسال صورة الإيصال هنا.\n\nسيقوم المشرف بالتفعيل خلال 5 دقائق.",
            'website_button': "🌐 زيارة الموقع",
            'download_apps': "📲 تحميل التطبيقات"
        }
    }
    
    return texts.get(lang, texts['en']).get(key, key)

def generate_ticket_id() -> str:
    """Generate unique ticket ID"""
    global ticket_counter
    ticket_counter += 1
    return f"VYN-{ticket_counter}"

def get_admin_name(admin_id: int) -> str:
    """Get admin name by ID"""
    return ADMIN_USERNAMES.get(admin_id, "Admin")

def is_admin(user_id: int) -> bool:
    """Check if user is admin"""
    return user_id in ADMIN_IDS

# ===== COMMAND HANDLERS =====

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Start command - Language selection"""
    user = update.effective_user
    user_id = user.id
    
    # Initialize user data
    if user_id not in users_data:
        users_data[user_id] = {
            'user_id': user_id,
            'username': user.username,
            'first_name': user.first_name,
            'lang': 'en',
            'tickets': [],
            'support_active': False
        }
    
    # Language selection keyboard
    keyboard = [
        [InlineKeyboardButton("🇬🇧 English", callback_data='set_lang_en')],
        [InlineKeyboardButton("🇦🇪 العربية", callback_data='set_lang_ar')]
    ]
    
    await update.message.reply_text(
        get_text(user_id, 'welcome'),
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode=ParseMode.MARKDOWN
    )

async def set_language(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Set user language"""
    query = update.callback_query
    await query.answer()
    
    user_id = update.effective_user.id
    lang = query.data.split('_')[-1]
    
    users_data[user_id]['lang'] = lang
    
    await show_main_menu(update, context)

async def show_main_menu(update: Update, context: ContextTypes.DEFAULT_TYPE, edit: bool = False):
    """Show main menu"""
    user_id = update.effective_user.id
    lang = users_data[user_id]['lang']
    
    keyboard = [
        [InlineKeyboardButton(get_text(user_id, 'new_order'), callback_data='new_order')],
        [InlineKeyboardButton(get_text(user_id, 'my_tickets'), callback_data='my_tickets')],
        [InlineKeyboardButton(get_text(user_id, 'faq'), callback_data='faq')],
        [InlineKeyboardButton(get_text(user_id, 'support'), callback_data='support')],
        [InlineKeyboardButton(get_text(user_id, 'language'), callback_data='change_lang')]
    ]
    
    # Add website and download buttons
    keyboard.append([
        InlineKeyboardButton(get_text(user_id, 'website_button'), url='https://iptv-neo-4k.pages.dev/'),
        InlineKeyboardButton(get_text(user_id, 'download_apps'), url='https://neo4kpro.app/neo-4k-pro-iptv-player-downloads-2/')
    ])
    
    text = get_text(user_id, 'main_menu')
    
    if edit:
        await update.callback_query.edit_message_text(
            text,
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
    else:
        await update.message.reply_text(
            text,
            reply_markup=InlineKeyboardMarkup(keyboard)
        )

# ===== ORDER FLOW =====

async def new_order_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Start new order - Select plan"""
    query = update.callback_query
    await query.answer()
    
    user_id = update.effective_user.id
    
    keyboard = []
    for key, plan in PLANS.items():
        name = plan['name_en'] if users_data[user_id]['lang'] == 'en' else plan['name_ar']
        keyboard.append([InlineKeyboardButton(
            f"{name} - ${plan['price']}",
            callback_data=f'plan_{key}'
        )])
    
    keyboard.append([InlineKeyboardButton(get_text(user_id, 'back'), callback_data='main_menu')])
    
    await query.edit_message_text(
        get_text(user_id, 'select_plan'),
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

async def select_plan(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle plan selection"""
    query = update.callback_query
    await query.answer()
    
    user_id = update.effective_user.id
    plan_key = query.data.split('_')[1]
    
    context.user_data['selected_plan'] = plan_key
    
    await query.edit_message_text(get_text(user_id, 'enter_name'))
    return ENTERING_NAME

async def enter_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle name input"""
    user_id = update.effective_user.id
    name = update.message.text
    
    context.user_data['name'] = name
    
    await update.message.reply_text(get_text(user_id, 'enter_email'))
    return ENTERING_EMAIL

async def enter_email(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle email input"""
    user_id = update.effective_user.id
    email = update.message.text
    
    # Basic email validation
    if '@' not in email or '.' not in email:
        await update.message.reply_text(get_text(user_id, 'invalid_email'))
        return ENTERING_EMAIL
    
    context.user_data['email'] = email
    
    await update.message.reply_text(get_text(user_id, 'enter_country'))
    return ENTERING_COUNTRY

async def enter_country(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle country input"""
    user_id = update.effective_user.id
    country = update.message.text
    
    context.user_data['country'] = country
    
    # Show device selection
    keyboard = []
    for key, device in DEVICES.items():
        name = device['en'] if users_data[user_id]['lang'] == 'en' else device['ar']
        keyboard.append([InlineKeyboardButton(name, callback_data=f'device_{key}')])
    
    await update.message.reply_text(
        get_text(user_id, 'select_device'),
        reply_markup=InlineKeyboardMarkup(keyboard)
    )
    return SELECTING_DEVICE

async def select_device(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle device selection"""
    query = update.callback_query
    await query.answer()
    
    user_id = update.effective_user.id
    device_key = query.data.split('_')[1]
    
    context.user_data['device'] = device_key
    
    # Show payment methods
    keyboard = []
    for key, method in PAYMENT_METHODS.items():
        name = method['en'] if users_data[user_id]['lang'] == 'en' else method['ar']
        keyboard.append([InlineKeyboardButton(name, callback_data=f'payment_{key}')])
    
    keyboard.append([InlineKeyboardButton(get_text(user_id, 'back'), callback_data='new_order')])
    
    await query.edit_message_text(
        get_text(user_id, 'select_payment'),
        reply_markup=InlineKeyboardMarkup(keyboard)
    )
    return SELECTING_PAYMENT

async def select_payment(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle payment selection and show summary"""
    query = update.callback_query
    await query.answer()
    
    user_id = update.effective_user.id
    payment_key = query.data.split('_')[1]
    
    context.user_data['payment'] = payment_key
    
    # Get plan details
    plan_key = context.user_data['selected_plan']
    plan = PLANS[plan_key]
    device = DEVICES[context.user_data['device']]
    
    lang = users_data[user_id]['lang']
    plan_name = plan['name_en'] if lang == 'en' else plan['name_ar']
    device_name = device['en'] if lang == 'en' else device['ar']
    payment_name = PAYMENT_METHODS[payment_key]['en'] if lang == 'en' else PAYMENT_METHODS[payment_key]['ar']
    
    # Show summary
    summary = get_text(user_id, 'order_summary').format(
        name=context.user_data['name'],
        email=context.user_data['email'],
        country=context.user_data['country'],
        device=device_name,
        plan=plan_name,
        payment=payment_name,
        price=plan['price']
    )
    
    keyboard = [
        [InlineKeyboardButton(get_text(user_id, 'confirm'), callback_data='confirm_order')],
        [InlineKeyboardButton(get_text(user_id, 'cancel'), callback_data='main_menu')]
    ]
    
    await query.edit_message_text(summary, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode=ParseMode.MARKDOWN)

async def confirm_order(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Confirm order and create ticket"""
    query = update.callback_query
    await query.answer()
    
    user_id = update.effective_user.id
    ticket_id = generate_ticket_id()
    
    # Get data
    plan_key = context.user_data['selected_plan']
    plan = PLANS[plan_key]
    device = DEVICES[context.user_data['device']]
    payment_key = context.user_data['payment']
    
    lang = users_data[user_id]['lang']
    
    # Create ticket
    ticket = {
        'id': ticket_id,
        'user_id': user_id,
        'username': users_data[user_id]['username'],
        'name': context.user_data['name'],
        'email': context.user_data['email'],
        'country': context.user_data['country'],
        'device': device['en'] if lang == 'en' else device['ar'],
        'plan': plan['name_en'] if lang == 'en' else plan['name_ar'],
        'plan_key': plan_key,
        'payment': PAYMENT_METHODS[payment_key]['en'] if lang == 'en' else PAYMENT_METHODS[payment_key]['ar'],
        'payment_key': payment_key,
        'price': plan['price'],
        'status': 'pending',
        'created_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'assigned_to': None,
        'messages': []
    }
    
    tickets[ticket_id] = ticket
    users_data[user_id]['tickets'].append(ticket_id)
    
    # Notify admins
    await notify_admins_new_ticket(context, ticket)
    
    # Confirm to user
    await query.edit_message_text(
        get_text(user_id, 'order_confirmed').format(ticket_id=ticket_id),
        parse_mode=ParseMode.MARKDOWN
    )
    
    # Send payment instructions
    payment_text = get_text(user_id, 'payment_info').format(payment=ticket['payment'])
    await context.bot.send_message(user_id, payment_text, parse_mode=ParseMode.MARKDOWN)
    
    # Clear user data
    context.user_data.clear()
    
    return ConversationHandler.END

async def notify_admins_new_ticket(context: ContextTypes.DEFAULT_TYPE, ticket: dict):
    """Send ticket notification to all admins"""
    lang = users_data[ticket['user_id']]['lang']
    
    text = get_text(ticket['user_id'], 'ticket_notification').format(
        ticket_id=ticket['id'],
        name=ticket['name'],
        email=ticket['email'],
        country=ticket['country'],
        device=ticket['device'],
        plan=ticket['plan'],
        payment=ticket['payment'],
        price=ticket['price'],
        time=ticket['created_at']
    )
    
    keyboard = [
        [InlineKeyboardButton("👤 Assign to Me", callback_data=f'assign_{ticket["id"]}')],
        [InlineKeyboardButton("💬 Reply", callback_data=f'reply_{ticket["id"]}')],
        [InlineKeyboardButton("✅ Close", callback_data=f'close_{ticket["id"]}')]
    ]
    
    for admin_id in ADMIN_IDS:
        try:
            await context.bot.send_message(
                admin_id,
                text,
                reply_markup=InlineKeyboardMarkup(keyboard),
                parse_mode=ParseMode.MARKDOWN
            )
        except Exception as e:
            logger.error(f"Failed to notify admin {admin_id}: {e}")

# ===== FAQ SYSTEM =====

async def show_faq(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show FAQ menu"""
    query = update.callback_query
    await query.answer()
    
    user_id = update.effective_user.id
    lang = users_data[user_id]['lang']
    
    keyboard = []
    faq_data = FAQ_DATA[lang]
    
    for key, item in faq_data.items():
        keyboard.append([InlineKeyboardButton(item['q'], callback_data=f'faq_{key}')])
    
    keyboard.append([InlineKeyboardButton(get_text(user_id, 'back'), callback_data='main_menu')])
    
    await query.edit_message_text(
        get_text(user_id, 'faq_title'),
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

async def show_faq_answer(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show FAQ answer"""
    query = update.callback_query
    await query.answer()
    
    user_id = update.effective_user.id
    lang = users_data[user_id]['lang']
    faq_key = query.data.split('_')[1]
    
    faq_item = FAQ_DATA[lang].get(faq_key)
    if faq_item:
        text = f"❓ *{faq_item['q']}*\n\n{faq_item['a']}"
        keyboard = [[InlineKeyboardButton(get_text(user_id, 'back'), callback_data='faq')]]
        
        await query.edit_message_text(
            text,
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode=ParseMode.MARKDOWN
        )

# ===== SUPPORT SYSTEM =====

async def activate_support(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Activate live support"""
    query = update.callback_query
    await query.answer()
    
    user_id = update.effective_user.id
    
    users_data[user_id]['support_active'] = True
    
    await query.edit_message_text(
        get_text(user_id, 'support_welcome'),
        parse_mode=ParseMode.MARKDOWN
    )

async def handle_support_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle support messages from users"""
    user_id = update.effective_user.id
    message_text = update.message.text
    
    if not users_data[user_id].get('support_active'):
        await update.message.reply_text("Please use /start to begin")
        return
    
    user_data = users_data[user_id]
    
    # Find active ticket or create general inquiry
    active_ticket = None
    for ticket_id in user_data['tickets']:
        if tickets[ticket_id]['status'] == 'pending':
            active_ticket = tickets[ticket_id]
            break
    
    # Format message for admins
    if active_ticket:
        text = f"💬 *New Message - Ticket `{active_ticket['id']}`*\n\n"
    else:
        text = f"💬 *General Inquiry*\n\n"
    
    text += f"👤 {user_data.get('first_name', 'User')}\n"
    text += f"🆔 `{user_id}`\n"
    if user_data.get('username'):
        text += f"📱 @{user_data['username']}\n"
    text += f"\n📝 {message_text}\n\n"
    text += f"⏰ {datetime.now().strftime('%H:%M:%S')}"
    
    # Send to admins
    keyboard = [[InlineKeyboardButton("💬 Reply", callback_data=f'reply_{user_id}')]]
    
    for admin_id in ADMIN_IDS:
        try:
            await context.bot.send_message(
                admin_id,
                text,
                reply_markup=InlineKeyboardMarkup(keyboard),
                parse_mode=ParseMode.MARKDOWN
            )
        except Exception as e:
            logger.error(f"Failed to forward to admin {admin_id}: {e}")
    
    # Confirm to user
    await update.message.reply_text(get_text(user_id, 'support_message_sent'))

# ===== ADMIN FUNCTIONS =====

async def admin_panel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Admin panel"""
    user_id = update.effective_user.id
    
    if not is_admin(user_id):
        await update.message.reply_text(get_text(user_id, 'no_permission'))
        return
    
    keyboard = [
        [InlineKeyboardButton(get_text(user_id, 'stats'), callback_data='admin_stats')],
        [InlineKeyboardButton(get_text(user_id, 'active_tickets'), callback_data='admin_tickets')],
        [InlineKeyboardButton(get_text(user_id, 'broadcast'), callback_data='admin_broadcast')]
    ]
    
    await update.message.reply_text(
        get_text(user_id, 'admin_panel'),
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode=ParseMode.MARKDOWN
    )

async def admin_stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show statistics"""
    query = update.callback_query
    await query.answer()
    
    user_id = update.effective_user.id
    
    total_users = len(users_data)
    total_tickets = len(tickets)
    pending_tickets = sum(1 for t in tickets.values() if t['status'] == 'pending')
    closed_tickets = sum(1 for t in tickets.values() if t['status'] == 'closed')
    
    text = f"""
📊 *Statistics*

👥 Total Users: {total_users}
🎫 Total Tickets: {total_tickets}
⏳ Pending: {pending_tickets}
✅ Closed: {closed_tickets}

🕐 {datetime.now().strftime('%Y-%m-%d %H:%M')}
"""
    
    keyboard = [[InlineKeyboardButton(get_text(user_id, 'back'), callback_data='admin_panel')]]
    
    await query.edit_message_text(
        text,
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode=ParseMode.MARKDOWN
    )

async def admin_show_tickets(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show active tickets"""
    query = update.callback_query
    await query.answer()
    
    user_id = update.effective_user.id
    
    pending = [t for t in tickets.values() if t['status'] == 'pending']
    
    if not pending:
        await query.edit_message_text(
            "No pending tickets! ✅",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton(get_text(user_id, 'back'), callback_data='admin_panel')]])
        )
        return
    
    text = "🎫 *Active Tickets:*\n\n"
    for ticket in pending[:10]:  # Show last 10
        assigned = f" (👤 {get_admin_name(ticket['assigned_to'])})" if ticket['assigned_to'] else ""
        text += f"• `{ticket['id']}` - {ticket['name']} - {ticket['plan']}{assigned}\n"
    
    keyboard = [[InlineKeyboardButton(get_text(user_id, 'back'), callback_data='admin_panel')]]
    
    await query.edit_message_text(
        text,
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode=ParseMode.MARKDOWN
    )

async def admin_handle_actions(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle admin actions (assign, reply, close)"""
    query = update.callback_query
    await query.answer()
    
    user_id = update.effective_user.id
    data = query.data
    
    if data.startswith('assign_'):
        ticket_id = data.split('_')[1]
        if ticket_id in tickets:
            tickets[ticket_id]['assigned_to'] = user_id
            await query.edit_message_text(
                f"✅ Ticket `{ticket_id}` assigned to you!",
                parse_mode=ParseMode.MARKDOWN
            )
    
    elif data.startswith('reply_'):
        target_id = int(data.split('_')[1])
        context.user_data['admin_reply_to'] = target_id
        await query.edit_message_text("✍️ Type your reply:")
    
    elif data.startswith('close_'):
        ticket_id = data.split('_')[1]
        if ticket_id in tickets:
            tickets[ticket_id]['status'] = 'closed'
            # Notify user
            await context.bot.send_message(
                tickets[ticket_id]['user_id'],
                get_text(tickets[ticket_id]['user_id'], 'ticket_closed')
            )
            await query.edit_message_text(f"✅ Ticket `{ticket_id}` closed!")

async def admin_reply_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle admin reply"""
    user_id = update.effective_user.id
    
    if 'admin_reply_to' not in context.user_data:
        return
    
    target_id = context.user_data['admin_reply_to']
    message_text = update.message.text
    
    try:
        await context.bot.send_message(
            target_id,
            get_text(target_id, 'admin_reply').format(message=message_text),
            parse_mode=ParseMode.MARKDOWN
        )
        await update.message.reply_text("✅ Reply sent!")
    except Exception as e:
        await update.message.reply_text(f"❌ Failed: {e}")
    
    del context.user_data['admin_reply_to']

# ===== CALLBACK HANDLER =====

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle button callbacks"""
    query = update.callback_query
    await query.answer()
    
    data = query.data
    user_id = update.effective_user.id
    
    # Language setting
    if data.startswith('set_lang_'):
        await set_language(update, context)
        await show_main_menu(update, context, edit=True)
    
    # Main menu
    elif data == 'main_menu':
        await show_main_menu(update, context, edit=True)
    
    # New order
    elif data == 'new_order':
        await new_order_start(update, context)
    
    elif data.startswith('plan_'):
        await select_plan(update, context)
    
    elif data.startswith('device_'):
        await select_device(update, context)
    
    elif data.startswith('payment_'):
        await select_payment(update, context)
    
    elif data == 'confirm_order':
        await confirm_order(update, context)
    
    # FAQ
    elif data == 'faq':
        await show_faq(update, context)
    
    elif data.startswith('faq_'):
        await show_faq_answer(update, context)
    
    # Support
    elif data == 'support':
        await activate_support(update, context)
    
    # Admin
    elif data == 'admin_panel':
        await admin_panel(update, context)
    
    elif data == 'admin_stats':
        await admin_stats(update, context)
    
    elif data == 'admin_tickets':
        await admin_show_tickets(update, context)
    
    elif data.startswith(('assign_', 'reply_', 'close_')):
        await admin_handle_actions(update, context)

# ===== ERROR HANDLER =====

async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle errors"""
    logger.error(f"Update {update} caused error {context.error}")
    
    if update and update.effective_message:
        await update.effective_message.reply_text(
            "An error occurred. Please try again or contact support."
        )

# ===== MAIN FUNCTION =====

def main():
    """Start the bot"""
    # Create application
    application = Application.builder().token(BOT_TOKEN).build()
    
    # Conversation handler for orders
    order_conv = ConversationHandler(
        entry_points=[CallbackQueryHandler(select_plan, pattern='^plan_')],
        states={
            ENTERING_NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, enter_name)],
            ENTERING_EMAIL: [MessageHandler(filters.TEXT & ~filters.COMMAND, enter_email)],
            ENTERING_COUNTRY: [MessageHandler(filters.TEXT & ~filters.COMMAND, enter_country)],
            SELECTING_DEVICE: [CallbackQueryHandler(select_device, pattern='^device_')],
            SELECTING_PAYMENT: [CallbackQueryHandler(select_payment, pattern='^payment_')]
        },
        fallbacks=[CallbackQueryHandler(button_handler)],
        per_message=False
    )
    
    # Add handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("admin", admin_panel))
    application.add_handler(order_conv)
    application.add_handler(CallbackQueryHandler(button_handler))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_support_message))
    
    # Admin reply handler
    application.add_handler(MessageHandler(
        filters.TEXT & ~filters.COMMAND & filters.User(ADMIN_IDS),
        admin_reply_message
    ))
    
    # Error handler
    application.add_error_handler(error_handler)
    
    # Set commands
    commands = [
        BotCommand("start", "Start the bot"),
        BotCommand("admin", "Admin panel (admins only)")
    ]
    
    print("🤖 VYNEX Bot Starting...")
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == '__main__':
    main()
