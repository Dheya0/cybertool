import streamlit as st
import re
import requests
import hashlib
import plotly.express as px
import pandas as pd

# --- إعداد الصفحة ---
st.set_page_config(page_title="أدوات الأمن السيبراني", layout="wide", initial_sidebar_state="collapsed")

# --- CSS لتصميم ملون مع صورة متحركة ---
st.markdown(
    """
    <style>
    /* General RTL Styling */
    body {
        direction: rtl;
        text-align: right;
    }

    /* Streamlit Component Styling (Override defaults) */
    .stTextInput > div > div > input {
        text-align: right;
    }

    .stTextArea > div > div > textarea {
        text-align: right;
    }

    .stButton > button {
        background: linear-gradient(45deg, #f59e0b, #f97316);
        color: white;
        font-weight: 700;
        border-radius: 12px;
        padding: 12px 25px;
        font-size: 1.1em;
        transition: background 0.3s ease;
        box-shadow: 0 4px 12px rgba(245, 115, 22, 0.6);
    }

    .stButton > button:hover {
        background: linear-gradient(45deg, #f97316, #b45309);
        color: #fffbeb;
        box-shadow: 0 6px 16px rgba(180, 83, 9, 0.8);
    }

    /* Card Styling */
    .card {
        background: linear-gradient(135deg, #ffecd2 0%, #fcb69f 100%);
        border-radius: 18px;
        padding: 30px 25px;
        margin-bottom: 25px;
        box-shadow: 0 10px 30px rgba(252, 182, 159, 0.4);
        transition: transform 0.3s ease;
    }

    .card:hover {
        transform: translateY(-7px);
        box-shadow: 0 14px 40px rgba(252, 182, 159, 0.6);
    }

    /* Progress Bar Styling */
    .progress-container {
        background-color: #fde68a;
        border-radius: 14px;
        height: 26px;
        margin-top: 10px;
        box-shadow: inset 1px 1px 4px #fff7d6, inset -1px -1px 4px #f5f3c1;
    }

    .progress-bar {
        height: 100%;
        border-radius: 14px;
        text-align: center;
        color: #874f00;
        font-weight: 700;
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        display: flex;
        justify-content: center;
        align-items: center;
        box-shadow: 0 2px 6px rgba(191, 90, 0, 0.5);
        background: linear-gradient(90deg, #f97316, #facc15);
    }

    /* Header Styling */
    .header-title {
        text-align: center;
        font-size: 3em;
        font-weight: 900;
        background: linear-gradient(to right, #fb923c, #f97316);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 7px;
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    }

    .header-subtitle {
        text-align: center;
        font-size: 1.3em;
        color: #b45309;
        margin-bottom: 25px;
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        font-weight: 600;
    }

    /* Alert Styling */
    .stWarning {
        background-color: #fffbeb !important;
        border-left: 6px solid #f59e0b !important;
        color: #92400e !important;
        font-weight: 700;
    }

    .stError {
        background-color: #fee2e2 !important;
        border-left: 6px solid #ef4444 !important;
        color: #b91c1c !important;
        font-weight: 700;
    }

    .stSuccess {
        background-color: #ecfdf5 !important;
        border-left: 6px solid #22c55e !important;
        color: #166534 !important;
        font-weight: 700;
    }

    /* Header Icon Animation */
    .header-icon {
        width: 45px;
        vertical-align: middle;
        margin-right: 12px;
        animation: bounce 2s infinite;
    }

    @keyframes bounce {
        0%, 100% { transform: translateY(0); }
        50% { transform: translateY(-14px); }
    }
    </style>
    """,
    unsafe_allow_html=True,
)

st.markdown(
    """
    <h1 class='header-title'>
        <img src="https://media.giphy.com/media/Qxgxh4w1goZ5o/giphy.gif" alt="cyber icon" class="header-icon">
        أدوات الأمن السيبراني التفاعلية
    </h1>
    """,
    unsafe_allow_html=True,
)

st.markdown("<p class='header-subtitle'>تطبيقات عملية لتعلم مبادئ الأمن السيبراني</p>", unsafe_allow_html=True)
st.markdown("---")

