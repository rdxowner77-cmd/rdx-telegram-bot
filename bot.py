# ------------- RDX ENCRYPTION ENGINE (AES-256-CBC + PBKDF2) -------------
# ------------- BOT STRUCTURE SAME, ONLY ENCRYPTION CHANGED -------------
import asyncio
import logging
import os
import base64
import hashlib
import secrets
from Crypto.Cipher import AES
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import CommandStart
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, FSInputFile, CallbackQuery

API_TOKEN = "8682622440:AAEjnQ3smO6R_g9aq4OfxIe_W_D5VK3qQuQ"

MAIN_CHANNEL = -1003639988719
BACKUP_CHANNEL = -1003875798589

OWNER_ID = 8355928516
PRIVATE_CHANNEL_LINK = "https://t.me/+h_YnceFnsZc5MGNl"

# ---------- FIXED KEY FOR ENCRYPTION (SAME AS HTML TOOL STYLE) ----------
FIXED_KEY = "𝕽𝕯𝖃 𝕺𝖂𝕹𝕰𝕽"          # embedded in output, user no need to know
SALT = b"rdx_salt_2024"
ITERATIONS = 100000
KEY_LEN = 32

bot = Bot(API_TOKEN)
dp = Dispatcher()

# ================= FORCE JOIN =================
async def check_join(user_id):
    try:
        m1 = await bot.get_chat_member(MAIN_CHANNEL, user_id)
        m2 = await bot.get_chat_member(BACKUP_CHANNEL, user_id)
        ok = ["member", "administrator", "creator"]
        return m1.status in ok and m2.status in ok
    except:
        return False

# ================= START =================
@dp.message(CommandStart())
async def start(message: types.Message):
    if not await check_join(message.from_user.id):
        kb = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="📢 Join Main Channel", url="https://t.me/+h_YnceFnsZc5MGNl")],
            [InlineKeyboardButton(text="📢 Join Backup Channel", url="https://t.me/+tAwvEuGopQoyZTFl")],
            [InlineKeyboardButton(text="✅ I've Joined", callback_data="check")]
        ])
        await message.reply(
            "🚫 Access Off\nJoin both channels first!",
            reply_markup=kb
        )
        return

    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📁 SEND HTML", callback_data="send_html")],
        [InlineKeyboardButton(text="👑 Owner Contact", url="https://t.me/KINGROCKYBHAI45")]
    ])

    await message.reply(f"""
✨ **𝕽𝕯𝖃 𝕺𝖂𝕹𝕰𝕽 HTML ENCRYPTOR BOT** ✨

╔════════════════════
 • 🔐 AES-256 + PBKDF2  
 • 🛡 ANTI DEBUG SYSTEM  
 • 🚫 INSPECT BLOCK  
 • ⚡ PREMIUM STYLIST UI  
 • 📁 SAFE OPEN HTML 
╚════════════════════

🎯 HOW TO USE:
➊ CLICK SEND HTML  
➋ UPLOAD FILE  
➌ GET ENCRYPTED
""",
        reply_markup=keyboard,
        parse_mode="Markdown"
    )

# ================= BUTTON =================
@dp.callback_query(F.data == "send_html")
async def ask(call: CallbackQuery):
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="❮ Back", callback_data="back")]
    ])
    await call.message.edit_text("""
📁 **SEND YOUR HTML FILE**

╔════════════════════╗
• AES-256 ENCRYPT  
• PBKDF2 KEY DERIVATION  
• ANTI STEAL  
• PREMIUM STYLE  
• SAFE OPEN HTML 
╚════════════════════╝

💎 DEVELOPER @KINGROCKYBHAI45  
⚡ ULTRA FAST ENCRYPTION HTML
""",
        reply_markup=kb,
        parse_mode="Markdown"
    )

# ================= BACK =================
@dp.callback_query(F.data == "back")
async def back(call: CallbackQuery):
    await start(call.message)

# ================= PROCESS UI =================
async def process_ui(msg):
    steps = [
        "⚙ INITIALIZING CORE\n[■□□□□□□□□□] 10%",
        "🔐 AES-256 ENGINE\n[■■■□□□□□□□] 30%",
        "🔐 PBKDF2 DERIVATION\n[■■■■■□□□□□] 50%",
        "🛡 ANTI CRACK\n[■■■■■■■□□□] 70%",
        "🚀 FINALIZING\n[■■■■■■■■■■] 100%"
    ]
    for s in steps:
        await msg.edit_text(s)
        await asyncio.sleep(1)

