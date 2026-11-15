"""
=============================================================================
  TELEGRAM CHAT & ACCOUNT CLEANER - BY MNHATREALZ
  Features: Leave Groups/Supergroups, Leave Channels, Filter Admin/Owner,
            Bypass Whitelist, SpamBot Evasion Delays, Smart FloodWait Handling,
            Keyword Spam Filter, Dead Groups Cleaner, Contacts Cleaner,
            Isolated Multi-Account Profile Manager & Dual-Language (VI/EN).
=============================================================================
"""

import os
import sys
import json
import time
import asyncio
import random
import datetime
from typing import List, Dict, Set, Tuple, Optional

# Hỗ trợ hiển thị màu sắc trên Console
try:
    from colorama import init, Fore, Style
    init(autoreset=True)
    HAS_COLORAMA = True
except ImportError:
    HAS_COLORAMA = False
    class Fore:
        GREEN = RED = YELLOW = CYAN = MAGENTA = WHITE = BLUE = RESET = ""
    class Style:
        BRIGHT = DIM = RESET_ALL = ""

from telethon import TelegramClient
from telethon.tl.types import Channel, Chat, User
from telethon.tl.functions.channels import LeaveChannelRequest
from telethon.tl.functions.messages import DeleteChatUserRequest, DeleteHistoryRequest
from telethon.tl.functions.contacts import BlockRequest, GetContactsRequest, DeleteContactsRequest
from telethon.errors import (
    FloodWaitError,
    PeerFloodError,
    ChannelPrivateError,
    UserNotParticipantError,
    ChatAdminRequiredError
)

CONFIG_FILE = "config.json"
WHITELIST_FILE = "whitelist.txt"
SESSIONS_DIR = "sessions"
ACCOUNTS_FILE = os.path.join(SESSIONS_DIR, "accounts.json")
DEFAULT_SESSION_NAME = "tele_session"

# Danh sách từ khóa rác mặc định (Crypto, Casino, Kèo, 18+, Bet, Scam...)
DEFAULT_SPAM_KEYWORDS = [
    "crypto", "casino", "kèo", "18+", "bet", "tài xỉu", "gái", "sex", "lừa đảo",
    "airdrop", "baccarat", "ku", "kubet", "thabet", "bóng đá", "độ", "tín dụng",
    "vay", "hoa hồng", "đầu tư", "tiền số", "forex", "kiếm tiền", "vip", "nhóm kéo",
    "game bài", "nổ hũ", "chẵn lẻ", "momo", "xổ số", "lô đề", "shbet", "jun88", "hi88",
    "porn", "scam", "pump", "signals", "trading", "investment", "giveaway"
]

DEFAULT_CONFIG = {
    "api_id": 0,
    "api_hash": "",
    "phone": "",
    "session_name": DEFAULT_SESSION_NAME,
    "language": "vi",  # "vi" hoặc "en"
    "min_delay_seconds": 1.5,
    "max_delay_seconds": 3.0,
    "batch_size": 15,
    "batch_cooldown_seconds": 30,
    "skip_admin_or_owned": True,
    "auto_flood_wait": True
}


# =============================================================================
#   HỆ THỐNG ĐA NGÔN NGỮ (BILINGUAL I18N SYSTEM: VI & EN)
# =============================================================================

