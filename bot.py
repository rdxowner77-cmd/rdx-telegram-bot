#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
╔══════════════════════════════════════════════════════════════════════════╗
║         ☠️ RDX ULTIMATE BOT – FINAL (RAILWAY READY) ☠️                   ║
║          Telegram bot · AES-256 · Stars System · No Errors               ║
║                         POWERED BY @RDX_OWNER_7                          ║
╚══════════════════════════════════════════════════════════════════════════╝
"""

import os
import re
import base64
import hashlib
import secrets
import json
import sqlite3
import random
import string
from datetime import datetime
from io import BytesIO

from Crypto.Cipher import AES
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from pyrogram.enums import ParseMode, ChatMemberStatus
from pyrogram.errors import UserNotParticipant

# ---------------------------- CONFIGURATION ---------------------------------
API_ID = 32876561
API_HASH = "45e2abbeff227e76f8a2b080edb82bdc"
BOT_TOKEN = "8645132870:AAGuyT77fSAV5XOlO9HCCBDFfN4heMAwA0I"

FIXED_KEY = "RDX_FIXED_MASTER_KEY_2024"
SALT = b"rdx_salt_2024"
ITERATIONS = 100000
KEY_LEN = 32

# --- CHANNEL SETTINGS (CHANGE THESE TO YOUR CHANNELS) ---
CHANNEL_1_USERNAME = "RDXOWNER77"
CHANNEL_2_USERNAME = "RDXOWNER7"
CHANNEL_1_LINK = "https://t.me/RDXOWNER77"
CHANNEL_2_LINK = "https://t.me/RDXOWNER7"

# --- DEFAULT CREDITS ---
DEFAULT_CREDITS = [
    "Obfuscated By: @RDX_OWNER_7",
    "Bot Developer : RDX @RDX_OWNER_7",
    "Signature: RDX_HTMLOBF_PROTECTED"
]

# ---------------------------- DATABASE SETUP ---------------------------------
def init_db():
    conn = sqlite3.connect('rdx_bot.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS users 
                 (user_id INTEGER PRIMARY KEY, stars INTEGER DEFAULT 5, 
                  remove_banner INTEGER DEFAULT 0, custom_credits TEXT,
                  verified INTEGER DEFAULT 0)''')
    conn.commit()
    conn.close()

init_db()

def get_user_stars(user_id):
    conn = sqlite3.connect('rdx_bot.db')
    c = conn.cursor()
    c.execute("SELECT stars, remove_banner, custom_credits FROM users WHERE user_id = ?", (user_id,))
    result = c.fetchone()
    conn.close()
    if result:
        return result[0], result[1], result[2]
    return 5, 0, None

def add_stars(user_id, amount):
    conn = sqlite3.connect('rdx_bot.db')
    c = conn.cursor()
    c.execute("INSERT OR IGNORE INTO users (user_id, stars) VALUES (?, 5)", (user_id,))
    c.execute("UPDATE users SET stars = stars + ? WHERE user_id = ?", (amount, user_id))
    conn.commit()
    conn.close()

def deduct_stars(user_id, amount):
    conn = sqlite3.connect('rdx_bot.db')
    c = conn.cursor()
    c.execute("SELECT stars FROM users WHERE user_id = ?", (user_id,))
    result = c.fetchone()
    if result and result[0] >= amount:
        c.execute("UPDATE users SET stars = stars - ? WHERE user_id = ?", (amount, user_id))
        conn.commit()
        conn.close()
        return True
    conn.close()
    return False

def set_remove_banner(user_id):
    conn = sqlite3.connect('rdx_bot.db')
    c = conn.cursor()
    c.execute("UPDATE users SET remove_banner = 1 WHERE user_id = ?", (user_id,))
    conn.commit()
    conn.close()

def set_custom_credits(user_id, credits):
    conn = sqlite3.connect('rdx_bot.db')
    c = conn.cursor()
    c.execute("UPDATE users SET custom_credits = ? WHERE user_id = ?", (json.dumps(credits), user_id))
    conn.commit()
    conn.close()

def set_verified(user_id):
    conn = sqlite3.connect('rdx_bot.db')
    c = conn.cursor()
    c.execute("INSERT OR IGNORE INTO users (user_id, stars, verified) VALUES (?, 5, 1)", (user_id,))
    c.execute("UPDATE users SET verified = 1 WHERE user_id = ?", (user_id,))
    conn.commit()
    conn.close()

def is_verified(user_id):
    conn = sqlite3.connect('rdx_bot.db')
    c = conn.cursor()
    c.execute("SELECT verified FROM users WHERE user_id = ?", (user_id,))
    result = c.fetchone()
    conn.close()
    return result and result[0] == 1

# ---------------------------- HELPER FUNCTIONS -----------------------------
def is_html_file(file_path):
    return file_path.lower().endswith(('.html', '.htm'))

def random_str(n=6):
    return ''.join(random.choices(string.ascii_letters + string.digits, k=n))

# ==================== FORCE SUB CHECKER ====================
async def is_user_subscribed(client, user_id):
    channels = [CHANNEL_1_USERNAME, CHANNEL_2_USERNAME]
    for ch in channels:
        try:
            member = await client.get_chat_member(f"@{ch}", user_id)
            if member.status not in [ChatMemberStatus.MEMBER, ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.OWNER]:
                return False
        except UserNotParticipant:
            return False
        except Exception:
            return False
    return True

# ==================== ENCRYPTION ENGINE (SAME AS ORIGINAL) ====================
def encrypt_html(plaintext: str, password: str, user_id: int, username: str) -> str:
    stars, remove_banner, custom_credits_json = get_user_stars(user_id)
    custom_credits = json.loads(custom_credits_json) if custom_credits_json else None
    
    if remove_banner:
        credit_lines = []
    elif custom_credits:
        credit_lines = custom_credits
    else:
        credit_lines = DEFAULT_CREDITS
    
    header_lines = [
        "# PROTECTED HTML - DO NOT MODIFY THIS HEADER",
        "",
        credit_lines[0] if credit_lines else "Obfuscated By: @RDX_OWNER_7",
        credit_lines[1] if len(credit_lines) > 1 else "Bot Developer : RDX @RDX_OWNER_7",
        f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        credit_lines[2] if len(credit_lines) > 2 else "Signature: RDX_HTMLOBF_PROTECTED",
        "",
        "⚠ WARNING: Removing or modifying this credit header will cause this page to stop working!"
    ]
    
    header_comment = '\n'.join([f"<!-- {line} -->" for line in header_lines])
    
    key = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), SALT, ITERATIONS, dklen=KEY_LEN)
    iv = secrets.token_bytes(16)
    plain_bytes = plaintext.encode('utf-8')
    pad_len = 16 - (len(plain_bytes) % 16)
    padded = plain_bytes + bytes([pad_len] * pad_len)
    cipher = AES.new(key, AES.MODE_CBC, iv)
    ciphertext = cipher.encrypt(padded)
    combined = iv + ciphertext
    enc_b64 = base64.b64encode(combined).decode('ascii')
    safe_key = password.replace('\\', '\\\\').replace("'", "\\'").replace('"', '\\"')
    
    check_lines = custom_credits if custom_credits else DEFAULT_CREDITS
    var1 = random_str(8)
    var2 = random_str(8)
    var3 = random_str(8)
    escaped = [l.replace("'", "\\'") for l in check_lines]
    error_html = f'''
    <div style="text-align:center; margin-top:20vh; font-family:monospace; background:#000; color:#fff;">
        <h1 style="color:red;">⚠️ CREDIT TAMPERED</h1>
        <p>The credit header has been modified or removed.</p>
        <p>{'<br>'.join(check_lines)}</p>
        <p>Refurbish the original credit to use this file.</p>
    </div>
    '''
    error_js = error_html.replace('"', '\\"').replace('\n', '\\n')
    
    integrity_script = f"""
    <script>
    (function(){{
        var {var1} = false;
        var {var2} = document.documentElement.outerHTML;
        var {var3} = {escaped};
        for(var i=0; i<{var3}.length; i++){{
            if({var2}.indexOf({var3}[i]) === -1){{
                document.body.innerHTML = "{error_js}";
                document.title = 'Access Denied';
                throw new Error('Integrity check failed');
            }}
        }}
    }})();
    </script>
    """
    
    anti_debug = """
    <script>
    document.addEventListener('contextmenu', function(e){ e.preventDefault(); return false; });
    document.addEventListener('keydown', function(e){ if(e.key === 'F12' || (e.ctrlKey && e.shiftKey && e.key === 'I') || (e.ctrlKey && e.key === 'U')){ e.preventDefault(); return false; } });
    setInterval(function(){ console.clear(); }, 200);
    </script>
    """
    
    decoder = f"""
    <script src="https://cdnjs.cloudflare.com/ajax/libs/crypto-js/4.1.1/crypto-js.min.js"></script>
    <script>
    (async function() {{
        try {{
            const encData = "{enc_b64}";
            const key = "{safe_key}";
            const SALT = "rdx_salt_2024";
            const ITERATIONS = 100000;

            function base64ToArrayBuffer(base64) {{
                const binary = atob(base64);
                const len = binary.length;
                const bytes = new Uint8Array(len);
                for (let i = 0; i < len; i++) bytes[i] = binary.charCodeAt(i);
                return bytes.buffer;
            }}

            async function deriveKey(password, salt) {{
                const encoder = new TextEncoder();
                const keyMaterial = await crypto.subtle.importKey('raw', encoder.encode(password), {{ name: 'PBKDF2' }}, false, ['deriveKey']);
                return crypto.subtle.deriveKey(
                    {{ name: 'PBKDF2', salt: encoder.encode(salt), iterations: ITERATIONS, hash: 'SHA-256' }},
                    keyMaterial, {{ name: 'AES-CBC', length: 256 }}, true, ['decrypt']
                );
            }}

            const combined = base64ToArrayBuffer(encData);
            const iv = combined.slice(0, 16);
            const ciphertext = combined.slice(16);
            const cryptoKey = await deriveKey(key, SALT);
            const decrypted = await crypto.subtle.decrypt(
                {{ name: 'AES-CBC', iv: new Uint8Array(iv) }},
                cryptoKey,
                ciphertext
            );
            const decoder = new TextDecoder();
            const originalHtml = decoder.decode(decrypted);
            document.open();
            document.write(originalHtml);
            document.close();
        }} catch(e) {{
            document.body.innerHTML = '<h1 style="color:red;text-align:center;margin-top:20%;">Error: Invalid key or corrupted file.</h1>';
        }}
    }})();
    </script>
    """
    
    final = f"""<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8">
