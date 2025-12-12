# bot/commands/referral.py

from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ContextTypes
from bot.database import get_referrals, build_referral_tree, get_user, set_premium

async def referral_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    user = get_user(user_id)

    if not user:
        await update.message.reply_text("Сначала начните бота: /start")
        return

    # Реферальная ссылка
    ref_link = f"https://t.me/LeoHelperBot?start={user_id}"

    # Построим дерево
    tree = build_referral_tree(user_id)
    level1 = len(tree.get(1, []))
    level2 = len(tree.get(2, []))
    level3 = len(tree.get(3, []))

    keyboard = [
        [InlineKeyboardButton("🔗 Скопировать ссылку", url=ref_link)],
        [InlineKeyboardButton("👥 Мои рефералы", callback_data="referrals_list")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text(
        f"👥 **Реферальная система**\n\n"
        f"🔗 Ваша ссылка: `{ref_link}`\n\n"
        f"📊 Ваши рефералы:\n"
        f"1️⃣ Уровень: {level1} человек (+7 дней премиума)\n"
        f"2️⃣ Уровень: {level2} человек (+3 дня)\n"
        f"3️⃣ Уровень: {level3} человек (+1 день)\n\n"
        f"🎁 За каждого приглашённого — премиум-дни!",
        reply_markup=reply_markup,
        parse_mode='Markdown'
    )

async def show_referrals(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    tree = build_referral_tree(user_id)

    msg = "👥 *Ваши рефералы*\n\n"
    for level in [1, 2, 3]:
        refs = tree.get(level, [])
        if refs:
            msg += f"*{level} уровень* ({len(refs)}):\n"
            for ref_id in refs[:10]:  # первые 10
                ref_user = get_user(ref_id)
                name = ref_user['first_name'] if ref_user else str(ref_id)
                msg += f"  • {name} (ID: {ref_id})\n"
            if len(refs) > 10:
                msg += f"  ... и ещё {len(refs) - 10}\n"
            msg += "\n"

    if msg == "👥 *Ваши рефералы*\n\n":
        msg = "🚫 У вас пока нет рефералов."

    await update.callback_query.message.reply_text(msg, parse_mode='Markdown')
    await update.callback_query.answer()