TRANSLATIONS = {
    "vi": {
        "banner_sub": "⚡ TELEGRAM CHAT & ACCOUNT CLEANER ⚡",
        "banner_author": "👑 Tác giả:",
        "banner_ver": "Phiên bản:",
        "acc_list_title": "📋 DANH SÁCH TÀI KHOẢN TRÊN MÁY NÀY:",
        "acc_new": "➕ Đăng nhập tài khoản mới (Người dùng khác)",
        "acc_del": "🗑️  Xóa bớt tài khoản khỏi máy",
        "acc_exit": "🚪 Thoát chương trình",
        "acc_prompt": "👉 Bạn muốn sử dụng tài khoản nào? (Nhập số tương ứng): ",
        "acc_del_prompt": "Nhập số thứ tự tài khoản muốn xóa khỏi máy: ",
        "acc_deleted": "[✓] Đã xóa tài khoản khỏi máy!",
        "acc_connecting": "[*] Đang kết nối tài khoản:",
        "acc_expired": "[!] Phiên đăng nhập đã hết hạn. Đang đăng nhập lại...",
        "invalid_choice": "[!] Lựa chọn không hợp lệ.",
        "login_title": "📞 [ĐĂNG NHẬP TÀI KHOẢN TELEGRAM MỚI]",
        "phone_prompt": "Nhập số điện thoại Telegram của bạn (kèm mã quốc gia, vd: +84912345678): ",
        "phone_empty": "[!] Số điện thoại không được để trống!",
        "save_prompt": "Bạn có muốn lưu tài khoản này trên máy tính để lần sau không cần đăng nhập lại?",
        "save_opt_1": "Lưu tài khoản (Máy tính cá nhân của bạn)",
        "save_opt_2": "Không lưu / Dùng tạm (Tự xóa phiên khi tắt tool, bảo vệ sự riêng tư)",
        "save_choice": "👉 Lựa chọn (1-2, mặc định 1): ",
        "client_starting": "[*] Đang khởi động Telegram Client...",
        "2fa_title": "🔐 [BẢO MẬT 2 LỚP - 2FA TELEGRAM]",
        "2fa_desc": "Tài khoản của bạn đã kích hoạt Xác thực 2 bước (Two-Step Verification).",
        "2fa_visible": "👉 Ký tự sẽ hiển thị rõ ràng bên dưới để bạn kiểm tra, không sợ gõ nhầm:",
        "2fa_prompt": "Nhập mật khẩu 2FA của bạn rồi bấm Enter: ",
        "acc_saved": "[✓] Đã lưu thông tin tài khoản:",
        "guest_notice": "[i] Chế độ Khách (Dùng tạm): Phiên đăng nhập sẽ tự động xóa khi bạn thoát tool.",
        "logged_in_as": "👤 Đang đăng nhập:",
        "guest_tag": "[Dùng tạm - Không lưu]",
        "whitelist_status": "🛡️  Whitelist bảo vệ: {count} mục (trong file {file})",
        "menu_header": "VUI LÒNG CHỌN CHỨC NĂNG:",
        "menu_1": "🔴 Chỉ rời NHÓM (Groups & Supergroups) - Giữ Kênh & Chat cá nhân",
        "menu_2": "📢 Chỉ rời KÊNH (Broadcast Channels) - Giữ Nhóm & Chat cá nhân",
        "menu_3": "⚡ Rời CẢ NHÓM VÀ KÊNH - Giữ Chat cá nhân",
        "menu_4": "💬 XÓA TRÒ CHUYỆN (Xóa tin nhắn riêng 1-1 & Chặn xóa Bot)",
        "menu_5": "💣 DỌN SẠCH TẤT CẢ (Rời Nhóm + Kênh + Xóa Trò Chuyện & Bot - DỌN TRẮNG NICK)",
        "menu_6": "🔍 RỜI NHÓM THEO TỪ KHÓA RÁC (Keyword Filter: crypto, casino, kèo, 18+...)",
        "menu_7": "💤 RỜI NHÓM 'CHẾT' (Không hoạt động > 30, 60, 90 ngày)",
        "menu_8": "📇 DỌN SẠCH DANH BẠ RÁC (Xóa danh bạ đồng bộ & Nick Deleted Account)",
        "menu_9": "👁️  Quét kiểm tra (Dry-Run: Xem danh sách, KHÔNG rời/xóa)",
        "menu_l": "🌐 ĐỔI NGÔN NGỮ / CHANGE LANGUAGE (Tiếng Việt / English)",
        "menu_s": "⚙️  Cài đặt thông số Delay, Cooldown & API",
        "menu_a": "🔄 ĐỔI TÀI KHOẢN KHÁC (Quay lại danh sách chọn nick)",
        "menu_x": "🗑️  ĐĂNG XUẤT NICK NÀY (Xóa tài khoản này khỏi máy)",
        "menu_0": "🚪 Thoát chương trình",
        "prompt_choice": "👉 Nhập lựa chọn của bạn: ",
        "thank_you": "[✓] Cảm ơn bạn đã sử dụng tool của mnhatrealz. Tạm biệt!",
        "logout_confirm": "⚠️  Bạn có chắc chắn muốn đăng xuất và xóa tài khoản {name} khỏi máy? (y/N): ",
        "logout_success": "[✓] Đã xóa tài khoản khỏi máy thành công!",
        "press_enter": "[Nhấn Enter để quay lại Menu...]",
        "press_enter_cont": "[Nhấn Enter để tiếp tục...]",
        "dry_run_which": "Bạn muốn quét kiểm tra loại nào?",
        "dry_run_opts": " [1] Nhóm | [2] Kênh | [3] Cả Nhóm & Kênh | [4] Trò chuyện cá nhân | [5] Tất cả | [6] Từ khóa | [7] Nhóm chết",
        "chat_filter_title": "Chọn loại trò chuyện muốn xóa:",
        "chat_filter_1": "🤖+💬 Xóa TẤT CẢ (Cả Bot rác & Tin nhắn người thật - Khuyên dùng)",
        "chat_filter_2": "🤖 Chỉ xóa BOT (Chặn vĩnh viễn & Xóa sạch toàn bộ bot rác)",
        "chat_filter_3": "👤 Chỉ xóa Người thật (Giữ lại Bot)",
        "kw_title": "=== CẤU HÌNH TỪ KHÓA RÁC ĐỂ RỜI NHÓM/KÊNH ===",
        "kw_opt_1": "Dùng danh sách từ khóa rác mặc định ({count} từ khóa: crypto, bet, casino, tài xỉu, 18+...)",
        "kw_opt_2": "Tự nhập từ khóa của riêng bạn (cách nhau bằng dấu phẩy)",
        "kw_prompt": "Nhập các từ khóa muốn lọc (vd: coin, kèo, gái, tài xỉu): ",
        "kw_active": "[✓] Đang áp dụng {count} từ khóa lọc rác.",
        "inact_title": "=== CHỌN THỜI GIAN NHÓM KHÔNG HOẠT ĐỘNG (NHÓM CHẾT) ===",
        "inact_opt_1": "Không có tin nhắn trên 30 ngày (1 tháng)",
        "inact_opt_2": "Không có tin nhắn trên 60 ngày (2 tháng - Khuyên dùng)",
        "inact_opt_3": "Không có tin nhắn trên 90 ngày (3 tháng)",
        "inact_opt_4": "Không có tin nhắn trên 180 ngày (6 tháng)",
        "inact_opt_5": "Tự nhập số ngày tùy ý",
        "inact_prompt": "Nhập số ngày không hoạt động: ",
        "inact_active": "[✓] Tiêu chuẩn nhóm chết: Không hoạt động trên {days} ngày.",
        "scan_scope_title": "Chọn số lượng hội thoại muốn xử lý:",
        "scan_scope_1": "⚡ Quét 1.000 mục gần nhất",
        "scan_scope_2": "🚀 Quét 2.000 mục gần nhất",
        "scan_scope_3": "🔥 Quét 5.000 mục gần nhất",
        "scan_scope_4": "🌐 Quét TOÀN BỘ tài khoản (Không giới hạn - Bấm Enter)",
        "scan_scope_custom": "(Hoặc bạn có thể gõ trực tiếp số lượng tùy thích, ví dụ: 1500, 3000...)",
        "scan_scope_prompt": "👉 Nhập lựa chọn (1-4) hoặc gõ số lượng (mặc định Toàn bộ): ",
        "scan_result_title": "================ KẾT QUẢ QUÉT ================",
        "scan_res_scanned": "📊 Tổng số hội thoại đã quét :",
        "scan_res_matched": "🎯 Số mục thỏa mãn điều kiện :",
        "scan_res_skipped_adm": "👑 Bỏ qua do bạn là Admin/Chủ sở hữu:",
        "scan_res_skipped_wl": "🛡️  Bỏ qua do nằm trong Whitelist   :",
        "scan_res_adm_list": "[i] Danh sách nhóm Admin/Owner được tự động bảo vệ:",
        "dry_run_list_title": "Danh sách dự kiến sẽ xử lý (rời/xóa):",
        "no_targets": "[!] Không tìm thấy mục nào cần xử lý theo yêu cầu.",
        "warn_nuke": "💣 CẢNH BÁO NGUY HIỂM: Bạn đang chọn DỌN SẠCH TẤT CẢ (Rời nhóm, kênh VÀ chặn + xóa toàn bộ trò chuyện & Bot)!",
        "warn_chat": "💬 XÁC NHẬN: Bạn sắp XÓA SẠCH {count} {desc}!",
        "warn_kw": "🔍 XÁC NHẬN: Bạn sắp rời {count} nhóm/kênh chứa TỪ KHÓA RÁC!",
        "warn_inact": "💤 XÁC NHẬN: Bạn sắp rời {count} NHÓM CHẾT (không hoạt động > {days} ngày)!",
        "warn_leave": "⚠️  XÁC NHẬN: Bạn sắp rời {count} nhóm/kênh!",
        "confirm_prompt": "Nhập '{yes}' hoặc 'y' để bắt đầu: ",
        "op_cancelled": "[!] Đã hủy thao tác.",
        "exec_title": "=== BẮT ĐẦU XỬ LÝ (Tổng: {count} mục) ===",
        "exec_params": "⚙️  Thông số an toàn: Delay ngẫu nhiên {min_d}s - {max_d}s | Nghỉ {cooldown}s sau mỗi {batch} mục",
        "del_success": "[XÓA THÀNH CÔNG]",
        "leave_success": "[RỜI THÀNH CÔNG]",
        "blocked_and_deleted": " (Đã chặn & xóa)",
        "flood_warn": "[CẢNH BÁO FLOODWAIT] Telegram yêu cầu chờ {sec} giây để tránh quét SpamBot!",
        "peer_flood_warn": "[CẢNH BÁO NGUY HIỂM - PEER_FLOOD] Tài khoản đã bị Telegram gắn cờ gửi lệnh quá nhanh. ĐÃ DỪNG TOOL NGAY LẬP TỨC ĐỂ BẢO VỆ NICK!",
        "peer_flood_advice": "👉 Vui lòng để tài khoản nghỉ ngơi từ 2-6 tiếng trước khi tiếp tục.",
        "skip_label": "[BỎ QUA]",
        "err_label": "[LỖI]",
        "cooldown_notice": "🛡️  [GIẢM NHIỆT AN TOÀN] Đã xử lý {cur}/{total} mục.",
        "cooldown_reason": "Nghỉ hạ nhiệt sau đợt {batch} mục",
        "exec_done": "🎉 HOÀN THÀNH QUÁ TRÌNH XỬ LÝ",
        "exec_success_stat": "✅ Thành công    :",
        "exec_error_stat": "⚠️  Lỗi / Bỏ qua  :",
        "exec_time_stat": "⏱️  Thời gian chạy: {sec} giây",
        "contacts_title": "📇 [DỌN SẠCH DANH BẠ TELEGRAM - CONTACTS CLEANER]",
        "contacts_loading": "[*] Đang tải danh sách liên hệ từ máy chủ Telegram...",
        "contacts_err": "[X] Lỗi khi lấy danh bạ:",
        "contacts_res_title": "📊 KẾT QUẢ QUÉT DANH BẠ:",
        "contacts_total": " • Tổng số liên hệ trong danh bạ :",
        "contacts_active": " • Tài khoản bình thường          :",
        "contacts_deleted_acc": " • Nick đã bị xóa (Deleted Account):",
        "contacts_empty": "[✓] Danh bạ của bạn hoàn toàn trống. Không có gì cần xóa!",
        "contacts_opt_title": "Chọn chế độ dọn danh bạ:",
        "contacts_opt_1": "👻 Chỉ xóa nick 'Deleted Account' (Giữ lại bạn bè bình thường)",
        "contacts_opt_2": "💣 Xóa TẤT CẢ DANH BẠ ({count} liên hệ - Xóa trắng danh bạ đồng bộ)",
        "contacts_opt_0": "🚪 Quay lại Menu chính",
        "contacts_no_del": "[✓] Không có nick 'Deleted Account' nào trong danh bạ.",
        "contacts_confirm": "⚠️  XÁC NHẬN: Bạn sắp {desc}!",
        "contacts_cleaning": "[*] Đang tiến hành xóa {count} liên hệ...",
        "contacts_batch_done": "[✓] Đã xóa đợt: {cur}/{total} liên hệ...",
        "contacts_done": "🎉 [HOÀN THÀNH] Đã xóa thành công {count} liên hệ trong {sec} giây!",
        "settings_title": "=== CÀI ĐẶT THÔNG SỐ VẬN HÀNH & NÉ QUÉT ===",
        "settings_1": "Delay ngẫu nhiên tối thiểu  :",
        "settings_2": "Delay ngẫu nhiên tối đa     :",
        "settings_3": "Kích thước đợt (Batch size) :",
        "settings_4": "Thời gian nghỉ mỗi đợt      :",
        "settings_5": "Bỏ qua nhóm là Admin/Owner  :",
        "settings_6": "Tự động chờ khi FloodWait   :",
        "settings_7": "Đổi API ID / API HASH",
        "settings_0": "Quay lại Menu chính",
        "lang_switch_title": "🌐 CHỌN NGÔN NGỮ / SELECT LANGUAGE:",
        "lang_changed": "[✓] Đã đổi ngôn ngữ sang Tiếng Việt!"
    },
    "en": {
        "banner_sub": "⚡ TELEGRAM CHAT & ACCOUNT CLEANER ⚡",
        "banner_author": "👑 Author:",
        "banner_ver": "Version:",
        "acc_list_title": "📋 SAVED ACCOUNTS ON THIS PC:",
        "acc_new": "➕ Log in new account (Another user)",
        "acc_del": "🗑️  Remove account from this PC",
        "acc_exit": "🚪 Exit Program",
        "acc_prompt": "👉 Which account do you want to use? (Enter corresponding number): ",
        "acc_del_prompt": "Enter the number of account to remove from PC: ",
        "acc_deleted": "[✓] Account removed from this PC!",
        "acc_connecting": "[*] Connecting account:",
        "acc_expired": "[!] Login session expired. Logging in again...",
        "invalid_choice": "[!] Invalid choice.",
        "login_title": "📞 [LOG IN TO TELEGRAM ACCOUNT]",
        "phone_prompt": "Enter your Telegram phone number with country code (e.g. +1234567890): ",
        "phone_empty": "[!] Phone number cannot be empty!",
        "save_prompt": "Do you want to save this account on this PC for quick future access?",
        "save_opt_1": "Save account (Your personal PC)",
        "save_opt_2": "Guest / Temporary mode (Auto-deletes session on exit, maximum privacy)",
        "save_choice": "👉 Choice (1-2, default 1): ",
        "client_starting": "[*] Starting Telegram Client...",
        "2fa_title": "🔐 [TWO-STEP VERIFICATION - 2FA]",
        "2fa_desc": "Your account has Two-Step Verification (2FA) enabled.",
        "2fa_visible": "👉 Characters will be displayed clearly below so you can check before submitting:",
        "2fa_prompt": "Enter your 2FA password and press Enter: ",
        "acc_saved": "[✓] Saved account profile:",
        "guest_notice": "[i] Guest Mode: Login session will be automatically deleted when exiting.",
        "logged_in_as": "👤 Logged in as:",
        "guest_tag": "[Guest / Temporary]",
        "whitelist_status": "🛡️  Whitelist protected: {count} items (in file {file})",
        "menu_header": "PLEASE SELECT AN OPTION:",
        "menu_1": "🔴 Leave GROUPS only (Groups & Supergroups) - Keep Channels & DMs",
        "menu_2": "📢 Leave CHANNELS only (Broadcast Channels) - Keep Groups & DMs",
        "menu_3": "⚡ Leave BOTH Groups & Channels - Keep Direct Messages",
        "menu_4": "💬 DELETE DIRECT CHATS (1-1 Messages & Block + Wipe Bots)",
        "menu_5": "💣 NUKE EVERYTHING (Leave Groups + Channels + Wipe Chats & Bots - CLEAN SLATE)",
        "menu_6": "🔍 LEAVE GROUPS BY SPAM KEYWORDS (Keyword Filter: crypto, casino, bet, 18+...)",
        "menu_7": "💤 LEAVE DEAD / INACTIVE GROUPS (No activity > 30, 60, 90 days)",
        "menu_8": "📇 CONTACTS CLEANER (Bulk wipe synced contacts & Deleted Accounts)",
        "menu_9": "👁️  Dry-Run Scan (Preview list, do NOT leave/delete)",
        "menu_l": "🌐 CHANGE LANGUAGE / ĐỔI NGÔN NGỮ (English / Tiếng Việt)",
        "menu_s": "⚙️  Safety Settings (Delay, Cooldown & API)",
        "menu_a": "🔄 SWITCH ACCOUNT (Return to account list)",
        "menu_x": "🗑️  LOG OUT CURRENT ACCOUNT (Remove session from this PC)",
        "menu_0": "🚪 Exit Program",
        "prompt_choice": "👉 Enter your choice: ",
        "thank_you": "[✓] Thank you for using mnhatrealz's tool. Goodbye!",
        "logout_confirm": "⚠️  Are you sure you want to log out and remove {name} from this PC? (y/N): ",
        "logout_success": "[✓] Account successfully removed from this PC!",
        "press_enter": "[Press Enter to return to Menu...]",
        "press_enter_cont": "[Press Enter to continue...]",
        "dry_run_which": "Which category do you want to dry-run inspect?",
        "dry_run_opts": " [1] Groups | [2] Channels | [3] Groups & Channels | [4] DMs & Bots | [5] All | [6] Keywords | [7] Dead Groups",
        "chat_filter_title": "Select chat type to delete:",
        "chat_filter_1": "🤖+💬 Delete ALL (Both Spam Bots & Real Users - Recommended)",
        "chat_filter_2": "🤖 Delete BOTS only (Permanently Block & Wipe all bots)",
        "chat_filter_3": "👤 Delete Real Users only (Keep Bots)",
        "kw_title": "=== CONFIGURE SPAM KEYWORDS FOR LEAVING GROUPS ===",
        "kw_opt_1": "Use default spam keywords list ({count} popular keywords: crypto, bet, casino, 18+...)",
        "kw_opt_2": "Enter your own custom keywords (comma-separated)",
        "kw_prompt": "Enter keywords to filter (e.g. coin, airdrop, bet, porn): ",
        "kw_active": "[✓] Applying {count} spam filter keywords.",
        "inact_title": "=== SELECT INACTIVE DURATION THRESHOLD (DEAD GROUPS) ===",
        "inact_opt_1": "No messages for over 30 days (1 month)",
        "inact_opt_2": "No messages for over 60 days (2 months - Recommended)",
        "inact_opt_3": "No messages for over 90 days (3 months)",
        "inact_opt_4": "No messages for over 180 days (6 months)",
        "inact_opt_5": "Custom number of days",
        "inact_prompt": "Enter number of inactive days: ",
        "inact_active": "[✓] Dead group threshold: Inactive for more than {days} days.",
        "scan_scope_title": "Select scan limit:",
        "scan_scope_1": "⚡ Scan latest 1,000 items",
        "scan_scope_2": "🚀 Scan latest 2,000 items",
        "scan_scope_3": "🔥 Scan latest 5,000 items",
        "scan_scope_4": "🌐 Scan ENTIRE account (Unlimited - Press Enter)",
        "scan_scope_custom": "(Or directly type any custom number, e.g. 1500, 3000...)",
        "scan_scope_prompt": "👉 Enter choice (1-4) or custom number (default: Entire account): ",
        "scan_result_title": "================ SCAN RESULTS ================",
        "scan_res_scanned": "📊 Total dialogs scanned :",
        "scan_res_matched": "🎯 Matching targets found:",
        "scan_res_skipped_adm": "👑 Skipped (You are Admin/Owner):",
        "scan_res_skipped_wl": "🛡️  Skipped (In Whitelist)      :",
        "scan_res_adm_list": "[i] Admin/Owner groups automatically protected:",
        "dry_run_list_title": "List of targets scheduled for processing (leave/delete):",
        "no_targets": "[!] No targets found matching your criteria.",
        "warn_nuke": "💣 CRITICAL WARNING: You selected NUKE EVERYTHING (Leave groups, channels AND permanently block + wipe all chats & bots)!",
        "warn_chat": "💬 CONFIRMATION: You are about to DELETE {count} {desc}!",
        "warn_kw": "🔍 CONFIRMATION: You are about to leave {count} groups/channels matching SPAM KEYWORDS!",
        "warn_inact": "💤 CONFIRMATION: You are about to leave {count} DEAD GROUPS (inactive > {days} days)!",
        "warn_leave": "⚠️  CONFIRMATION: You are about to leave {count} groups/channels!",
        "confirm_prompt": "Type '{yes}' or 'y' to proceed: ",
        "op_cancelled": "[!] Operation cancelled.",
        "exec_title": "=== STARTING EXECUTION (Total: {count} items) ===",
        "exec_params": "⚙️  Safety parameters: Jitter delay {min_d}s - {max_d}s | Cooldown {cooldown}s every {batch} items",
        "del_success": "[DELETE SUCCESS]",
        "leave_success": "[LEAVE SUCCESS]",
        "blocked_and_deleted": " (Blocked & Wiped)",
        "flood_warn": "[FLOODWAIT WARNING] Telegram requests a wait of {sec} seconds to avoid SpamBot restrictions!",
        "peer_flood_warn": "[CRITICAL WARNING - PEER_FLOOD] Account flagged for sending requests too fast. TOOL STOPPED IMMEDIATELY TO PROTECT YOUR ACCOUNT!",
        "peer_flood_advice": "👉 Please let your account rest for 2-6 hours before resuming.",
        "skip_label": "[SKIPPED]",
        "err_label": "[ERROR]",
        "cooldown_notice": "🛡️  [SAFETY COOLDOWN] Processed {cur}/{total} items.",
        "cooldown_reason": "Cooldown sleep after {batch} items batch",
        "exec_done": "🎉 PROCESS COMPLETED SUCCESSFULLY",
        "exec_success_stat": "✅ Successful    :",
        "exec_error_stat": "⚠️  Errors/Skipped:",
        "exec_time_stat": "⏱️  Elapsed time : {sec} seconds",
        "contacts_title": "📇 [TELEGRAM CONTACTS CLEANER]",
        "contacts_loading": "[*] Fetching contacts from Telegram servers...",
        "contacts_err": "[X] Error fetching contacts:",
        "contacts_res_title": "📊 CONTACTS SCAN RESULTS:",
        "contacts_total": " • Total contacts in address book :",
        "contacts_active": " • Active accounts               :",
        "contacts_deleted_acc": " • Deleted accounts (Ghost/Spam) :",
        "contacts_empty": "[✓] Your Telegram contacts list is completely empty!",
        "contacts_opt_title": "Select contacts cleanup mode:",
        "contacts_opt_1": "👻 Delete 'Deleted Account' contacts only (Keep normal friends)",
        "contacts_opt_2": "💣 WIPE ENTIRE CONTACTS LIST ({count} contacts - Clean address book)",
        "contacts_opt_0": "🚪 Return to Main Menu",
        "contacts_no_del": "[✓] No 'Deleted Account' contacts found in address book.",
        "contacts_confirm": "⚠️  CONFIRMATION: You are about to {desc}!",
        "contacts_cleaning": "[*] Deleting {count} contacts...",
        "contacts_batch_done": "[✓] Deleted batch: {cur}/{total} contacts...",
        "contacts_done": "🎉 [COMPLETED] Successfully deleted {count} contacts in {sec} seconds!",
        "settings_title": "=== SAFETY & PERFORMANCE SETTINGS ===",
        "settings_1": "Minimum random delay        :",
        "settings_2": "Maximum random delay        :",
        "settings_3": "Batch size (items per run)  :",
        "settings_4": "Cooldown duration per batch :",
        "settings_5": "Skip Admin / Owned groups   :",
        "settings_6": "Auto-wait on FloodWait      :",
        "settings_7": "Reset API ID / API HASH",
        "settings_0": "Return to Main Menu",
        "lang_switch_title": "🌐 SELECT LANGUAGE / CHỌN NGÔN NGỮ:",
        "lang_changed": "[✓] Language switched to English!"
    }
}


