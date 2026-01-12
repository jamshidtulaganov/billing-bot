import asyncio, os, re, smtplib, time, tempfile, sys
from email.message import EmailMessage
from datetime import datetime
from aiogram import Bot, Dispatcher
from aiogram.types import Message, KeyboardButton, ReplyKeyboardMarkup
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
import pdfplumber
from dotenv import load_dotenv
from zoho_drive import ZohoWorkDrive

# Fix encoding for Windows console
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding='utf-8')
    sys.stderr.reconfigure(encoding='utf-8')


# ==============================
# CONFIG
# ==============================
load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")
SMTP_SERVER = os.getenv("SMTP_SERVER")
SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
SMTP_USERNAME = os.getenv("SMTP_USERNAME", "emailapikey")
EMAIL_ADDRESS = os.getenv("EMAIL_ADDRESS")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")
EXCLUDED_EMAIL = os.getenv("EXCLUDED_EMAIL", "info@tsst.ai").lower()

# Zoho WorkDrive Configuration
ZOHO_CLIENT_ID = os.getenv("ZOHO_CLIENT_ID")
ZOHO_CLIENT_SECRET = os.getenv("ZOHO_CLIENT_SECRET")
ZOHO_REFRESH_TOKEN = os.getenv("ZOHO_REFRESH_TOKEN")
ZOHO_API_DOMAIN = os.getenv("ZOHO_API_DOMAIN")

ZOHO_INVOICE_FOLDER_ID = os.getenv("ZOHO_INVOICE_FOLDER_ID")
ZOHO_ZELLE_FOLDER_ID = os.getenv("ZOHO_ZELLE_FOLDER_ID")
ZOHO_DEBTOR_FOLDER_ID = os.getenv("ZOHO_DEBTOR_FOLDER_ID")
ZOHO_SENT_FOLDER_ID = os.getenv("ZOHO_SENT_FOLDER_ID")

ALLOWED_USERS = set(int(x) for x in os.getenv("ALLOWED_USERS", "").split(",") if x.strip())

EMAIL_TEMPLATES = {
    "invoice": ("Invoice & Report — Period Review", "Hello,\n\nPlease find attached the invoice.\n\nThanks,\nTSS Technology\n"),
    "zelle": ("Request for Zelle Transfer", "Hello dear customer!\nWe hope this message finds you well.\n\nWe would like to kindly remind you about the pending payment for the invoice related to our recent transaction.\nTo ensure a seamless and efficient payment process, we highly recommend utilizing Zelle as your preferred payment method.\nWe kindly request you to proceed with the Zelle transfer using the following payment details:\n\nRecipient Name: TSS Technology LLC\nRecipient account: info@tsst.ai\n\nThanks, Billing Department\nTSS Technology\n"),
    "debtor": ("URGENT! Fuel Card Deactivation Message", "Hello,\n\nWe regret to inform you that your fuel cards have been deactivated due to an unpaid invoice. Immediate action is required to resolve this matter and reactivate your cards.\n\nTo reinstate the functionality of your fuel cards, please contact us at your earliest convenience. Our team is available to assist you in settling the outstanding amount and reinstating your cards promptly.\n\nThanks, Billing Department\nTSS Technology\n")
}

TYPE_FOLDER_IDS = {"invoice": ZOHO_INVOICE_FOLDER_ID, "zelle": ZOHO_ZELLE_FOLDER_ID, "debtor": ZOHO_DEBTOR_FOLDER_ID}

# Initialize Zoho WorkDrive
zoho = ZohoWorkDrive(ZOHO_CLIENT_ID, ZOHO_CLIENT_SECRET, ZOHO_REFRESH_TOKEN, ZOHO_API_DOMAIN)


# ==============================
# STATES
# ==============================
class Flow(StatesGroup):
    picking_type = State()
    awaiting_ids = State()


# ==============================
# UTILITIES
# ==============================
def is_allowed(uid): return uid in ALLOWED_USERS


def log_console(msg: str):
    now = datetime.now().strftime("%H:%M:%S")
    print(f"[{now}] {msg}")


def extract_email(pdf_path):
    try:
        with pdfplumber.open(pdf_path) as pdf:
            for page in pdf.pages:
                text = page.extract_text() or ""
                for e in re.findall(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}", text):
                    if e.lower() != EXCLUDED_EMAIL:
                        return e
    except Exception as e:
        log_console(f"[WARN] Cannot extract email from {pdf_path}: {e}")
    return None