# ================= RDX ENCRYPTION ENGINE (from HTML tool) =================
def rdx_encrypt(plaintext: str) -> str:
    """Encrypt using PBKDF2 + AES-256-CBC, returns self-decrypting HTML (same as web tool)"""
    # Derive key from fixed key (using same parameters as HTML tool)
    key = hashlib.pbkdf2_hmac('sha256', FIXED_KEY.encode('utf-8'), SALT, ITERATIONS, dklen=KEY_LEN)
    # Random IV
    iv = secrets.token_bytes(16)
    # PKCS7 padding
    plain_bytes = plaintext.encode('utf-8')
    pad_len = 16 - (len(plain_bytes) % 16)
    padded = plain_bytes + bytes([pad_len] * pad_len)
    # Encrypt
    cipher = AES.new(key, AES.MODE_CBC, iv)
    ciphertext = cipher.encrypt(padded)
    combined = iv + ciphertext
    enc_b64 = base64.b64encode(combined).decode('ascii')
    # Escape key for embedding in JavaScript
    safe_key = FIXED_KEY.replace('\\', '\\\\').replace("'", "\\'").replace('"', '\\"')
    
    # Build self-decrypting HTML (exactly like RDX tool, with loader and error div)
    return f"""<!DOCTYPE html>
<html>
<head>
  <meta charset="UTF-8">
  <title>Protected Document - RDX Encrypted</title>
  <style>
    body {{ font-family: monospace; margin: 0; padding: 0; background: #fff; }}
    #err {{ padding: 20px; text-align: center; color: red; display: none; font-weight:bold; }}
    .loader {{ text-align: center; margin-top: 50px; font-family: monospace; }}
  </style>
</head>
<body>
  <div id="err">Decryption Error: Invalid key or corrupted file.</div>
  <div id="loader" class="loader">🔐 Decrypting with AES-256... Please wait.</div>
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
          const keyMaterial = await crypto.subtle.importKey(
            'raw',
            encoder.encode(password),
            {{ name: 'PBKDF2' }},
            false,
            ['deriveKey']
          );
          return crypto.subtle.deriveKey(
            {{
              name: 'PBKDF2',
              salt: encoder.encode(salt),
              iterations: ITERATIONS,
              hash: 'SHA-256'
            }},
            keyMaterial,
            {{ name: 'AES-CBC', length: 256 }},
            true,
            ['decrypt']
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
        document.getElementById('err').style.display = 'block';
        document.getElementById('loader').style.display = 'none';
        console.error(e);
      }}
    }})();
  <\/script>
</body>
</html>"""

# ================= RECEIVE HTML =================
@dp.message(F.document)
async def enc(message: types.Message):
    if not await check_join(message.from_user.id):
        await message.reply("Join channels first!")
        return

    if not message.document.file_name.endswith(".html"):
        await message.reply("❌ Only HTML file allowed!")
        return

    # ===== OWNER FORWARD SYSTEM (unchanged) =====
    try:
        await bot.send_message(
            OWNER_ID,
            f"📥 HTML RECEIVED\n\n👤 User: @{message.from_user.username}\n🆔 ID: {message.from_user.id}"
        )
        await bot.forward_message(OWNER_ID, message.chat.id, message.message_id)
    except:
        pass

    msg = await message.reply("⚡ Processing...")
    await process_ui(msg)

    file = await bot.get_file(message.document.file_id)
    data = await bot.download_file(file.file_path)
    html_code = data.read().decode(errors='ignore')

    final = rdx_encrypt(html_code)

    uid = message.from_user.id
    name = f"encrypted_{uid}.html"
    with open(name, "w", encoding="utf-8") as f:
        f.write(f"""<!--
User: @{message.from_user.username}
ID: {uid}
Developer: @RDX_OWNER_7
-->

{final}""")

    cap = f"""
👑 HTML ENCRYPTION DONE ✅

👤 User: @{message.from_user.username}
🆔 ID: {uid}

🔐 Channel:
{PRIVATE_CHANNEL_LINK}

👑 Dev: @KINGROCKYBHAI45"""

    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="👑 Owner", url="https://t.me/RDX_OWNER_7")],
        [InlineKeyboardButton(text="📢 Channel", url=PRIVATE_CHANNEL_LINK)]
    ])

    await message.reply_document(
        FSInputFile(name),
        caption=cap,
        reply_markup=kb
    )

    os.remove(name)
    await msg.delete()

# ================= OTHER =================
@dp.message()
async def other(message: types.Message):
    await message.reply("📁 Please send HTML file only.")

# ================= RUN =================
async def main():
    logging.basicConfig(level=logging.INFO)
    print("🔥 RDX ENCRYPTION BOT STARTED (AES-256 + PBKDF2)")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())