def t(key: str, lang: str = "vi", **kwargs) -> str:
    """Truy xuất chuỗi dịch theo ngôn ngữ hiện tại"""
    lang_dict = TRANSLATIONS.get(lang, TRANSLATIONS["vi"])
    template = lang_dict.get(key, TRANSLATIONS["vi"].get(key, key))
    if kwargs:
        try:
            return template.format(**kwargs)
        except Exception:
            return template
    return template


def clear_screen():
    os.system("cls" if os.name == "nt" else "clear")


def print_banner(lang: str = "vi"):
    banner = f"""{Fore.CYAN}{Style.BRIGHT}
  ███╗   ███╗███╗   ██╗██╗  ██╗ █████╗ ████████╗██████╗ ███████╗ █████╗ ██╗     ███████╗
  ████╗ ████║████╗  ██║██║  ██║██╔══██╗╚══██╔══╝██╔══██╗██╔════╝██╔══██╗██║     ╚══███╔╝
  ██╔████╔██║██╔██╗ ██║███████║███████║   ██║   ██████╔╝█████╗  ███████║██║       ███╔╝ 
  ██║╚██╔╝██║██║╚██╗██║██╔══██║██╔══██║   ██║   ██╔══██╗██╔══╝  ██╔══██║██║      ███╔╝  
  ██║ ╚═╝ ██║██║ ╚████║██║  ██║██║  ██║   ██║   ██║  ██║███████╗██║  ██║███████╗███████╗
  ╚═╝     ╚═╝╚═╝  ╚═══╝╚═╝  ╚═╝╚═╝  ╚═╝   ╚═╝   ╚═╝  ╚═╝╚══════╝╚═╝  ╚═╝╚══════╝╚══════╝
{Fore.YELLOW}             {t('banner_sub', lang)}{Style.RESET_ALL}
{Fore.MAGENTA}             {t('banner_author', lang)} {Fore.WHITE}{Style.BRIGHT}mnhatrealz{Style.RESET_ALL}{Fore.MAGENTA} | {t('banner_ver', lang)} {Fore.GREEN}v2.5 PRO MAX{Style.RESET_ALL}
{Fore.BLUE}  ================================================================================={Style.RESET_ALL}"""
    print(banner)