def find_pdfs_in_zoho(folder_id, carrier_ids):
    """Match PDFs from Zoho WorkDrive by filename"""
    matches = {cid: [] for cid in carrier_ids}

    try:
        files = zoho.list_files(folder_id)
        log_console(f"[DEBUG] Found {len(files)} files in Zoho folder")

        for file_item in files:
            attrs = file_item['attributes']
            fname = attrs['name']
            ftype = attrs['type']

            log_console(f"[DEBUG] Checking file: {fname} (type: {ftype})")

            # Skip folders
            if ftype == 'folder':
                log_console(f"[DEBUG] Skipping {fname} - it's a folder")
                continue

            if not fname.lower().endswith('.pdf'):
                log_console(f"[DEBUG] Skipping {fname} - not a PDF")
                continue

            file_id = file_item['id']
            low = fname.lower()

            for cid in carrier_ids:
                # More flexible pattern: match if carrier ID appears with word boundaries
                # Matches: _5811056_, -5811056-, 5811056_, _5811056, etc.
                pattern = rf"(?:^|[\s_\-]){cid}(?:[\s_\-\.]|$)"
                if re.search(pattern, low):
                    log_console(f"[DEBUG] MATCH! {fname} matches carrier ID {cid}")
                    matches[cid].append({'id': file_id, 'name': fname})
                else:
                    log_console(f"[DEBUG] No match: {fname} does not match carrier ID {cid}")

    except Exception as e:
        log_console(f"[ERROR] Failed to list files from Zoho: {e}")

    return matches


async def send_email_async(to, subject, body, pdf_path):
    """Send one email asynchronously with its own SMTP session."""
    try:
        msg = EmailMessage()
        msg["From"], msg["To"], msg["Subject"] = EMAIL_ADDRESS, to, subject
        msg.set_content(body)
        with open(pdf_path, "rb") as f:
            msg.add_attachment(f.read(), maintype="application", subtype="pdf", filename=os.path.basename(pdf_path))

        def send():
            with smtplib.SMTP(SMTP_SERVER, SMTP_PORT, timeout=25) as s:
                s.starttls()
                s.login(SMTP_USERNAME, EMAIL_PASSWORD)
                s.send_message(msg)

        await asyncio.to_thread(send)
        return "OK"
    except Exception as e:
        return f"ERR: {e}"


def move_to_sent_zoho(file_id, file_name, tp):
    """Move file to Sent Files folder in Zoho WorkDrive"""
    try:
        # Get the subfolder ID for the document type in Sent Files
        subfolder_id = zoho.get_subfolder_id(ZOHO_SENT_FOLDER_ID, tp.capitalize())

        if not subfolder_id:
            log_console(f"[WARN] Subfolder '{tp.capitalize()}' not found in Sent Files, using parent folder")
            subfolder_id = ZOHO_SENT_FOLDER_ID

        # Download the file temporarily
        temp_dir = tempfile.gettempdir()
        temp_path = os.path.join(temp_dir, file_name)

        zoho.download_file(file_id, temp_path)

        # Upload to Sent Files folder
        zoho.upload_file(subfolder_id, temp_path)

        # Delete from original folder
        zoho.delete_file(file_id)

        # Clean up temp file
        if os.path.exists(temp_path):
            os.remove(temp_path)

        log_console(f"[MOVED] {file_name} → Sent Files/{tp.capitalize()}")
        return True

    except Exception as e:
        log_console(f"[ERROR] Failed to move file {file_name}: {e}")
        return False


# ==============================
# BOT HANDLERS
# ==============================
def home_keyboard():
    return ReplyKeyboardMarkup(keyboard=[
        [KeyboardButton(text="Invoice"), KeyboardButton(text="Zelle"), KeyboardButton(text="Debtor")]
    ], resize_keyboard=True)


def back_keyboard():
    return ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text="Go Back")]], resize_keyboard=True)


async def cmd_start(msg: Message, state: FSMContext):
    if not is_allowed(msg.from_user.id):
        log_console(f"[DENY] Unauthorized user: {msg.from_user.id}")
        return
    await state.set_state(Flow.picking_type)
    await msg.answer("Select document type:", reply_markup=home_keyboard())


async def handle_type(msg: Message, state: FSMContext):
    t = msg.text.lower()
    tp = "invoice" if "invoice" in t else "zelle" if "zelle" in t else "debtor" if "debtor" in t else None
    if not tp:
        return await msg.answer("Use provided buttons.", reply_markup=home_keyboard())
    await state.update_data(doc_type=tp)
    await state.set_state(Flow.awaiting_ids)
    await msg.answer(f"{tp.upper()} selected. Send Carrier IDs separated by spaces.", reply_markup=back_keyboard())