# Tabs
tab1, tab2, tab3 = st.tabs(
    ["فحص كلمة المرور", "كشف التصيد الاحتيالي", "نصائح الأمان"],
)

# --- دوال القوة والتنبيهات ---
def check_password_strength(pwd):
    score = 0
    feedback = []
    if len(pwd) < 8:
        feedback.append("يجب أن تتكون كلمة المرور من 8 أحرف على الأقل.");
        score -= 1  # Penalize short passwords
    else:
        score += 1
    if not re.search(r"[a-z]", pwd):
        feedback.append("يجب أن تحتوي كلمة المرور على أحرف صغيرة.")
    else:
        score += 1
    if not re.search(r"[A-Z]", pwd):
        feedback.append("يجب أن تحتوي كلمة المرور على أحرف كبيرة.")
    else:
        score += 1
    if not re.search(r"[0-9]", pwd):
        feedback.append("يجب أن تحتوي كلمة المرور على أرقام.")
    else:
        score += 1
    if not re.search(r"[^A-Za-z0-9]", pwd):
        feedback.append("يجب أن تحتوي كلمة المرور على رموز خاصة.")
    else:
        score += 1
    if "password" in pwd.lower() or "123456" in pwd:
        feedback.append("تجنب استخدام كلمات مرور شائعة مثل 'password' أو '123456'.");
        score -= 1
    return score, feedback


def get_strength_text(score):
    if score <= 1:
        return "ضعيفة جداً"
    if score <= 3:
        return "ضعيفة"
    if score <= 4:
        return "جيدة"
    return "قوية جداً"


def get_strength_color(score):
    if score <= 1:
        return "#DC2626"  # أحمر
    if score <= 3:
        return "#F59E0B"  # أصفر
    if score <= 4:
        return "#3B82F6"  # أزرق
    return "#16A34A"  # أخضر


# فحص كلمة المرور مع التقييم اللحظي والتأكد من تسريبها
def check_pwned_password(password):
    sha1pwd = hashlib.sha1(password.encode('utf-8')).hexdigest().upper()
    prefix = sha1pwd[:5]
    suffix = sha1pwd[5:]
    url = f"https://api.pwnedpasswords.com/range/{prefix}"
    try:
        res = requests.get(url)
        res.raise_for_status()  # Raise HTTPError for bad responses (4xx or 5xx)
        hashes = (line.split(':') for line in res.text.splitlines())
        for h, count in hashes:
            if h == suffix:
                return int(count)
        return 0
    except requests.exceptions.RequestException as e:
        st.error(f"حدث خطأ أثناء التحقق من التسريب: {e}")
        return None  # Indicate an error occurred

# Define update_strength function BEFORE using it
def update_strength():
    pwd = st.session_state.pwd_input
    if pwd:
        score, feedback = check_password_strength(pwd)
        st.session_state.score = score
        st.session_state.feedback = feedback
        # تحقق من التسريب
        pwned_count = check_pwned_password(pwd)
        st.session_state.pwned_count = pwned_count
    else:
        st.session_state.score = 0
        st.session_state.feedback = []
        st.session_state.pwned_count = 0


# Tab 1: فحص كلمة المرور
if 'pwd_input' not in st.session_state:
    st.session_state.pwd_input = ""
if 'score' not in st.session_state:
    st.session_state.score = 0
if 'feedback' not in st.session_state:
    st.session_state.feedback = []
if 'pwned_count' not in st.session_state:
    st.session_state.pwned_count = 0

