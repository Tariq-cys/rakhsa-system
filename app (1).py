import streamlit as st
from datetime import datetime, date
import json, os

# ══════════════════════════════════════════════
# إعدادات الصفحة
# ══════════════════════════════════════════════
st.set_page_config(
    page_title="نظام متابعة الرخصة | قتاد اللوجستية",
    page_icon="🪪", layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Tajawal:wght@400;500;700;800&display=swap');
*, .stApp { font-family: 'Tajawal', sans-serif !important; direction: rtl; }
.main { background: #F2F5FA; }
.kpi-card {
    background: white; border-radius: 12px; padding: 18px;
    text-align: center; box-shadow: 0 2px 10px rgba(0,0,0,0.08);
    border-top: 4px solid; margin-bottom: 10px;
}
.kpi-card .val { font-size: 40px; font-weight: 800; line-height: 1.1; }
.kpi-card .lbl { font-size: 12px; color: #666; margin-top: 4px; font-weight: 600; }
.styled-table {
    width:100%; border-collapse:collapse; background:white;
    border-radius:10px; overflow:hidden;
    box-shadow:0 2px 8px rgba(0,0,0,0.06); font-size:13px;
}
.styled-table th { background:#1F3864; color:white; padding:10px 12px; text-align:center; font-weight:700; }
.styled-table td { padding:9px 12px; border-bottom:1px solid #F0F0F0; text-align:center; }
.styled-table tr:nth-child(even) { background:#F8FAFC; }
.styled-table tr:hover { background:#EBF3FF; }
.alert-r { background:#FDECEA; border-right:4px solid #C00000; padding:10px 14px; border-radius:8px; margin:4px 0; }
.alert-o { background:#FFF2CC; border-right:4px solid #BF8F00; padding:10px 14px; border-radius:8px; margin:4px 0; }
.alert-g { background:#E2EFDA; border-right:4px solid #1E7145; padding:10px 14px; border-radius:8px; margin:4px 0; }
section[data-testid="stSidebar"] { background:#1F3864 !important; }
section[data-testid="stSidebar"] * { color:white !important; }
section[data-testid="stSidebar"] .stButton button { background:#2E5496 !important; border:none; }
#MainMenu,footer,.stDeployButton { visibility:hidden; }
div[data-testid="stToolbar"] { visibility:hidden; }
</style>
""", unsafe_allow_html=True)

# ══════════════════════════════════════════════
# المستخدمون والصلاحيات
# ══════════════════════════════════════════════
USERS = {
    "admin":  {"password": "Qitad@2026!",  "role": "admin",  "name": "المدير"},
    "editor": {"password": "Edit@Qitad1",  "role": "editor", "name": "المحرر"},
    "viewer": {"password": "View@Qitad1",  "role": "viewer", "name": "مشاهد"},
}
ROLES = {
    "admin":  {"label":"🔑 مدير",   "can_edit":True,  "can_add":True,  "can_delete":True},
    "editor": {"label":"✏️ محرر",  "can_edit":True,  "can_add":False, "can_delete":False},
    "viewer": {"label":"👁️ مشاهد","can_edit":False, "can_add":False, "can_delete":False},
}

# ══════════════════════════════════════════════
# قاعدة البيانات
# ══════════════════════════════════════════════
DATA_FILE = "data.json"

def empty_worker(wid, name="", iqama=""):
    return {
        "id": wid, "name": name, "iqama": iqama,
        # هل يملك رخصة مسبقاً؟
        "has_license_already": "",
        "existing_license_date": "",
        # التقييم
        "eval_date":"", "eval_time":"", "eval_hours":"", "eval_result":"",
        # تدريب نظري
        "train_n1_date":"", "train_n1_time":"",
        "train_n2_date":"", "train_n2_time":"",
        "train_n_attend":"",
        # اختبار نظري 3 محاولات
        "exam_n1_date":"", "exam_n1_time":"", "exam_n1_result":"",
        "exam_n2_date":"", "exam_n2_time":"", "exam_n2_result":"",
        "exam_n3_date":"", "exam_n3_time":"", "exam_n3_result":"",
        # تدريب عملي
        "train_e_date":"", "train_e_time":"", "train_e_attend":"",
        # اختبار عملي 3 محاولات
        "exam_e1_date":"", "exam_e1_time":"", "exam_e1_result":"",
        "exam_e2_date":"", "exam_e2_time":"", "exam_e2_result":"",
        "exam_e3_date":"", "exam_e3_time":"", "exam_e3_result":"",
        # رخصة
        "license_date":"",
        # أخرى
        "notes":"", "email":""
    }

DEFAULT_WORKERS = [
    ("MD TARIK","2626999490"),("MOHAMMAD JISAN","2626439638"),
    ("Reehan Akbar Akbar Ali","2626194373"),("Ali Haider Muhammad Yaqoob","2629185873"),
    ("MD Ashraful Islam","2629170594"),("MD Ataur Rahman","2629264801"),
    ("Hassan Muhammad Safdar","2625979436"),("MAHFUZ HASAN","2626329540"),
    ("Muhammad Mohsin Mia","2623235666"),("MD PARBEZ","2603872579"),
    ("MD YASIN ALI","2623438807"),("MD SOFIR","2603844130"),
    ("SOFIKUL LSLAM SAGOR","2604813549"),("MOHAMMAD MOYAJJAM","2618439299"),
    ("MD JANNATUL FERDUS","2624056053"),("MD ESRAFIL HOSSIN","2618285429"),
    ("MD FARIDUL ISLAM AKAS","2628410611"),("MUHAMMAD USMAN","2630584155"),
    ("MD TUHIN ALAM","2630931893"),("MD REZAUL HAQUE","2622553192"),
    ("MUHAMMAD ISTIKHAR","2612680542"),("AL MAMUN","2626177568"),
    ("JISSAN HOSSAN ASIF","2622185649"),("MD AULLE ULLHA","2629182979"),
]

def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE,'r',encoding='utf-8') as f:
            return json.load(f)
    workers = [empty_worker(i+1, n, iq) for i,(n,iq) in enumerate(DEFAULT_WORKERS)]
    return {"workers": workers, "company_note": "", "next_id": len(workers)+1}

def save_data(data):
    with open(DATA_FILE,'w',encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

# ══════════════════════════════════════════════
# دوال مساعدة
# ══════════════════════════════════════════════
def get_status(w):
    if w.get("has_license_already") == "نعم": return "✅ يملك رخصة مسبقاً"
    if w.get("license_date"): return "✅ أصدر رخصة"
    if any(w.get(f"exam_e{i}_result")=="ناجح" for i in range(1,4)): return "✅ اكتمل العملي"
    if any(w.get(f) for f in ["exam_e1_date","train_e_date"]): return "🔄 مرحلة العملي"
    if any(w.get(f"exam_n{i}_result")=="ناجح" for i in range(1,4)): return "✅ اكتمل النظري"
    if any(w.get(f) for f in ["exam_n1_date","train_n1_date"]): return "🔄 مرحلة النظري"
    if w.get("eval_date"): return "🔄 التقييم"
    return "⛔ لم يبدأ"

def get_fail_n(w): return sum(1 for i in range(1,4) if w.get(f"exam_n{i}_result")=="راسب")
def get_fail_e(w): return sum(1 for i in range(1,4) if w.get(f"exam_e{i}_result")=="راسب")

def get_stagnant(w):
    dates = []
    for k in ["eval_date","train_n1_date","exam_n1_date","train_e_date","exam_e1_date","license_date"]:
        v = w.get(k,"")
        if v:
            try: dates.append(datetime.strptime(v,"%Y-%m-%d").date())
            except: pass
    if not dates: return None
    return (date.today()-max(dates)).days

def parse_date(s):
    if not s: return None
    try: return datetime.strptime(s,"%Y-%m-%d").date()
    except: return None

def fmt_date(d):
    return d.strftime("%Y-%m-%d") if d else ""

def get_appointments(workers):
    today = date.today()
    appt_fields = [
        ("train_n1_date","train_n1_time","تدريب نظري 1"),
        ("train_n2_date","train_n2_time","تدريب نظري 2"),
        ("exam_n1_date","exam_n1_time","اختبار نظري 1"),
        ("exam_n2_date","exam_n2_time","اختبار نظري 2"),
        ("exam_n3_date","exam_n3_time","اختبار نظري 3"),
        ("train_e_date","train_e_time","تدريب عملي"),
        ("exam_e1_date","exam_e1_time","اختبار عملي 1"),
        ("exam_e2_date","exam_e2_time","اختبار عملي 2"),
        ("exam_e3_date","exam_e3_time","اختبار عملي 3"),
    ]
    appts = []
    for w in workers:
        for dk,tk,name in appt_fields:
            d = parse_date(w.get(dk,""))
            if d:
                diff = (d-today).days
                if -30 <= diff <= 14:
                    if diff<0: status="🔴 فات الموعد"
                    elif diff==0: status="🔴 اليوم!"
                    elif diff==1: status="🟠 غداً"
                    elif diff<=3: status="⚠️ قريب"
                    else: status="✅ الأسبوعان"
                    appts.append({"name":w["name"],"iqama":w["iqama"],
                        "type":name,"date":d,"time":w.get(tk,"--") or "--",
                        "status":status,"diff":diff})
    return sorted(appts, key=lambda x: x["date"])

STATUS_COLORS = {
    "✅ أصدر رخصة":"#1E7145","🔄 مرحلة النظري":"#2E5496",
    "🔄 مرحلة العملي":"#00695C","✅ اكتمل النظري":"#4472C4",
    "✅ اكتمل العملي":"#1E7145","🔄 التقييم":"#7030A0","⛔ لم يبدأ":"#404040"
}

# ══════════════════════════════════════════════
# صفحة تسجيل الدخول
# ══════════════════════════════════════════════
def login_page():
    col1,col2,col3 = st.columns([1,1.2,1])
    with col2:
        st.markdown("<br><br>", unsafe_allow_html=True)
        st.markdown("""
        <div style="text-align:center;margin-bottom:20px;">
            <div style="font-size:64px;">🪪</div>
            <h2 style="color:#1F3864;font-weight:800;margin:0;">نظام متابعة مراحل الرخصة</h2>
            <p style="color:#666;margin:5px 0;">قتاد اللوجستية</p>
        </div>""", unsafe_allow_html=True)

        with st.form("login"):
            username = st.text_input("👤 اسم المستخدم")
            password = st.text_input("🔒 كلمة المرور", type="password")
            submitted = st.form_submit_button("دخول ←", use_container_width=True, type="primary")
            if submitted:
                if username in USERS and USERS[username]["password"] == password:
                    st.session_state.logged_in = True
                    st.session_state.user = USERS[username]
                    st.session_state.username = username
                    st.rerun()
                else:
                    st.error("❌ اسم المستخدم أو كلمة المرور غير صحيحة")

# ══════════════════════════════════════════════
# نموذج تعديل/إضافة عامل
# ══════════════════════════════════════════════
def worker_form(w, key_prefix=""):
    """نموذج إدخال كامل لبيانات العامل — كل الحقول مثل Excel"""
    
    RES_OPTS   = ["","ناجح","راسب","غائب","لم يتم الحجز"]
    ATTEND_OPTS= ["","حضر","غائب","مؤجل"]
    HOURS_OPTS = ["","6 ساعات","15 ساعة","30 ساعة"]

    def sel_idx(opts, val):
        return opts.index(val) if val in opts else 0

    # معلومات أساسية
    st.markdown("#### 👤 معلومات العامل")
    c1,c2 = st.columns(2)
    w["name"]  = c1.text_input("الاسم الكامل *", value=w.get("name",""), key=f"{key_prefix}_name")
    w["iqama"] = c2.text_input("رقم الإقامة *", value=w.get("iqama",""), key=f"{key_prefix}_iqama")
    w["email"] = c1.text_input("📧 الإيميل", value=w.get("email",""), key=f"{key_prefix}_email")

    st.markdown("---")
    tabs = st.tabs(["⓪ الرخصة المسبقة","① التقييم","② تدريب نظري","③ اختبار نظري","④ تدريب عملي","⑤ اختبار عملي","⑥ الرخصة","📝 ملاحظات"])

    # ── الرخصة المسبقة
    with tabs[0]:
        st.markdown("**هل يملك العامل رخصة قيادة مسبقاً؟**")
        has_lic = st.radio(
            "الحالة",
            ["لا يملك رخصة", "نعم — يملك رخصة مسبقاً"],
            index=1 if w.get("has_license_already")=="نعم" else 0,
            key=f"{key_prefix}_hl",
            horizontal=True
        )
        w["has_license_already"] = "نعم" if "نعم" in has_lic else ""

        if w["has_license_already"] == "نعم":
            st.success("✅ هذا العامل يملك رخصة مسبقاً — لا يحتاج لاجتياز المراحل")
            c1,c2 = st.columns(2)
            d = c1.date_input("تاريخ الرخصة المسبقة", value=parse_date(w.get("existing_license_date")), key=f"{key_prefix}_eld")
            w["existing_license_date"] = fmt_date(d)
            c2.info("سيظهر في المؤشرات كـ ✅ يملك رخصة مسبقاً")
        else:
            st.info("ℹ️ سيمر العامل بكل مراحل التقييم والتدريب والاختبار")

    # ── التقييم
    with tabs[2]:
        st.markdown("**بيانات التقييم**")
        c1,c2,c3,c4 = st.columns(4)
        d = c1.date_input("تاريخ التقييم", value=parse_date(w.get("eval_date")), key=f"{key_prefix}_ed")
        w["eval_date"] = fmt_date(d)
        w["eval_time"]   = c2.text_input("وقت التقييم", value=w.get("eval_time",""), placeholder="مثال: 10:00", key=f"{key_prefix}_et")
        w["eval_hours"]  = c3.selectbox("ساعات التقييم", HOURS_OPTS, index=sel_idx(HOURS_OPTS,w.get("eval_hours","")), key=f"{key_prefix}_eh")
        w["eval_result"] = c4.selectbox("نتيجة التقييم", RES_OPTS, index=sel_idx(RES_OPTS,w.get("eval_result","")), key=f"{key_prefix}_er")

    # ── تدريب نظري
    with tabs[2]:
        st.markdown("**التدريب النظري — موعدان**")
        c1,c2 = st.columns(2)
        with c1:
            st.markdown("**موعد 1**")
            d = st.date_input("التاريخ", value=parse_date(w.get("train_n1_date")), key=f"{key_prefix}_tn1d")
            w["train_n1_date"] = fmt_date(d)
            w["train_n1_time"] = st.text_input("الوقت", value=w.get("train_n1_time",""), placeholder="مثال: 09:00", key=f"{key_prefix}_tn1t")
        with c2:
            st.markdown("**موعد 2**")
            d = st.date_input("التاريخ", value=parse_date(w.get("train_n2_date")), key=f"{key_prefix}_tn2d")
            w["train_n2_date"] = fmt_date(d)
            w["train_n2_time"] = st.text_input("الوقت", value=w.get("train_n2_time",""), placeholder="مثال: 09:00", key=f"{key_prefix}_tn2t")
        w["train_n_attend"] = st.selectbox("الحضور", ATTEND_OPTS, index=sel_idx(ATTEND_OPTS,w.get("train_n_attend","")), key=f"{key_prefix}_tna")

    # ── اختبار نظري
    with tabs[3]:
        st.markdown("**اختبار نظري — 3 محاولات**")
        for i in range(1,4):
            with st.expander(f"محاولة {i}", expanded=(i==1)):
                c1,c2,c3 = st.columns(3)
                d = c1.date_input("التاريخ", value=parse_date(w.get(f"exam_n{i}_date")), key=f"{key_prefix}_en{i}d")
                w[f"exam_n{i}_date"] = fmt_date(d)
                w[f"exam_n{i}_time"]   = c2.text_input("الوقت", value=w.get(f"exam_n{i}_time",""), placeholder="مثال: 10:00", key=f"{key_prefix}_en{i}t")
                w[f"exam_n{i}_result"] = c3.selectbox("النتيجة", RES_OPTS, index=sel_idx(RES_OPTS,w.get(f"exam_n{i}_result","")), key=f"{key_prefix}_en{i}r")

    # ── تدريب عملي
    with tabs[4]:
        st.markdown("**التدريب العملي — موعد واحد**")
        c1,c2,c3 = st.columns(3)
        d = c1.date_input("التاريخ", value=parse_date(w.get("train_e_date")), key=f"{key_prefix}_ted")
        w["train_e_date"]   = fmt_date(d)
        w["train_e_time"]   = c2.text_input("الوقت", value=w.get("train_e_time",""), placeholder="مثال: 14:00", key=f"{key_prefix}_tet")
        w["train_e_attend"] = c3.selectbox("الحضور", ATTEND_OPTS, index=sel_idx(ATTEND_OPTS,w.get("train_e_attend","")), key=f"{key_prefix}_tea")

    # ── اختبار عملي
    with tabs[5]:
        st.markdown("**اختبار عملي — 3 محاولات**")
        for i in range(1,4):
            with st.expander(f"محاولة {i}", expanded=(i==1)):
                c1,c2,c3 = st.columns(3)
                d = c1.date_input("التاريخ", value=parse_date(w.get(f"exam_e{i}_date")), key=f"{key_prefix}_ee{i}d")
                w[f"exam_e{i}_date"] = fmt_date(d)
                w[f"exam_e{i}_time"]   = c2.text_input("الوقت", value=w.get(f"exam_e{i}_time",""), placeholder="مثال: 10:00", key=f"{key_prefix}_ee{i}t")
                w[f"exam_e{i}_result"] = c3.selectbox("النتيجة", RES_OPTS, index=sel_idx(RES_OPTS,w.get(f"exam_e{i}_result","")), key=f"{key_prefix}_ee{i}r")

    # ── الرخصة
    with tabs[6]:
        st.markdown("**إصدار الرخصة**")
        d = st.date_input("تاريخ إصدار الرخصة", value=parse_date(w.get("license_date")), key=f"{key_prefix}_ld")
        w["license_date"] = fmt_date(d)
        st.info(f"الحالة الحالية: **{get_status(w)}**")

    # ── ملاحظات
    with tabs[7]:
        w["notes"] = st.text_area("ملاحظات", value=w.get("notes",""), height=120, key=f"{key_prefix}_notes")

    return w

# ══════════════════════════════════════════════
# الصفحات
# ══════════════════════════════════════════════
def dashboard_page(data, role):
    workers = data["workers"]
    today = date.today()

    total     = len([w for w in workers if w["name"]])
    licensed  = len([w for w in workers if w.get("license_date")])
    in_prog   = len([w for w in workers if "🔄" in get_status(w)])
    not_start = len([w for w in workers if get_status(w)=="⛔ لم يبدأ"])
    evaluated = len([w for w in workers if w.get("eval_date")])
    fail_n    = sum(get_fail_n(w) for w in workers)
    fail_e    = sum(get_fail_e(w) for w in workers)
    appts     = get_appointments(workers)
    today_ap  = [a for a in appts if a["diff"]==0]
    pct = round(licensed/max(1,total)*100)

    if data.get("company_note"):
        st.info(f"📢 {data['company_note']}")

    # KPI Row 1
    cols = st.columns(4)
    for col,(val,lbl,color) in zip(cols,[
        (total,"👷 إجمالي العمال","#1F3864"),
        (evaluated,"📋 المُقيَّمون","#7030A0"),
        (licensed,"✅ أصدر رخصة","#1E7145"),
        (in_prog,"🔄 قيد التنفيذ","#2E5496"),
    ]):
        col.markdown(f'<div class="kpi-card" style="border-top-color:{color};"><div class="val" style="color:{color};">{val}</div><div class="lbl">{lbl}</div></div>', unsafe_allow_html=True)

    # KPI Row 2
    cols2 = st.columns(4)
    for col,(val,lbl,color) in zip(cols2,[
        (not_start,"⛔ لم يبدأ","#404040"),
        (fail_n,"⚠️ رسوب نظري","#C55A11"),
        (len(today_ap),"📅 موعد اليوم","#00695C"),
        (f"{pct}%","📈 نسبة الإنجاز","#7030A0"),
    ]):
        col.markdown(f'<div class="kpi-card" style="border-top-color:{color};"><div class="val" style="color:{color};">{val}</div><div class="lbl">{lbl}</div></div>', unsafe_allow_html=True)

    st.markdown("---")
    col_l, col_r = st.columns([1.5,1])

    with col_l:
        st.markdown("### 📅 مواعيد اليوم")
        if today_ap:
            for a in today_ap:
                st.markdown(f'<div class="alert-r"><strong>🔴 {a["name"]}</strong> — {a["type"]} &nbsp; ⏰ {a["time"]}</div>', unsafe_allow_html=True)
        else:
            st.markdown('<div class="alert-g">✅ لا توجد مواعيد اليوم</div>', unsafe_allow_html=True)

        soon = [a for a in appts if 0<a["diff"]<=3]
        if soon:
            st.markdown("### ⚠️ مواعيد قريبة")
            for a in soon[:5]:
                days_txt = "غداً" if a["diff"]==1 else f"بعد {a['diff']} أيام"
                st.markdown(f'<div class="alert-o"><strong>{a["name"]}</strong> — {a["type"]} | 📅 {a["date"]} ({days_txt})</div>', unsafe_allow_html=True)

    with col_r:
        st.markdown("### 📊 توزيع المراحل")
        stage_counts = {}
        for w in workers:
            s = get_status(w)
            stage_counts[s] = stage_counts.get(s,0)+1
        for stage,count in stage_counts.items():
            pct_s = round(count/max(1,total)*100)
            color = STATUS_COLORS.get(stage,"#666")
            bar = "█"*round(pct_s/5)+"░"*(20-round(pct_s/5))
            st.markdown(f'<div style="margin:5px 0;display:flex;align-items:center;gap:8px;"><span style="min-width:170px;font-size:13px;font-weight:600;">{stage}</span><span style="color:{color};font-family:monospace;font-size:10px;">{bar}</span><span style="font-weight:700;color:{color};">{count}</span></div>', unsafe_allow_html=True)

def tracking_page(data, role):
    workers = data["workers"]
    can_edit = ROLES[role]["can_edit"]
    can_add  = ROLES[role]["can_add"]
    can_del  = ROLES[role]["can_delete"]

    st.markdown("### 📋 متابعة مراحل الرخصة")

    # ── إضافة عامل جديد (المدير فقط)
    if can_add:
        with st.expander("➕ إضافة عامل جديد", expanded=False):
            next_id = data.get("next_id", len(workers)+1)
            new_w = empty_worker(next_id)
            new_w = worker_form(new_w, key_prefix="new")
            if st.button("✅ إضافة العامل", type="primary"):
                if not new_w["name"]:
                    st.error("❌ يرجى إدخال اسم العامل")
                else:
                    new_w["id"] = next_id
                    workers.append(new_w)
                    data["workers"] = workers
                    data["next_id"] = next_id + 1
                    save_data(data)
                    st.success(f"✅ تم إضافة {new_w['name']}")
                    st.rerun()

    st.markdown("---")

    # ── فلترة وبحث
    c1,c2,c3 = st.columns([2,1.2,1])
    search = c1.text_input("🔍 بحث بالاسم أو رقم الإقامة", placeholder="اكتب للبحث...")
    filter_status = c2.selectbox("فلتر الحالة", ["الكل","⛔ لم يبدأ","🔄 التقييم",
        "🔄 مرحلة النظري","✅ اكتمل النظري","🔄 مرحلة العملي","✅ اكتمل العملي","✅ أصدر رخصة"])
    filter_fail = c3.checkbox("الراسبون فقط")

    filtered = [w for w in workers if
        (not search or search.lower() in w["name"].lower() or search in w.get("iqama","")) and
        (filter_status=="الكل" or get_status(w)==filter_status) and
        (not filter_fail or get_fail_n(w)>0 or get_fail_e(w)>0)
    ]
    st.caption(f"عرض {len(filtered)} من {len(workers)} عامل")

    # ── جدول ملخص
    rows = ""
    for w in filtered:
        status = get_status(w)
        color  = STATUS_COLORS.get(status,"#666")
        fn,fe  = get_fail_n(w), get_fail_e(w)
        stag   = get_stagnant(w)
        stag_str   = f"{stag} يوم" if isinstance(stag,int) else "لم يبدأ"
        stag_color = "#C00000" if isinstance(stag,int) and stag>30 else "#C55A11" if isinstance(stag,int) and stag>15 else "#404040"
        fail_n_str = f'<span style="color:#C00000;font-weight:700;">{fn}</span>' if fn>0 else "—"
        fail_e_str = f'<span style="color:#C00000;font-weight:700;">{fe}</span>' if fe>0 else "—"
        rows += f"""<tr>
            <td style="font-weight:700;color:#1F3864;">{w['id']}</td>
            <td style="text-align:right;font-weight:600;">{w['name']}</td>
            <td>{w.get('iqama','')}</td>
            <td><span style="background:{color}22;color:{color};padding:3px 10px;border-radius:12px;font-size:12px;font-weight:700;">{status}</span></td>
            <td>{fail_n_str}</td><td>{fail_e_str}</td>
            <td style="color:{stag_color};font-weight:600;">{stag_str}</td>
        </tr>"""

    st.markdown(f"""<table class="styled-table"><thead><tr>
        <th>#</th><th>الاسم</th><th>الإقامة</th><th>الحالة</th>
        <th>رسوب نظري</th><th>رسوب عملي</th><th>أيام التعطل</th>
    </tr></thead><tbody>{rows}</tbody></table>""", unsafe_allow_html=True)

    # ── تعديل عامل
    if can_edit:
        st.markdown("---")
        st.markdown("### ✏️ تعديل بيانات عامل")
        names = [f"{w['id']}. {w['name']}" for w in workers]
        sel = st.selectbox("اختر العامل للتعديل", names)
        idx = int(sel.split(".")[0]) - 1
        # البحث بالـ ID
        w_idx = next((i for i,w in enumerate(workers) if w["id"]==idx+1), 0)
        w = dict(workers[w_idx])

        with st.expander(f"📝 بيانات: {w['name']}", expanded=True):
            w = worker_form(w, key_prefix=f"edit_{w['id']}")

            cols_btn = st.columns([1,1,3])
            if cols_btn[0].button("💾 حفظ التعديلات", type="primary"):
                workers[w_idx] = w
                data["workers"] = workers
                save_data(data)
                st.success("✅ تم الحفظ!")
                st.rerun()

            # حذف (المدير فقط)
            if can_del:
                if cols_btn[1].button("🗑️ حذف العامل", type="secondary"):
                    if st.session_state.get("confirm_delete") == w["id"]:
                        workers.pop(w_idx)
                        data["workers"] = workers
                        save_data(data)
                        st.success("✅ تم الحذف")
                        st.session_state.confirm_delete = None
                        st.rerun()
                    else:
                        st.session_state.confirm_delete = w["id"]
                        st.warning("⚠️ اضغط مرة أخرى للتأكيد")

def schedule_page(data):
    workers = data["workers"]
    appts = get_appointments(workers)
    today = date.today()

    st.markdown("### 📅 مواعيد الأسبوعين")

    c1,c2,c3,c4 = st.columns(4)
    c1.metric("🔴 اليوم", len([a for a in appts if a["diff"]==0]))
    c2.metric("📅 الأسبوعان (قادم)", len([a for a in appts if 0<=a["diff"]<=14]))
    c3.metric("🔴 فات موعده", len([a for a in appts if a["diff"]<0]))
    c4.metric("📆 اليوم", today.strftime("%Y/%m/%d"))

    st.markdown("---")

    if not appts:
        st.info("لا توجد مواعيد في هذه الفترة")
        return

    type_colors = {
        "تدريب نظري 1":"#1565C0","تدريب نظري 2":"#1565C0",
        "اختبار نظري 1":"#7030A0","اختبار نظري 2":"#7030A0","اختبار نظري 3":"#7030A0",
        "تدريب عملي":"#00695C",
        "اختبار عملي 1":"#1E7145","اختبار عملي 2":"#1E7145","اختبار عملي 3":"#1E7145",
    }
    status_colors = {
        "🔴 اليوم!":      ("#FDECEA","#C00000"),
        "🔴 فات الموعد":  ("#FDECEA","#C00000"),
        "🟠 غداً":        ("#FCE4D6","#C55A11"),
        "⚠️ قريب":       ("#FFF2CC","#BF8F00"),
        "✅ الأسبوعان":   ("#E2EFDA","#1E7145"),
    }
    days_ar = ["الاثنين","الثلاثاء","الأربعاء","الخميس","الجمعة","السبت","الأحد"]

    rows = ""
    for a in appts:
        bg,fg = status_colors.get(a["status"],("#F2F2F2","#404040"))
        tc = type_colors.get(a["type"],"#404040")
        day_ar = days_ar[a["date"].weekday()]
        diff_str = f"اليوم" if a["diff"]==0 else f"{a['diff']:+d} يوم"
        rows += f"""<tr>
            <td style="text-align:right;font-weight:600;">{a['name']}</td>
            <td><span style="background:{tc}22;color:{tc};padding:3px 8px;border-radius:10px;font-size:11px;font-weight:700;">{a['type']}</span></td>
            <td style="font-weight:600;">{a['date'].strftime('%Y/%m/%d')}</td>
            <td style="color:#7030A0;font-weight:700;">{a['time']}</td>
            <td>{day_ar} ({diff_str})</td>
            <td><span style="background:{bg};color:{fg};padding:3px 10px;border-radius:10px;font-size:11px;font-weight:700;">{a['status']}</span></td>
        </tr>"""

    st.markdown(f"""<table class="styled-table"><thead><tr>
        <th>اسم العامل</th><th>نوع الموعد</th><th>التاريخ</th>
        <th>الوقت</th><th>اليوم</th><th>الحالة</th>
    </tr></thead><tbody>{rows}</tbody></table>""", unsafe_allow_html=True)

def indicators_page(data):
    workers = data["workers"]
    total    = len([w for w in workers if w["name"]])
    licensed = len([w for w in workers if w.get("license_date")])
    fail_n   = sum(get_fail_n(w) for w in workers)
    fail_e   = sum(get_fail_e(w) for w in workers)
    stagnant = [w for w in workers if isinstance(get_stagnant(w),int) and get_stagnant(w)>30]

    all_n = [w.get(f"exam_n{i}_result","") for w in workers for i in range(1,4) if w.get(f"exam_n{i}_result") in ["ناجح","راسب"]]
    all_e = [w.get(f"exam_e{i}_result","") for w in workers for i in range(1,4) if w.get(f"exam_e{i}_result") in ["ناجح","راسب"]]
    pass_n = round(all_n.count("ناجح")/max(1,len(all_n))*100) if all_n else 0
    pass_e = round(all_e.count("ناجح")/max(1,len(all_e))*100) if all_e else 0

    st.markdown("### 📊 المؤشرات الشاملة")
    c1,c2,c3,c4 = st.columns(4)
    c1.metric("✅ نجاح النظري",f"{pass_n}%")
    c2.metric("✅ نجاح العملي",f"{pass_e}%")
    c3.metric("❌ رسوب النظري",f"{100-pass_n}%" if all_n else "—")
    c4.metric("😴 معطل +30 يوم",len(stagnant))

    st.markdown("---")
    col1,col2 = st.columns(2)

    with col1:
        st.markdown("#### 📊 توزيع المراحل")
        stage_data = {}
        for w in workers:
            s = get_status(w); stage_data[s] = stage_data.get(s,0)+1
        for stage,count in stage_data.items():
            pct_s = round(count/max(1,total)*100)
            st.markdown(f"**{stage}** — {count} ({pct_s}%)")
            st.progress(pct_s/100)

        st.markdown("#### 📈 إحصائيات الاختبارات")
        c1,c2,c3 = st.columns(3)
        c1.metric("ناجح نظري", all_n.count("ناجح"))
        c2.metric("راسب نظري", all_n.count("راسب"))
        c3.metric("غائب نظري", sum(1 for w in workers for i in range(1,4) if w.get(f"exam_n{i}_result")=="غائب"))

    with col2:
        st.markdown("#### 😴 العمال الجامدون (+30 يوم)")
        if stagnant:
            for w in stagnant:
                st.markdown(f'<div class="alert-r"><strong>{w["name"]}</strong> — {get_stagnant(w)} يوم<br><small>{get_status(w)}</small></div>', unsafe_allow_html=True)
        else:
            st.markdown('<div class="alert-g">✅ لا يوجد عمال جامدون</div>', unsafe_allow_html=True)

        st.markdown("#### 🚨 الراسبون في الاختبار")
        failed = [w for w in workers if get_fail_n(w)>0 or get_fail_e(w)>0]
        if failed:
            for w in failed:
                fn,fe = get_fail_n(w),get_fail_e(w)
                parts = []
                if fn: parts.append(f"رسوب نظري: {fn}")
                if fe: parts.append(f"رسوب عملي: {fe}")
                st.markdown(f'<div class="alert-r"><strong>{w["name"]}</strong> — {" | ".join(parts)}</div>', unsafe_allow_html=True)
        else:
            st.markdown('<div class="alert-g">✅ لا يوجد راسبون</div>', unsafe_allow_html=True)

def search_page(data):
    workers = data["workers"]
    st.markdown("### 🔍 البحث السريع")

    c1,c2 = st.columns(2)
    search_name = c1.text_input("🔍 بحث بالاسم", placeholder="اكتب اسم العامل...")
    search_iq   = c2.text_input("🔍 بحث برقم الإقامة", placeholder="اكتب رقم الإقامة...")

    results = [w for w in workers if
        (search_name and search_name.lower() in w["name"].lower()) or
        (search_iq and search_iq in w.get("iqama","")) or
        (not search_name and not search_iq)
    ]

    if not search_name and not search_iq:
        st.info("اكتب في أحد حقول البحث لعرض النتائج")
        return

    if not results:
        st.warning("لم يُعثر على نتائج")
        return

    for w in results:
        status = get_status(w)
        color  = STATUS_COLORS.get(status,"#666")
        fn,fe  = get_fail_n(w), get_fail_e(w)
        stag   = get_stagnant(w)
        appts  = get_appointments([w])
        with st.expander(f"👤 {w['name']} — {w.get('iqama','')}", expanded=True):
            c1,c2,c3,c4 = st.columns(4)
            c1.markdown(f'<span style="background:{color}22;color:{color};padding:5px 12px;border-radius:12px;font-weight:700;">{status}</span>', unsafe_allow_html=True)
            c2.metric("رسوب نظري", fn)
            c3.metric("رسوب عملي", fe)
            c4.metric("أيام التعطل", stag if isinstance(stag,int) else "لم يبدأ")
            if w.get("notes"):
                st.info(f"📝 {w['notes']}")
            if appts:
                st.markdown("**📅 مواعيده القريبة:**")
                for a in appts[:3]:
                    st.markdown(f"- {a['type']} | {a['date']} | {a['status']}")

# ══════════════════════════════════════════════
# البرنامج الرئيسي
# ══════════════════════════════════════════════
def main():
    if "logged_in" not in st.session_state:
        st.session_state.logged_in = False

    if not st.session_state.logged_in:
        login_page()
        return

    user = st.session_state.user
    role = user["role"]
    data = load_data()

    with st.sidebar:
        st.markdown(f"""
        <div style="text-align:center;padding:15px 0;">
            <div style="font-size:40px;">🪪</div>
            <h3 style="color:white;margin:5px 0;">قتاد اللوجستية</h3>
            <div style="background:#2E5496;padding:6px 12px;border-radius:8px;margin:8px 0;">
                <span style="font-size:13px;">{ROLES[role]['label']}: {user['name']}</span>
            </div>
            <small style="color:#FFFFFF88;">آخر تحديث: {datetime.now().strftime('%H:%M')}</small>
        </div>""", unsafe_allow_html=True)

        st.markdown("---")
        pages = ["🏠 الرئيسية","📋 المتابعة","📅 المواعيد","📊 المؤشرات","🔍 البحث"]
        page = st.radio("", pages, label_visibility="hidden")

        # ملاحظات الشركة (المحرر والمدير)
        if ROLES[role]["can_edit"]:
            st.markdown("---")
            note = st.text_area("📢 ملاحظات الشركة", value=data.get("company_note",""), key="cn", height=80)
            if st.button("💾 حفظ الملاحظة", use_container_width=True):
                data["company_note"] = note
                save_data(data)
                st.success("✅")

        st.markdown("---")
        if st.button("🚪 تسجيل الخروج", use_container_width=True):
            for key in ["logged_in","user","username"]:
                st.session_state.pop(key, None)
            st.rerun()

    if page   == "🏠 الرئيسية": dashboard_page(data, role)
    elif page == "📋 المتابعة":  tracking_page(data, role)
    elif page == "📅 المواعيد":  schedule_page(data)
    elif page == "📊 المؤشرات": indicators_page(data)
    elif page == "🔍 البحث":    search_page(data)

if __name__ == "__main__":
    main()