async def handle_ids(msg: Message, state: FSMContext):
    if msg.text.lower().startswith("go back"):
        return await cmd_start(msg, state)

    data = await state.get_data()
    tp = data.get("doc_type")
    if not tp:
        return await cmd_start(msg, state)

    carrier_ids = [x.strip() for x in msg.text.split() if x.strip()]
    folder_id = TYPE_FOLDER_IDS[tp]
    subject, body = EMAIL_TEMPLATES[tp]

    start_time = time.perf_counter()

    status = await msg.answer("📥 Received IDs... scanning Zoho WorkDrive...")
    matches = find_pdfs_in_zoho(folder_id, carrier_ids)
    log_console(f"[SCAN] Found matches for {len(carrier_ids)} Carrier IDs in Zoho folder")

    await msg.bot.edit_message_text(chat_id=msg.chat.id, message_id=status.message_id,
                                    text="🔍 Matching PDFs found, preparing emails...")

    sent, failed, times = [], [], []
    total = len(carrier_ids)
    temp_dir = tempfile.gettempdir()

    for idx, cid in enumerate(carrier_ids, start=1):
        t0 = time.perf_counter()
        pdfs = matches.get(cid, [])
        avg_time = (sum(times) / len(times)) if times else 3
        remaining = total - (idx - 1)
        eta = remaining * avg_time
        elapsed = time.perf_counter() - start_time

        progress_text = (
            f"📤 Sending {idx}/{total} — Carrier ID: {cid}\n"
            f"🕒 Elapsed: {elapsed:.1f}s | ETA: {eta:.1f}s"
        )
        await msg.bot.edit_message_text(chat_id=msg.chat.id, message_id=status.message_id, text=progress_text)
        log_console(progress_text)

        if not pdfs:
            failed.append(f"{cid} — No PDF Found")
            log_console(f"[MISS] {cid} — No PDF Found")
            continue

        pdf_info = pdfs[0]
        file_id = pdf_info['id']
        file_name = pdf_info['name']

        # Download PDF temporarily
        temp_pdf_path = os.path.join(temp_dir, file_name)

        try:
            zoho.download_file(file_id, temp_pdf_path)
        except Exception as e:
            failed.append(f"{cid} — Download Failed: {e}")
            log_console(f"[FAIL] {cid} — Download Failed: {e}")
            continue

        email = extract_email(temp_pdf_path)
        if not email:
            failed.append(f"{cid} — Email Missing")
            log_console(f"[MISS] {cid} — Email Missing")
            if os.path.exists(temp_pdf_path):
                os.remove(temp_pdf_path)
            continue

        result = await send_email_async(email, subject, body, temp_pdf_path)
        duration = time.perf_counter() - t0
        times.append(duration)

        if result == "OK":
            sent.append(f"{cid} → {email} ({duration:.1f}s)")
            move_to_sent_zoho(file_id, file_name, tp)
            log_console(f"[SENT] {cid} to {email} in {duration:.1f}s")
        else:
            failed.append(f"{cid} — {result}")
            log_console(f"[FAIL] {cid} — {result}")

        # Clean up temp file
        if os.path.exists(temp_pdf_path):
            os.remove(temp_pdf_path)

    total_time = time.perf_counter() - start_time
    avg_time = (sum(times) / len(times)) if times else 0

    summary = [
        f"{tp.upper()} — Summary Report",
        f"Total time: {total_time:.1f}s (avg {avg_time:.1f}s/email)",
        "",
        f"✅ Sent: {len(sent)}",
    ]
    summary += sent or ["—"]
    summary += ["", f"❌ Failed: {len(failed)}"]
    summary += failed or ["—"]

    await msg.bot.edit_message_text(chat_id=msg.chat.id, message_id=status.message_id, text="\n".join(summary))
    log_console(f"[DONE] All emails processed in {total_time:.1f}s.")


# ==============================
# RUN
# ==============================
async def main():
    bot = Bot(BOT_TOKEN)
    dp = Dispatcher()
    dp.message.register(cmd_start, Command("start"))
    dp.message.register(handle_type, Flow.picking_type)
    dp.message.register(handle_ids, Flow.awaiting_ids)
    log_console("[BOT] BillingBot running with Zoho WorkDrive integration...")
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