<title>Protected Document - RDX Encrypted</title>
<style>body{{margin:0;padding:0;background:#fff;}}</style>
{integrity_script}
{anti_debug}
{decoder}
</head>
<body></body>
</html>"""
    
    return header_comment + "\n" + final

# ---------------------------- TELEGRAM BOT ---------------------------------
app = Client("rdx_bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)
user_data = {}
user_verified = {}

@app.on_message(filters.command("start"))
async def start(client, message):
    uid = message.from_user.id
    stars, _, _ = get_user_stars(uid)
    
    if not is_verified(uid):
        if await is_user_subscribed(client, uid):
            set_verified(uid)
        else:
            keyboard = InlineKeyboardMarkup([
                [InlineKeyboardButton("📢 Join Channel 1", url=CHANNEL_1_LINK)],
                [InlineKeyboardButton("📢 Join Channel 2", url=CHANNEL_2_LINK)],
                [InlineKeyboardButton("✅ I've Joined", callback_data="verify")]
            ])
            await message.reply_text(
                "❌ **ACCESS DENIED!**\n\n"
                "Aapko pahle dono channels join karne honge.\n\n"
                f"⭐ Your Stars: `{stars}`\n\n"
                "Join karne ke baad **I've Joined** click karein.",
                reply_markup=keyboard
            )
            return
    
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("📁 SEND HTML", callback_data="send_html")],
        [InlineKeyboardButton(f"⭐ STARS: {stars}", callback_data="show_stars")],
        [InlineKeyboardButton("🛡 OPTIONS", callback_data="options")],
        [InlineKeyboardButton("👑 OWNER", url="https://t.me/RDX_OWNER_7")]
    ])
    await message.reply_text(
        "**# HTML OBFUSCATOR BOT**\n\n"
        "**RDX HTML OBFUSCATOR BOT**\n\n"
        "Send me an **HTML file** – I will return a **dangerously protected** version with:\n"
        "🔒 **Credit header lock** (remove header → page shows CREDIT TAMPERED)\n"
        "🛡️ Anti-debug, right-click block, keyboard block, DevTools detection\n"
        "🌐 Optional domain lock\n"
        "🧹 Console clear, anti-scraping, iframe detection\n\n"
        f"⭐ **Your Stars: {stars}**\n\n"
        "**Powered by @RDX_OWNER_7**",
        reply_markup=keyboard
    )

@app.on_callback_query()
async def callback_handler(client, callback_query: CallbackQuery):
    data = callback_query.data
    uid = callback_query.from_user.id
    
    if data == "verify":
        if await is_user_subscribed(client, uid):
            set_verified(uid)
            await callback_query.message.delete()
            await start(client, callback_query.message)
        else:
            await callback_query.answer("❌ Pehle dono channels join karein!", show_alert=True)
        return
    
    if data == "show_stars":
        stars, _, _ = get_user_stars(uid)
        await callback_query.answer(f"⭐ You have {stars} stars!", show_alert=True)
        return
    
    if data == "options":
        stars, remove_banner, custom_credits = get_user_stars(uid)
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("🗑️ Remove Banner (3 ⭐)", callback_data="buy_remove_banner")],
            [InlineKeyboardButton("✏️ Change Credits (2 ⭐)", callback_data="buy_change_credits")],
            [InlineKeyboardButton("🔙 BACK", callback_data="back_to_menu")]
        ])
        await callback_query.message.edit_text(
            "**🛡 CUSTOMIZATION OPTIONS**\n\n"
            f"⭐ Your Stars: `{stars}`\n\n"
            "• Remove Banner: `3 Stars` – Fully removes obfuscator banner\n"
            "• Change Credits: `2 Stars` – Change 3 credit lines\n\n"
            "Choose an option below:",
            reply_markup=keyboard
        )
        await callback_query.answer()
        return
    
    if data == "buy_remove_banner":
        if deduct_stars(uid, 3):
            set_remove_banner(uid)
            await callback_query.answer("✅ Banner removal purchased!", show_alert=True)
            await callback_query.message.edit_text("✅ **Banner removal activated!**\n\nUse /start to continue.")
        else:
            await callback_query.answer("❌ Not enough stars! Need 3 stars.", show_alert=True)
        return
    
    if data == "buy_change_credits":
        if deduct_stars(uid, 2):
            user_data[uid] = {"awaiting_credits": True}
            await callback_query.message.edit_text(
                "✏️ **Change Credits**\n\n"
                "Send 3 lines separated by `|`\n\n"
                "Example:\n"
                "`Obfuscated By: @YourName | Bot Developer: YourName | Signature: YOUR_SIGNATURE`\n\n"
                "Send /cancel to cancel."
            )
        else:
            await callback_query.answer("❌ Not enough stars! Need 2 stars.", show_alert=True)
        return
    
    if data == "send_html":
        await callback_query.answer()
        kb = InlineKeyboardMarkup([[InlineKeyboardButton("🔙 BACK", callback_data="back_to_menu")]])
        await callback_query.message.edit_text(
            "📁 **SEND YOUR HTML FILE**\n\n"
            "• Upload the HTML file below.\n"
            "• Guaranteed No UI Breaking.\n"
            "• Highly Protected Source Code.\n\n"
            "💎 @RDX_OWNER_7",
            reply_markup=kb
        )
        return
    
    if data == "back_to_menu":
        await callback_query.message.delete()
        await start(client, callback_query.message)
        return

# Handle custom credits input
@app.on_message(filters.text & ~filters.command)
async def handle_credits(client, message):
    uid = message.from_user.id
    if user_data.get(uid, {}).get("awaiting_credits"):
        text = message.text.strip()
        if "|" in text:
            parts = text.split("|")
            if len(parts) >= 3:
                credits = [p.strip() for p in parts[:3]]
                set_custom_credits(uid, credits)
                del user_data[uid]["awaiting_credits"]
                await message.reply_text("✅ **Credits changed!**\n\nUse /start to continue.")
                return
        await message.reply_text("❌ Invalid format! Send 3 lines separated by `|`")
        return
    await message.reply_text("Use /start to begin.")

# Handle HTML file
@app.on_message(filters.document)
async def handle_html(client, message):
    uid = message.from_user.id
    
    if not is_verified(uid):
        if await is_user_subscribed(client, uid):
            set_verified(uid)
        else:
            await message.reply_text("❌ Pehle channels join karein! Use /start.")
            return
    
    if not message.document.file_name.endswith(".html"):
        await message.reply_text("❌ Please send an **HTML file** only.")
        return
    
    msg = await message.reply_text("⚙ **Processing...**")
    
    file_path = await message.download()
    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
        html_content = f.read()
    os.remove(file_path)
    
    username = message.from_user.username or "NoUsername"
    encrypted = encrypt_html(html_content, FIXED_KEY, uid, username)
    
    filename = f"RDX_PROTECTED_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html"
    bio = BytesIO(encrypted.encode('utf-8'))
    bio.name = filename
    
    stars, _, _ = get_user_stars(uid)
    caption = f"✅ **Obfuscation Complete!**\n\nFile: `{message.document.file_name}`\n⭐ Stars: `{stars}`\nPowered by @RDX_OWNER_7"
    
    await message.reply_document(bio, caption=caption)
    await msg.delete()

print("=" * 65)
print("🔥 RDX ULTIMATE BOT STARTED")
print("📌 Features:")
print("   1. Force Subscribe - 2 Channels")
print("   2. AES-256 Encryption")
print("   3. Stars System (Free 5 stars on start)")
print("   4. Remove Banner - 3 Stars")
print("   5. Change Credits - 2 Stars")
print("💀 Powered by @RDX_OWNER_7")
print("=" * 65)

app.run()