def ensure_sessions_dir():
    if not os.path.exists(SESSIONS_DIR):
        os.makedirs(SESSIONS_DIR, exist_ok=True)


def load_config() -> dict:
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
                config = DEFAULT_CONFIG.copy()
                config.update(data)
                return config
        except Exception as e:
            print(f"{Fore.YELLOW}[!] Lỗi đọc {CONFIG_FILE}: {e}. Dùng cấu hình mặc định.{Style.RESET_ALL}")
    return DEFAULT_CONFIG.copy()


def save_config(config: dict):
    try:
        with open(CONFIG_FILE, "w", encoding="utf-8") as f:
            json.dump(config, f, indent=4, ensure_ascii=False)
        print(f"{Fore.GREEN}[✓] Saved configuration to {CONFIG_FILE}{Style.RESET_ALL}")
    except Exception as e:
        print(f"{Fore.RED}[X] Error saving configuration: {e}{Style.RESET_ALL}")


def load_whitelist() -> Set[str]:
    """Tải danh sách trắng các ID hoặc username không được rời"""
    whitelist = set()
    if not os.path.exists(WHITELIST_FILE):
        with open(WHITELIST_FILE, "w", encoding="utf-8") as f:
            f.write("# Whitelist: Telegram Groups/Channels that will NEVER be left\n")
            f.write("# Enter Chat ID (e.g. -1001234567890) or @username (e.g. @mygroup), one per line:\n")
        return whitelist

    with open(WHITELIST_FILE, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#"):
                clean_item = line.lower().lstrip("@")
                whitelist.add(clean_item)
                whitelist.add(line.lower())
    return whitelist


def is_in_whitelist(dialog, whitelist: Set[str]) -> bool:
    """Kiểm tra hội thoại có nằm trong whitelist không"""
    if not whitelist:
        return False

    chat_id_str = str(dialog.id)
    if chat_id_str in whitelist:
        return True

    entity = dialog.entity
    entity_id_str = str(getattr(entity, "id", ""))
    if entity_id_str in whitelist:
        return True

    username = getattr(entity, "username", None)
    if username:
        username_clean = username.lower().lstrip("@")
        if username_clean in whitelist or f"@{username_clean}" in whitelist:
            return True

    return False


def is_user_admin_or_owner(entity) -> Tuple[bool, str]:
    """Kiểm tra xem tài khoản hiện tại có phải chủ sở hữu hoặc quản trị viên không"""
    if getattr(entity, "creator", False):
        return True, "Owner"
    if getattr(entity, "admin_rights", None) is not None:
        return True, "Admin"
    return False, ""


async def countdown_sleep(seconds: float, reason: str = "Safe Delay"):
    """Đếm ngược thời gian nghỉ để người dùng biết tool không bị treo"""
    sec = int(seconds)
    remain_float = seconds - sec
    for s in range(sec, 0, -1):
        print(f"\r{Fore.YELLOW}⏳ [{reason}] Waiting: {s}s...{Style.RESET_ALL}   ", end="", flush=True)
        await asyncio.sleep(1)
    if remain_float > 0:
        await asyncio.sleep(remain_float)
    print("\r" + " " * 60 + "\r", end="", flush=True)


async def setup_credentials() -> dict:
    """Hỏi và thiết lập API ID & API HASH nếu chưa có"""
    config = load_config()

    if not config.get("api_id") or not config.get("api_hash"):
        print(f"{Fore.YELLOW}=== TELEGRAM API CREDENTIALS REQUIRED ==={Style.RESET_ALL}")
        print("To use MTProto Telethon at blazing speeds, you need an API ID & API HASH from Telegram.")
        print(f"👉 Please visit: {Fore.CYAN}https://my.telegram.org{Style.RESET_ALL}")
        print("1. Log in with your phone number.")
        print("2. Navigate to 'API development tools'.")
        print("3. Enter any app title to receive your App api_id and App api_hash.\n")

        while True:
            api_id_input = input("Enter API ID (digits): ").strip()
            if api_id_input.isdigit():
                config["api_id"] = int(api_id_input)
                break
            print(f"{Fore.RED}[!] API ID must be numbers only. Please try again!{Style.RESET_ALL}")

        while True:
            api_hash_input = input("Enter API HASH (32 character hex string): ").strip()
            if len(api_hash_input) >= 10:
                config["api_hash"] = api_hash_input
                break
            print(f"{Fore.RED}[!] Invalid API HASH. Please try again!{Style.RESET_ALL}")

        save_config(config)
        print(f"{Fore.GREEN}[✓] API credentials saved successfully!{Style.RESET_ALL}\n")

    return config


# =============================================================================
#   QUẢN LÝ ĐA TÀI KHOẢN (MULTI-ACCOUNT PROFILE MANAGER)
# =============================================================================

def load_accounts() -> List[dict]:
    """Tải danh sách các tài khoản Telegram đã lưu trên máy"""
    ensure_sessions_dir()
    if os.path.exists(ACCOUNTS_FILE):
        try:
            with open(ACCOUNTS_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
                valid = []
                for acc in data:
                    sess_path = acc.get("session_path", "")
                    if os.path.exists(f"{sess_path}.session"):
                        valid.append(acc)
                return valid
        except Exception:
            return []
    return []


def save_accounts(accounts: List[dict]):
    """Lưu danh sách tài khoản Telegram vào file quản lý riêng"""
    ensure_sessions_dir()
    try:
        with open(ACCOUNTS_FILE, "w", encoding="utf-8") as f:
            json.dump(accounts, f, indent=4, ensure_ascii=False)
    except Exception as e:
        print(f"{Fore.RED}[!] Error saving accounts: {e}{Style.RESET_ALL}")


def add_or_update_account(phone: str, name: str, username: str, session_path: str):
    """Cập nhật thông tin tài khoản vào danh sách"""
    accounts = load_accounts()
    for acc in accounts:
        if acc.get("phone") == phone or acc.get("session_path") == session_path:
            acc["phone"] = phone
            acc["name"] = name
            acc["username"] = username
            acc["session_path"] = session_path
            save_accounts(accounts)
            return
    accounts.append({
        "phone": phone,
        "name": name,
        "username": username,
        "session_path": session_path
    })
    save_accounts(accounts)


def delete_account_session(session_path: str, phone: str = ""):
    """Xóa triệt để file session và gỡ tài khoản khỏi máy"""
    for ext in [".session", ".session-journal"]:
        fpath = f"{session_path}{ext}"
        if os.path.exists(fpath):
            try:
                os.remove(fpath)
            except Exception:
                pass
    accounts = load_accounts()
    accounts = [acc for acc in accounts if acc.get("session_path") != session_path and acc.get("phone") != phone]
    save_accounts(accounts)


async def select_or_login_account(api_id: int, api_hash: str, config: dict):
    """
    Quản lý danh sách tài khoản:
    Hỗ trợ chuyển đổi đa tài khoản độc lập, chế độ khách dùng tạm và xóa phiên.
    """
    lang = config.get("language", "vi")
    while True:
        clear_screen()
        print_banner(lang)
        accounts = load_accounts()

        if accounts:
            print(f"{Fore.WHITE}{Style.BRIGHT}{t('acc_list_title', lang)}{Style.RESET_ALL}\n")
            for idx, acc in enumerate(accounts, 1):
                name = acc.get("name", "Telegram User")
                phone = acc.get("phone", "N/A")
                username = acc.get("username", "")
                user_desc = f" ({username})" if username and username not in ["Không có", "None"] else ""
                print(f"  [{Fore.CYAN}{idx}{Style.RESET_ALL}] 👤 {Fore.GREEN}{name}{Style.RESET_ALL} | {phone}{user_desc}")
            print("  " + "-" * 55)
            print(f"  [{Fore.CYAN}0{Style.RESET_ALL}] {t('acc_new', lang)}")
            print(f"  [{Fore.CYAN}L{Style.RESET_ALL}] {Fore.MAGENTA}{t('menu_l', lang)}{Style.RESET_ALL}")
            print(f"  [{Fore.CYAN}D{Style.RESET_ALL}] {t('acc_del', lang)}")
            print(f"  [{Fore.CYAN}Q{Style.RESET_ALL}] {t('acc_exit', lang)}\n")

            choice = input(t("acc_prompt", lang)).strip().lower()

            if choice == "q":
                return None, None, None, False, lang

            elif choice == "l":
                lang = switch_language_menu(config, lang)
                continue

            elif choice == "d":
                del_idx = input(t("acc_del_prompt", lang)).strip()
                if del_idx.isdigit() and 1 <= int(del_idx) <= len(accounts):
                    acc_to_del = accounts[int(del_idx) - 1]
                    delete_account_session(acc_to_del["session_path"], acc_to_del.get("phone", ""))
                    print(f"{Fore.GREEN}{t('acc_deleted', lang)}{Style.RESET_ALL}")
                    time.sleep(1.5)
                continue

            elif choice == "0":
                client, me, sess_path, is_guest = await login_new_account(api_id, api_hash, lang)
                return client, me, sess_path, is_guest, lang

            elif choice.isdigit() and 1 <= int(choice) <= len(accounts):
                sel_acc = accounts[int(choice) - 1]
                sess_path = sel_acc["session_path"]
                phone = sel_acc.get("phone", "")

                print(f"\n{Fore.CYAN}{t('acc_connecting', lang)} {sel_acc.get('name')} ({phone})...{Style.RESET_ALL}")
                client = TelegramClient(sess_path, api_id, api_hash)
                await client.connect()
                if await client.is_user_authorized():
                    me = await client.get_me()
                    return client, me, sess_path, False, lang
                else:
                    print(f"{Fore.YELLOW}{t('acc_expired', lang)}{Style.RESET_ALL}")
                    client, me, sess_path, is_guest = await login_with_phone(api_id, api_hash, phone, sess_path, is_guest=False, lang=lang)
                    return client, me, sess_path, is_guest, lang
            else:
                print(f"{Fore.RED}{t('invalid_choice', lang)}{Style.RESET_ALL}")
                time.sleep(1)
        else:
            print(f"{Fore.WHITE}{Style.BRIGHT}{t('acc_list_title', lang)}{Style.RESET_ALL}\n")
            no_acc_text = "(Chưa có tài khoản nào được lưu trên máy này)" if lang == "vi" else "(No saved accounts on this PC)"
            print(f"  {Fore.YELLOW}{no_acc_text}{Style.RESET_ALL}\n")
            print("  " + "-" * 55)
            print(f"  [{Fore.CYAN}1{Style.RESET_ALL}] ➕ {t('acc_new', lang)}")
            print(f"  [{Fore.CYAN}L{Style.RESET_ALL}] {Fore.MAGENTA}{t('menu_l', lang)}{Style.RESET_ALL}")
            print(f"  [{Fore.CYAN}Q{Style.RESET_ALL}] {t('acc_exit', lang)}\n")

            choice = input(t("acc_prompt", lang)).strip().lower()

            if choice == "q":
                return None, None, None, False, lang
            elif choice == "l":
                lang = switch_language_menu(config, lang)
                continue
            elif choice in ["1", "0", ""]:
                client, me, sess_path, is_guest = await login_new_account(api_id, api_hash, lang)
                return client, me, sess_path, is_guest, lang
            else:
                print(f"{Fore.RED}{t('invalid_choice', lang)}{Style.RESET_ALL}")
                time.sleep(1)


async def login_new_account(api_id: int, api_hash: str, lang: str = "vi"):
    """Đăng nhập tài khoản mới và hỏi người dùng có muốn lưu trên máy không"""
    print(f"\n{Fore.YELLOW}{Style.BRIGHT}{t('login_title', lang)}{Style.RESET_ALL}")
    while True:
        phone = input(t("phone_prompt", lang)).strip()
        if phone:
            break
        print(f"{Fore.RED}{t('phone_empty', lang)}{Style.RESET_ALL}")

    phone_digits = "".join(filter(str.isdigit, phone))
    session_path = os.path.join(SESSIONS_DIR, f"session_{phone_digits}")

    print(f"\n{Fore.WHITE}{t('save_prompt', lang)}{Style.RESET_ALL}")
    print(f" [{Fore.CYAN}1{Style.RESET_ALL}] {Fore.GREEN}{t('save_opt_1', lang)}{Style.RESET_ALL}")
    print(f" [{Fore.CYAN}2{Style.RESET_ALL}] {Fore.YELLOW}{t('save_opt_2', lang)}{Style.RESET_ALL}")
    save_opt = input(t("save_choice", lang)).strip()
    is_guest = (save_opt == "2")

    return await login_with_phone(api_id, api_hash, phone, session_path, is_guest=is_guest, lang=lang)


async def login_with_phone(api_id: int, api_hash: str, phone: str, session_path: str, is_guest: bool = False, lang: str = "vi"):
    print(f"\n{Fore.CYAN}{t('client_starting', lang)}{Style.RESET_ALL}")
    client = TelegramClient(session_path, api_id, api_hash)

    def prompt_password():
        print(f"\n{Fore.YELLOW}{t('2fa_title', lang)}{Style.RESET_ALL}")
        print(t("2fa_desc", lang))
        print(f"{Fore.GREEN}{t('2fa_visible', lang)}{Style.RESET_ALL}")
        return input(f"{Fore.CYAN}{t('2fa_prompt', lang)}{Style.RESET_ALL}").strip()

    await client.start(phone=phone, password=prompt_password)
    me = await client.get_me()

    first_name = getattr(me, "first_name", "") or ""
    last_name = getattr(me, "last_name", "") or ""
    full_name = f"{first_name} {last_name}".strip() or "Telegram User"
    username = f"@{me.username}" if getattr(me, "username", None) else ("Không có" if lang == "vi" else "None")
    phone_fmt = f"+{me.phone}" if getattr(me, "phone", None) else phone

    if not is_guest:
        add_or_update_account(phone_fmt, full_name, username, session_path)
        print(f"\n{Fore.GREEN}{t('acc_saved', lang)} {full_name} ({phone_fmt}){Style.RESET_ALL}")
    else:
        print(f"\n{Fore.YELLOW}{t('guest_notice', lang)}{Style.RESET_ALL}")

    time.sleep(1)
    return client, me, session_path, is_guest


# =============================================================================
#   QUÉT HỘI THOẠI & LỌC ĐA NĂNG
# =============================================================================

async def scan_dialogs(
    client: TelegramClient,
    mode: int,
    config: dict,
    whitelist: Set[str],
    scan_limit: Optional[int] = None,
    my_id: int = 0,
    chat_filter: str = "all",
    keywords: Optional[List[str]] = None,
    inactive_days: int = 0,
    lang: str = "vi"
):
    """
    Quét danh sách các hội thoại theo chế độ với tốc độ cao nhất
    """
    limit_text = f"({scan_limit})" if scan_limit else ("(All)" if lang == "en" else "(Toàn bộ)")
    scan_header = "⚡ [*] Scanning dialogs..." if lang == "en" else f"⚡ [*] Đang quét danh sách hội thoại {limit_text}..."
    print(f"\n{Fore.CYAN}{scan_header}{Style.RESET_ALL}")

    target_dialogs = []
    skipped_admin = []
    skipped_whitelist = []
    total_scanned = 0

    skip_admin = config.get("skip_admin_or_owned", True)
    now_utc = datetime.datetime.now(datetime.timezone.utc)
    clean_kws = [kw.strip().lower() for kw in (keywords or []) if kw.strip()]

    async for dialog in client.iter_dialogs(limit=scan_limit, ignore_migrated=True):
        total_scanned += 1

        if total_scanned % 5 == 0 or total_scanned == 1:
            counter_text = f"Duyệt: {total_scanned} | Tìm thấy: {len(target_dialogs)}" if lang == "vi" else f"Scanned: {total_scanned} | Found: {len(target_dialogs)}"
            print(f"\r{Fore.CYAN}⚡ [SCANNING] {counter_text}...{Style.RESET_ALL}   ", end="", flush=True)

        entity = dialog.entity
        is_user = dialog.is_user
        is_bot = bool(getattr(entity, 'bot', False))

        # Telegram Service Notifications (777000) & Saved Messages
        if is_user and (dialog.id in [777000, my_id] or getattr(entity, 'id', None) in [777000, my_id]):
            continue

        is_group = dialog.is_group
        is_channel = dialog.is_channel and not dialog.is_group

        if mode == 1 and not is_group:
            continue
        elif mode == 2 and not is_channel:
            continue
        elif mode == 3 and not (is_group or is_channel):
            continue
        elif mode == 4:
            if not is_user:
                continue
            if chat_filter == "only_bot" and not is_bot:
                continue
            if chat_filter == "only_user" and is_bot:
                continue
        elif mode == 5 and not (is_group or is_channel or is_user):
            continue
        elif mode == 6:
            if not (is_group or is_channel):
                continue
            title_search = (dialog.title or "").lower()
            user_search = (getattr(entity, 'username', '') or "").lower()
            matched_kw = None
            for kw in clean_kws:
                if kw in title_search or kw in user_search:
                    matched_kw = kw
                    break
            if not matched_kw:
                continue
        elif mode == 7:
            if not is_group:
                continue
            dialog_date = dialog.date
            if dialog_date:
                if dialog_date.tzinfo is None:
                    dialog_date = dialog_date.replace(tzinfo=datetime.timezone.utc)
                diff_days = (now_utc - dialog_date).days
                if diff_days < inactive_days:
                    continue
            else:
                diff_days = 9999

        title = dialog.title or getattr(entity, 'first_name', '') or ("Không tên" if lang == "vi" else "Untitled")
        if is_user:
            chat_type = "🤖 Bot" if is_bot else ("💬 Trò chuyện" if lang == "vi" else "💬 Chat")
            action_desc = "Block & Wipe" if is_bot else "Delete"
        elif is_group:
            chat_type = "👥 Nhóm" if lang == "vi" else "👥 Group"
            action_desc = "Leave"
        else:
            chat_type = "📢 Kênh" if lang == "vi" else "📢 Channel"
            action_desc = "Leave"

        extra_note = ""
        if mode == 6 and 'matched_kw' in locals() and matched_kw:
            extra_note = f" [Keyword: '{matched_kw}']"
        elif mode == 7 and 'diff_days' in locals():
            extra_note = f" [Inactive: {diff_days}d]"

        if is_in_whitelist(dialog, whitelist):
            skipped_whitelist.append((dialog, f"{title} (ID: {dialog.id})"))
            continue

        if not is_user and skip_admin:
            is_adm, role_desc = is_user_admin_or_owner(entity)
            if is_adm:
                skipped_admin.append((dialog, f"{title} [{role_desc}]"))
                continue

        target_dialogs.append({
            "dialog": dialog,
            "title": f"{title}{extra_note}",
            "id": dialog.id,
            "type": chat_type,
            "action_desc": action_desc,
            "is_user": is_user,
            "is_bot": is_bot,
            "is_group": is_group,
            "is_channel": dialog.is_channel
        })

    done_msg = f"✓ [SCAN COMPLETE] Scanned {total_scanned} dialogs | Found {len(target_dialogs)} matching targets!" if lang == "en" else f"✓ [QUÉT HOÀN TẤT] Đã duyệt {total_scanned} hội thoại | Tìm thấy {len(target_dialogs)} mục phù hợp!"
    print(f"\r{Fore.GREEN}{done_msg}              {Style.RESET_ALL}\n")
    return target_dialogs, skipped_admin, skipped_whitelist, total_scanned


async def execute_actions(client: TelegramClient, targets: List[dict], config: dict, lang: str = "vi"):
    """Thực hiện rời nhóm/kênh hoặc xóa trò chuyện với cơ chế an toàn tối đa"""
    total = len(targets)
    if total == 0:
        print(f"{Fore.YELLOW}{t('no_targets', lang)}{Style.RESET_ALL}")
        return

    min_delay = float(config.get("min_delay_seconds", 0.0))
    max_delay = float(config.get("max_delay_seconds", 0.0))
    batch_size = int(config.get("batch_size", 15))
    batch_cooldown = float(config.get("batch_cooldown_seconds", 0.0))
    auto_flood = bool(config.get("auto_flood_wait", True))

    print(f"\n{Fore.GREEN}{Style.BRIGHT}{t('exec_title', lang, count=total)}{Style.RESET_ALL}")
    print(t("exec_params", lang, min_d=min_delay, max_d=max_delay, cooldown=batch_cooldown, batch=batch_size) + "\n")

    success_count = 0
    error_count = 0
    start_time = time.time()

    for idx, item in enumerate(targets, 1):
        dialog = item["dialog"]
        title = item["title"]
        chat_id = item["id"]
        chat_type = item["type"]
        is_user = item["is_user"]
        is_bot = item.get("is_bot", False)
        is_channel = item["is_channel"]

        prefix = f"[{idx}/{total}]"

        while True:
            try:
                if is_user:
                    if is_bot:
                        try:
                            await client(BlockRequest(id=dialog.input_entity))
                        except Exception:
                            pass
                    await client(DeleteHistoryRequest(peer=dialog.input_entity, max_id=0, revoke=True))
                    success_count += 1
                    note = t("blocked_and_deleted", lang) if is_bot else ""
                    print(f"{Fore.GREEN}{prefix} {t('del_success', lang)}{Style.RESET_ALL} {chat_type}: {Fore.WHITE}{title}{Style.RESET_ALL} (ID: {chat_id}){note}")
                elif is_channel:
                    await client(LeaveChannelRequest(dialog.input_entity))
                    success_count += 1
                    print(f"{Fore.GREEN}{prefix} {t('leave_success', lang)}{Style.RESET_ALL} {chat_type}: {Fore.WHITE}{title}{Style.RESET_ALL} (ID: {chat_id})")
                else:
                    await client(DeleteChatUserRequest(chat_id=dialog.id, user_id="me"))
                    success_count += 1
                    print(f"{Fore.GREEN}{prefix} {t('leave_success', lang)}{Style.RESET_ALL} {chat_type}: {Fore.WHITE}{title}{Style.RESET_ALL} (ID: {chat_id})")
                break

            except FloodWaitError as e:
                wait_sec = e.seconds
                print(f"\n{Fore.RED}{Style.BRIGHT}{t('flood_warn', lang, sec=wait_sec)}{Style.RESET_ALL}")
                if auto_flood:
                    await countdown_sleep(wait_sec + 2, reason="FloodWait Handling")
                    continue
                else:
                    return

            except PeerFloodError:
                print(f"\n{Fore.RED}{Style.BRIGHT}{t('peer_flood_warn', lang)}{Style.RESET_ALL}")
                print(t("peer_flood_advice", lang) + "\n")
                return

            except (ChannelPrivateError, UserNotParticipantError):
                print(f"{Fore.YELLOW}{prefix} {t('skip_label', lang)} {title}")
                success_count += 1
                break

            except ChatAdminRequiredError:
                print(f"{Fore.YELLOW}{prefix} {t('skip_label', lang)} Admin required: {title}")
                error_count += 1
                break

            except Exception as e:
                print(f"{Fore.RED}{prefix} {t('err_label', lang)} {title}: {e}")
                error_count += 1
                break

        if idx < total:
            if batch_size > 0 and batch_cooldown > 0 and idx % batch_size == 0:
                print(f"\n{Fore.CYAN}{t('cooldown_notice', lang, cur=idx, total=total)}{Style.RESET_ALL}")
                await countdown_sleep(batch_cooldown, reason=t("cooldown_reason", lang, batch=batch_size))
            else:
                if max_delay > 0:
                    jitter_delay = random.uniform(min_delay, max_delay)
                    if jitter_delay > 0:
                        await asyncio.sleep(jitter_delay)

    elapsed = round(time.time() - start_time, 1)
    print(f"\n{Fore.GREEN}{Style.BRIGHT}==========================================")
    print(t("exec_done", lang))
    print(f"==========================================")
    print(f"{t('exec_success_stat', lang)} {success_count}/{total}")
    print(f"{t('exec_error_stat', lang)} {error_count}")
    print(t("exec_time_stat", lang, sec=elapsed) + f"{Style.RESET_ALL}\n")


# =============================================================================
#   DỌN SẠCH DANH BẠ RÁC (CONTACTS CLEANER)
# =============================================================================

async def clean_contacts_menu(client: TelegramClient, config: dict, lang: str = "vi"):
    """
    Quét và dọn dẹp danh bạ Telegram (Contacts Cleaner)
    """
    clear_screen()
    print_banner(lang)
    print(f"{Fore.CYAN}{Style.BRIGHT}{t('contacts_title', lang)}{Style.RESET_ALL}\n")
    print(t("contacts_loading", lang))

    try:
        contacts_res = await client(GetContactsRequest(hash=0))
        users = contacts_res.users
    except Exception as e:
        print(f"{Fore.RED}{t('contacts_err', lang)} {e}{Style.RESET_ALL}")
        input(f"\n{Fore.GREEN}{t('press_enter', lang)}{Style.RESET_ALL}")
        return

    total_contacts = len(users)
    deleted_accounts = [u for u in users if getattr(u, 'deleted', False)]
    active_contacts = [u for u in users if not getattr(u, 'deleted', False)]

    print(f"\n📊 {Fore.WHITE}{Style.BRIGHT}{t('contacts_res_title', lang)}{Style.RESET_ALL}")
    print(f"{t('contacts_total', lang)} {Fore.CYAN}{total_contacts}{Style.RESET_ALL}")
    print(f"{t('contacts_active', lang)} {Fore.GREEN}{len(active_contacts)}{Style.RESET_ALL}")
    print(f"{t('contacts_deleted_acc', lang)} {Fore.RED}{len(deleted_accounts)}{Style.RESET_ALL}\n")

    if total_contacts == 0:
        print(f"{Fore.GREEN}{t('contacts_empty', lang)}{Style.RESET_ALL}")
        input(f"\n{Fore.GREEN}{t('press_enter', lang)}{Style.RESET_ALL}")
        return

    print(f"{Fore.WHITE}{t('contacts_opt_title', lang)}{Style.RESET_ALL}")
    print(f" [{Fore.CYAN}1{Style.RESET_ALL}] {Fore.YELLOW}{t('contacts_opt_1', lang)}{Style.RESET_ALL}")
    print(f" [{Fore.CYAN}2{Style.RESET_ALL}] {Fore.RED}{t('contacts_opt_2', lang, count=total_contacts)}{Style.RESET_ALL}")
    print(f" [{Fore.CYAN}0{Style.RESET_ALL}] {t('contacts_opt_0', lang)}\n")

    opt = input(t("prompt_choice", lang)).strip()

    targets_to_delete = []
    if opt == "1":
        targets_to_delete = deleted_accounts
        mode_desc = f"delete {len(deleted_accounts)} 'Deleted Account' contacts" if lang == "en" else f"xóa {len(deleted_accounts)} nick 'Deleted Account'"
        if not deleted_accounts:
            print(f"{Fore.GREEN}{t('contacts_no_del', lang)}{Style.RESET_ALL}")
            input(f"\n{Fore.GREEN}{t('press_enter_cont', lang)}{Style.RESET_ALL}")
            return
    elif opt == "2":
        targets_to_delete = users
        mode_desc = f"wipe ALL {total_contacts} contacts in address book" if lang == "en" else f"xóa TẤT CẢ {total_contacts} liên hệ trong danh bạ"
    else:
        return

    print(f"\n{Fore.RED}{Style.BRIGHT}{t('contacts_confirm', lang, desc=mode_desc)}{Style.RESET_ALL}")
    cf = input(t("confirm_prompt", lang, yes="YES")).strip().lower()
    if cf not in ["yes", "y"]:
        print(f"{Fore.YELLOW}{t('op_cancelled', lang)}{Style.RESET_ALL}")
        input(f"\n{Fore.GREEN}{t('press_enter', lang)}{Style.RESET_ALL}")
        return

    print(f"\n{Fore.CYAN}{t('contacts_cleaning', lang, count=len(targets_to_delete))}{Style.RESET_ALL}")
    deleted_count = 0
    start_t = time.time()

    chunk_size = 50
    for i in range(0, len(targets_to_delete), chunk_size):
        chunk = targets_to_delete[i:i + chunk_size]
        input_users = []
        for u in chunk:
            try:
                inp = await client.get_input_entity(u)
                input_users.append(inp)
            except Exception:
                pass

        if input_users:
            try:
                await client(DeleteContactsRequest(id=input_users))
                deleted_count += len(input_users)
                print(f"  {Fore.GREEN}{t('contacts_batch_done', lang, cur=deleted_count, total=len(targets_to_delete))}{Style.RESET_ALL}")
                await asyncio.sleep(0.5)
            except FloodWaitError as e:
                print(f"{Fore.YELLOW}[!] FloodWait {e.seconds}s...{Style.RESET_ALL}")
                await countdown_sleep(e.seconds + 1, "Contacts FloodWait")
            except Exception as e:
                print(f"{Fore.RED}[!] Batch Error: {e}{Style.RESET_ALL}")

    elapsed = round(time.time() - start_t, 1)
    print(f"\n{Fore.GREEN}{Style.BRIGHT}{t('contacts_done', lang, count=deleted_count, sec=elapsed)}{Style.RESET_ALL}")
    input(f"\n{Fore.GREEN}{t('press_enter', lang)}{Style.RESET_ALL}")


# =============================================================================
#   CÀI ĐẶT THÔNG SỐ VẬN HÀNH & ĐỔI NGÔN NGỮ
# =============================================================================

def switch_language_menu(config: dict, current_lang: str) -> str:
    """Menu đổi ngôn ngữ (Tiếng Việt <-> English)"""
    clear_screen()
    print_banner(current_lang)
    print(f"{Fore.CYAN}{Style.BRIGHT}{t('lang_switch_title', current_lang)}{Style.RESET_ALL}\n")
    print(f" [{Fore.CYAN}1{Style.RESET_ALL}] 🇻🇳 Tiếng Việt")
    print(f" [{Fore.CYAN}2{Style.RESET_ALL}] 🇬🇧 English\n")
    print(f" [{Fore.CYAN}0{Style.RESET_ALL}] {t('settings_0', current_lang)}\n")

    c = input(t("prompt_choice", current_lang)).strip()
    if c == "1":
        config["language"] = "vi"
        save_config(config)
        print(f"\n{Fore.GREEN}{t('lang_changed', 'vi')}{Style.RESET_ALL}")
        time.sleep(1)
        return "vi"
    elif c == "2":
        config["language"] = "en"
        save_config(config)
        print(f"\n{Fore.GREEN}{t('lang_changed', 'en')}{Style.RESET_ALL}")
        time.sleep(1)
        return "en"
    return current_lang


async def settings_menu(config: dict, lang: str = "vi"):
    """Menu chỉnh sửa thông số an toàn & hiệu năng"""
    while True:
        clear_screen()
        print_banner(lang)
        print(f"{Fore.CYAN}{Style.BRIGHT}{t('settings_title', lang)}{Style.RESET_ALL}\n")
        print(f" [1] {t('settings_1', lang)} {Fore.GREEN}{config['min_delay_seconds']}s{Style.RESET_ALL}")
        print(f" [2] {t('settings_2', lang)} {Fore.GREEN}{config['max_delay_seconds']}s{Style.RESET_ALL}")
        print(f" [3] {t('settings_3', lang)} {Fore.GREEN}{config['batch_size']}{Style.RESET_ALL}")
        print(f" [4] {t('settings_4', lang)} {Fore.GREEN}{config['batch_cooldown_seconds']}s{Style.RESET_ALL}")
        print(f" [5] {t('settings_5', lang)} {Fore.GREEN}{'ON' if config['skip_admin_or_owned'] else 'OFF'}{Style.RESET_ALL}")
        print(f" [6] {t('settings_6', lang)} {Fore.GREEN}{'ON' if config['auto_flood_wait'] else 'OFF'}{Style.RESET_ALL}")
        print(f" [7] {t('settings_7', lang)}")
        print(f" [0] {t('settings_0', lang)}\n")

        choice = input(t("prompt_choice", lang)).strip()
        if choice == "0":
            break
        elif choice == "1":
            val = input("Minimum delay (seconds, e.g. 0 or 1.5): ").strip()
            try:
                config["min_delay_seconds"] = max(0.0, float(val))
                save_config(config)
            except ValueError:
                pass
        elif choice == "2":
            val = input("Maximum delay (seconds, e.g. 3.0): ").strip()
            try:
                config["max_delay_seconds"] = max(config["min_delay_seconds"], float(val))
                save_config(config)
            except ValueError:
                pass
        elif choice == "3":
            val = input("Batch size (e.g. 15): ").strip()
            if val.isdigit() and int(val) > 0:
                config["batch_size"] = int(val)
                save_config(config)
        elif choice == "4":
            val = input("Cooldown per batch (seconds, e.g. 30): ").strip()
            try:
                config["batch_cooldown_seconds"] = max(0.0, float(val))
                save_config(config)
            except ValueError:
                pass
        elif choice == "5":
            config["skip_admin_or_owned"] = not config.get("skip_admin_or_owned", True)
            save_config(config)
        elif choice == "6":
            config["auto_flood_wait"] = not config.get("auto_flood_wait", True)
            save_config(config)
        elif choice == "7":
            config["api_id"] = 0
            config["api_hash"] = ""
            save_config(config)
            print(f"{Fore.GREEN}[✓] API info reset. Restart tool to enter new API credentials.{Style.RESET_ALL}")
            time.sleep(1.5)


# =============================================================================
#   HÀM CHÍNH (MAIN ASYNC)
# =============================================================================

async def main_async():
    config = await setup_credentials()
    whitelist = load_whitelist()

    api_id = config["api_id"]
    api_hash = config["api_hash"]
    lang = config.get("language", "vi")

    while True:
        # Chọn tài khoản hoặc đăng nhập nick mới
        client, me, session_path, is_guest, lang = await select_or_login_account(api_id, api_hash, config)
        if not client:
            print(f"\n{Fore.GREEN}{t('thank_you', lang)}{Style.RESET_ALL}")
            break

        first_name = getattr(me, "first_name", "") or ""
        last_name = getattr(me, "last_name", "") or ""
        full_name = f"{first_name} {last_name}".strip() or "Telegram User"
        username = f"@{me.username}" if getattr(me, "username", None) else ("Không có" if lang == "vi" else "None")
        phone_display = f"+{me.phone}" if getattr(me, "phone", None) else "N/A"
        guest_tag = f" {Fore.YELLOW}{t('guest_tag', lang)}{Style.RESET_ALL}" if is_guest else ""

        user_switched = False

        while True:
            clear_screen()
            print_banner(lang)
            print(f"{t('logged_in_as', lang)} {Fore.GREEN}{Style.BRIGHT}{full_name}{Style.RESET_ALL} ({Fore.CYAN}{phone_display}{Style.RESET_ALL} | {Fore.YELLOW}{username}{Style.RESET_ALL}){guest_tag}")
            print(f"{t('whitelist_status', lang, count=len(whitelist), file=WHITELIST_FILE)}\n")

            print(f"{Fore.WHITE}{Style.BRIGHT}{t('menu_header', lang)}{Style.RESET_ALL}")
            print(f" [{Fore.CYAN}1{Style.RESET_ALL}] {t('menu_1', lang)}")
            print(f" [{Fore.CYAN}2{Style.RESET_ALL}] {t('menu_2', lang)}")
            print(f" [{Fore.CYAN}3{Style.RESET_ALL}] {t('menu_3', lang)}")
            print(f" [{Fore.CYAN}4{Style.RESET_ALL}] {t('menu_4', lang)}")
            print(f" [{Fore.CYAN}5{Style.RESET_ALL}] {Fore.RED}{t('menu_5', lang)}{Style.RESET_ALL}")
            print(f" [{Fore.CYAN}6{Style.RESET_ALL}] {Fore.YELLOW}{t('menu_6', lang)}{Style.RESET_ALL}")
            print(f" [{Fore.CYAN}7{Style.RESET_ALL}] {Fore.YELLOW}{t('menu_7', lang)}{Style.RESET_ALL}")
            print(f" [{Fore.CYAN}8{Style.RESET_ALL}] {Fore.YELLOW}{t('menu_8', lang)}{Style.RESET_ALL}")
            print(f" [{Fore.CYAN}9{Style.RESET_ALL}] {t('menu_9', lang)}")
            print(f" [{Fore.CYAN}L{Style.RESET_ALL}] {Fore.MAGENTA}{t('menu_l', lang)}{Style.RESET_ALL}")
            print(f" [{Fore.CYAN}S{Style.RESET_ALL}] {t('menu_s', lang)}")
            print(f" [{Fore.CYAN}A{Style.RESET_ALL}] {t('menu_a', lang)}")
            print(f" [{Fore.CYAN}X{Style.RESET_ALL}] {Fore.RED}{t('menu_x', lang)}{Style.RESET_ALL}")
            print(f" [{Fore.CYAN}0{Style.RESET_ALL}] {t('menu_0', lang)}\n")

            choice = input(t("prompt_choice", lang)).strip().lower()

            if choice == "0":
                print(f"\n{Fore.GREEN}{t('thank_you', lang)}{Style.RESET_ALL}")
                if is_guest:
                    delete_account_session(session_path)
                await client.disconnect()
                return

            elif choice == "l":
                # Đổi ngôn ngữ
                lang = switch_language_menu(config, lang)
                continue

            elif choice == "a":
                # Đổi tài khoản khác
                if is_guest:
                    delete_account_session(session_path)
                await client.disconnect()
                user_switched = True
                break

            elif choice == "x":
                # Đăng xuất tài khoản này khỏi máy
                cf = input(f"\n{Fore.RED}{t('logout_confirm', lang, name=full_name)}{Style.RESET_ALL}").strip().lower()
                if cf in ["y", "yes"]:
                    try:
                        await client.log_out()
                    except Exception:
                        pass
                    delete_account_session(session_path)
                    await client.disconnect()
                    print(f"{Fore.GREEN}{t('logout_success', lang)}{Style.RESET_ALL}")
                    time.sleep(1.5)
                    user_switched = True
                    break
                else:
                    input(f"\n{Fore.GREEN}{t('press_enter', lang)}{Style.RESET_ALL}")
                    continue

            elif choice == "s":
                await settings_menu(config, lang=lang)
                continue

            elif choice == "8":
                await clean_contacts_menu(client, config, lang=lang)
                continue

            elif choice in ["1", "2", "3", "4", "5", "6", "7", "9"]:
                is_dry_run = (choice == "9")
                actual_mode = int(choice) if not is_dry_run else 5

                if is_dry_run:
                    print(f"\n{Fore.CYAN}{t('dry_run_which', lang)}{Style.RESET_ALL}")
                    print(t("dry_run_opts", lang))
                    sub_c = input("Choice (1-7, default 5): ").strip()
                    if sub_c in ["1", "2", "3", "4", "5", "6", "7"]:
                        actual_mode = int(sub_c)
                    else:
                        actual_mode = 5

                chat_filter = "all"
                if actual_mode == 4:
                    print(f"\n{Fore.WHITE}{t('chat_filter_title', lang)}{Style.RESET_ALL}")
                    print(f" [{Fore.CYAN}1{Style.RESET_ALL}] {t('chat_filter_1', lang)}")
                    print(f" [{Fore.CYAN}2{Style.RESET_ALL}] {t('chat_filter_2', lang)}")
                    print(f" [{Fore.CYAN}3{Style.RESET_ALL}] {t('chat_filter_3', lang)}")
                    b_opt = input(t("prompt_choice", lang)).strip()
                    if b_opt == "2":
                        chat_filter = "only_bot"
                    elif b_opt == "3":
                        chat_filter = "only_user"

                keywords = None
                if actual_mode == 6:
                    print(f"\n{Fore.CYAN}{t('kw_title', lang)}{Style.RESET_ALL}")
                    print(f" [{Fore.CYAN}1{Style.RESET_ALL}] {t('kw_opt_1', lang, count=len(DEFAULT_SPAM_KEYWORDS))}")
                    print(f" [{Fore.CYAN}2{Style.RESET_ALL}] {t('kw_opt_2', lang)}")
                    kw_opt = input(t("prompt_choice", lang)).strip()
                    if kw_opt == "2":
                        custom_kw = input(t("kw_prompt", lang)).strip()
                        keywords = [k.strip() for k in custom_kw.split(",") if k.strip()]
                        if not keywords:
                            keywords = DEFAULT_SPAM_KEYWORDS
                    else:
                        keywords = DEFAULT_SPAM_KEYWORDS
                    print(f"{Fore.GREEN}{t('kw_active', lang, count=len(keywords))}{Style.RESET_ALL}")

                inactive_days = 0
                if actual_mode == 7:
                    print(f"\n{Fore.CYAN}{t('inact_title', lang)}{Style.RESET_ALL}")
                    print(f" [{Fore.CYAN}1{Style.RESET_ALL}] {t('inact_opt_1', lang)}")
                    print(f" [{Fore.CYAN}2{Style.RESET_ALL}] {t('inact_opt_2', lang)}")
                    print(f" [{Fore.CYAN}3{Style.RESET_ALL}] {t('inact_opt_3', lang)}")
                    print(f" [{Fore.CYAN}4{Style.RESET_ALL}] {t('inact_opt_4', lang)}")
                    print(f" [{Fore.CYAN}5{Style.RESET_ALL}] {t('inact_opt_5', lang)}")
                    inact_opt = input(t("prompt_choice", lang)).strip()
                    if inact_opt == "1":
                        inactive_days = 30
                    elif inact_opt == "3":
                        inactive_days = 90
                    elif inact_opt == "4":
                        inactive_days = 180
                    elif inact_opt == "5":
                        days_in = input(t("inact_prompt", lang)).strip()
                        inactive_days = int(days_in) if days_in.isdigit() and int(days_in) > 0 else 60
                    else:
                        inactive_days = 60
                    print(f"{Fore.GREEN}{t('inact_active', lang, days=inactive_days)}{Style.RESET_ALL}")

                # Scope
                print(f"\n{Fore.WHITE}{t('scan_scope_title', lang)}{Style.RESET_ALL}")
                print(f" [{Fore.CYAN}1{Style.RESET_ALL}] {t('scan_scope_1', lang)}")
                print(f" [{Fore.CYAN}2{Style.RESET_ALL}] {t('scan_scope_2', lang)}")
                print(f" [{Fore.CYAN}3{Style.RESET_ALL}] {t('scan_scope_3', lang)}")
                print(f" [{Fore.CYAN}4{Style.RESET_ALL}] {t('scan_scope_4', lang)}")
                print(f"       {Fore.YELLOW}{t('scan_scope_custom', lang)}{Style.RESET_ALL}")
                scan_opt = input(t("scan_scope_prompt", lang)).strip()

                scan_limit = None
                if scan_opt == "1":
                    scan_limit = 1000
                elif scan_opt == "2":
                    scan_limit = 2000
                elif scan_opt == "3":
                    scan_limit = 5000
                elif scan_opt == "4" or scan_opt == "":
                    scan_limit = None
                elif scan_opt.isdigit() and int(scan_opt) > 0:
                    scan_limit = int(scan_opt)

                targets, skipped_admin, skipped_wl, total_scanned = await scan_dialogs(
                    client,
                    actual_mode,
                    config,
                    whitelist,
                    scan_limit=scan_limit,
                    my_id=me.id,
                    chat_filter=chat_filter,
                    keywords=keywords,
                    inactive_days=inactive_days,
                    lang=lang
                )

                print(f"\n{Fore.CYAN}{t('scan_result_title', lang)}{Style.RESET_ALL}")
                print(f"{t('scan_res_scanned', lang)} {total_scanned}")
                print(f"{t('scan_res_matched', lang)} {Fore.GREEN}{len(targets)}{Style.RESET_ALL}")
                print(f"{t('scan_res_skipped_adm', lang)} {Fore.YELLOW}{len(skipped_admin)}{Style.RESET_ALL}")
                print(f"{t('scan_res_skipped_wl', lang)} {Fore.YELLOW}{len(skipped_wl)}{Style.RESET_ALL}")
                print(f"==============================================\n")

                if skipped_admin:
                    print(f"{Fore.YELLOW}{t('scan_res_adm_list', lang)}{Style.RESET_ALL}")
                    for _, name in skipped_admin[:5]:
                        print(f"   • {name}")
                    if len(skipped_admin) > 5:
                        print(f"   • ... +{len(skipped_admin) - 5}")
                    print()

                if is_dry_run:
                    print(f"{Fore.CYAN}{t('dry_run_list_title', lang)}{Style.RESET_ALL}")
                    for i, item in enumerate(targets, 1):
                        print(f"  {i}. [{item['type']}] {item['title']} (ID: {item['id']})")
                    input(f"\n{Fore.GREEN}{t('press_enter', lang)}{Style.RESET_ALL}")
                    continue

                if not targets:
                    print(f"{Fore.YELLOW}{t('no_targets', lang)}{Style.RESET_ALL}")
                    input(f"\n{Fore.GREEN}{t('press_enter_cont', lang)}{Style.RESET_ALL}")
                    continue

                # Confirmations
                if actual_mode == 5:
                    print(f"{Fore.RED}{Style.BRIGHT}{t('warn_nuke', lang)}{Style.RESET_ALL}")
                elif actual_mode == 4:
                    filter_text = "BOTS" if chat_filter == "only_bot" else ("User DMs" if chat_filter == "only_user" else "Direct Chats & Bots")
                    print(f"{Fore.RED}{Style.BRIGHT}{t('warn_chat', lang, count=len(targets), desc=filter_text)}{Style.RESET_ALL}")
                elif actual_mode == 6:
                    print(f"{Fore.RED}{Style.BRIGHT}{t('warn_kw', lang, count=len(targets))}{Style.RESET_ALL}")
                elif actual_mode == 7:
                    print(f"{Fore.RED}{Style.BRIGHT}{t('warn_inact', lang, count=len(targets), days=inactive_days)}{Style.RESET_ALL}")
                else:
                    print(f"{Fore.RED}{Style.BRIGHT}{t('warn_leave', lang, count=len(targets))}{Style.RESET_ALL}")

                confirm = input(t("confirm_prompt", lang, yes="YES")).strip().lower()

                if confirm in ["yes", "y"]:
                    await execute_actions(client, targets, config, lang=lang)
                else:
                    print(f"{Fore.YELLOW}{t('op_cancelled', lang)}{Style.RESET_ALL}")

                input(f"\n{Fore.GREEN}{t('press_enter', lang)}{Style.RESET_ALL}")

            else:
                print(f"{Fore.RED}{t('invalid_choice', lang)}{Style.RESET_ALL}")
                time.sleep(1)

        if not user_switched:
            break


def main():
    try:
        asyncio.run(main_async())
    except KeyboardInterrupt:
        print(f"\n\n{Fore.YELLOW}[!] Stopped by user (Ctrl+C). Safe exit!{Style.RESET_ALL}")
    except Exception as e:
        print(f"\n{Fore.RED}[X] Unexpected error: {e}{Style.RESET_ALL}")


if __name__ == "__main__":
    main()