with tab1:
    st.markdown("<div class='card'>", unsafe_allow_html=True)
    st.subheader("فاحص قوة كلمة المرور")
    pwd_input = st.text_input("أدخل كلمة المرور", type="password", key="pwd_input", on_change=update_strength)

    if st.session_state.pwd_input:
        score = st.session_state.score
        feedback = st.session_state.feedback
        pwned_count = st.session_state.pwned_count

        st.markdown(
            f"""
            <div class='progress-container'>
                <div class='progress-bar' style='width:{min(max(score, 0) / 5 * 100, 100)}%; background-color:{get_strength_color(score)}'>
                {get_strength_text(score)}
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        if feedback:
            st.warning("\n".join(feedback))

        if pwned_count is not None:
            if pwned_count > 0:
                st.error(
                    f"تنبيه: كلمة المرور هذه ظهرت في تسريبات {pwned_count} مرة! يُنصح بتغييرها."
                )
            else:
                st.success("كلمة المرور آمنة وغير مسربة.")

    st.markdown("</div>", unsafe_allow_html=True)

# Tab 2: كشف التصيد الاحتيالي
def check_phishing_email(email):
    indicators = [
        (r"urgent|عاجل|فوري", "يحتوي على كلمات تحث على الاستعجال."),
        (r"click here|اضغط هنا", "يحتوي على روابط مشبوهة."),
        (r"verify.*account|تأكيد.*حساب", "يطلب تأكيد معلومات الحساب."),
        (r"suspended|معلق|مجمد", "يهدد بتعليق الحساب."),
        (r"congratulations|مبروك|فائز", "يدعي الفوز بجائزة."),
        (r"limited time|وقت محدود", "يضع ضغط زمني."),
        (r"@[a-zA-Z0-9-]+\.(tk|ml|ga|cf)", "يستخدم نطاق ويب مشبوه."),
        (r"dear customer|عزيزي العميل", "تحية عامة وغير شخصية."),
        (r"bank account|رقم الحساب البنكي", "يطلب معلومات حساسة."),
        (r"security alert|تنبيه أمني", "يستخدم عبارات تنبيه أمني لخلق الذعر.")
    ]
    found = [msg for pattern, msg in indicators if re.search(pattern, email, re.IGNORECASE)]
    if len(found) >= 3:
        risk = "عالي"
    elif len(found) == 2:
        risk = "متوسط"
    elif len(found) == 1:
        risk = "منخفض"
    else:
        risk = "آمن"
    return found, risk


with tab2:
    st.markdown("<div class='card'>", unsafe_allow_html=True)
    st.subheader("كشف التصيد الاحتيالي")
    email_text = st.text_area("الصق نص الرسالة الإلكترونية هنا...")
    if st.button("فحص الرسالة"):
        if email_text.strip():
            indicators, risk = check_phishing_email(email_text)
            if indicators:
                st.error(f"تحذير: الرسالة تحتوي على علامات تصيد احتيالي (مستوى الخطر: {risk})")
                st.toast(f"تحذير: تم اكتشاف علامات تصيد {risk} الخطورة!", icon="⚠️", duration=4500)
                st.write("العلامات المكتشفة:")
                for i, msg in enumerate(indicators, 1):
                    st.write(f"{i}. {msg}")
            else:
                st.success("هذه الرسالة تبدو آمنة")
    st.markdown("</div>", unsafe_allow_html=True)

# Tab 3: نصائح الأمان
with tab3:
    st.markdown("<div class='card'>", unsafe_allow_html=True)
    st.subheader("نصائح الأمان")
    st.markdown("""
    - استخدم كلمات مرور قوية ومختلفة لكل حساب.
    - فعّل المصادقة الثنائية حيثما أمكن.
    - لا تضغط على روابط مشبوهة أو تفتح مرفقات غير موثوقة.
    - حدّث البرامج ونظام التشغيل باستمرار.
    - احتفظ بنسخ احتياطية للبيانات الهامة.
    - تجنب استخدام الشبكات العامة للمعاملات الحساسة.
    - تحقق دائمًا من هوية المرسل قبل مشاركة المعلومات الشخصية.
    - استخدم برامج مكافحة الفيروسات والجدران النارية المحدثة.
    - راقب حساباتك المالية بانتظام لاكتشاف أي نشاط غير معتاد.
    - قم بتشفير البيانات الحساسة عند التخزين أو المشاركة.
    - احذف أو امسح البيانات الشخصية قبل التخلص من الأجهزة القديمة.
    - لا تشارك كلمات المرور مع أي شخص.
    - استخدم مدير كلمات مرور موثوق لتخزين كلمات المرور بشكل آمن.
    - احذر من رسائل البريد الإلكتروني التي تطلب معلوماتك الشخصية أو البنكية.
    - تأكد من تحديث الإضافات والمكونات الإضافية للمتصفحات باستمرار.
    """)
    st.markdown("</div>", unsafe_allow_html=True)
