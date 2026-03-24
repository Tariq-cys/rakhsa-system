import streamlit as st
import pandas as pd
from datetime import datetime, date, timedelta
import json
import os

# ══════════════════════════════════════════════
# إعدادات الصفحة
# ══════════════════════════════════════════════
st.set_page_config(
    page_title="نظام متابعة الرخصة | قتاد اللوجستية",
    page_icon="🪪",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ══════════════════════════════════════════════
# CSS مخصص - RTL + تصميم احترافي
# ══════════════════════════════════════════════
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Tajawal:wght@400;500;700;800&display=swap');
    
    * { font-family: 'Tajawal', sans-serif !important; direction: rtl; }
    
    .main { background: #F2F5FA; }
    
    .stApp { direction: rtl; }
    
    /* Header */
    .main-header {
        background: linear-gradient(135deg, #1F3864 0%, #2E5496 100%);
        color: #BF8F00;
        padding: 20px 30px;
        border-radius: 12px;
        text-align: center;
        margin-bottom: 20px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.2);
    }
    .main-header h1 { color: #BF8F00; font-size: 28px; margin: 0; font-weight: 800; }
    .main-header p  { color: #FFFFFF99; margin: 5px 0 0; font-size: 14px; }
    
    /* KPI Cards */
    .kpi-card {
        background: white;
        border-radius: 12px;
        padding: 20px;
        text-align: center;
        box-shadow: 0 2px 10px rgba(0,0,0,0.08);
        border-top: 4px solid;
        margin-bottom: 10px;
    }
    .kpi-card .kpi-value { font-size: 42px; font-weight: 800; line-height: 1; }
    .kpi-card .kpi-label { font-size: 13px; color: #666; margin-top: 5px; font-weight: 600; }
    
    /* Status badges */
    .badge {
        display: inline-block;
        padding: 3px 10px;
        border-radius: 20px;
        font-size: 12px;
        font-weight: 700;
    }
    .badge-green  { background: #E2EFDA; color: #1E7145; }
    .badge-blue   { background: #EBF3FF; color: #1565C0; }
    .badge-red    { background: #FDECEA; color: #C00000; }
    .badge-orange { background: #FCE4D6; color: #C55A11; }
    .badge-gray   { background: #F2F2F2; color: #404040; }
    .badge-purple { background: #EAE0F2; color: #7030A0; }
    
    /* Tables */
    .styled-table {
        width: 100%;
        border-collapse: collapse;
        background: white;
        border-radius: 10px;
        overflow: hidden;
        box-shadow: 0 2px 8px rgba(0,0,0,0.06);
        font-size: 13px;
    }
    .styled-table th {
        background: #1F3864;
        color: white;
        padding: 10px 12px;
        text-align: center;
        font-weight: 700;
    }
    .styled-table td {
        padding: 9px 12px;
        border-bottom: 1px solid #F0F0F0;
        text-align: center;
    }
    .styled-table tr:nth-child(even) { background: #F8FAFC; }
    .styled-table tr:hover { background: #EBF3FF; }
    
    /* Sidebar */
    section[data-testid="stSidebar"] {
        background: #1F3864 !important;
    }
    section[data-testid="stSidebar"] * { color: white !important; }
    
    /* Login */
    .login-box {
        max-width: 400px;
        margin: 80px auto;
        background: white;
        padding: 40px;
        border-radius: 16px;
        box-shadow: 0 8px 30px rgba(0,0,0,0.12);
        text-align: center;
    }
    
    /* Alert boxes */
    .alert-today { background: #FDECEA; border-right: 4px solid #C00000; padding: 12px; border-radius: 8px; margin: 5px 0; }
    .alert-soon  { background: #FFF2CC; border-right: 4px solid #BF8F00; padding: 12px; border-radius: 8px; margin: 5px 0; }
    .alert-ok    { background: #E2EFDA; border-right: 4px solid #1E7145; padding: 12px; border-radius: 8px; margin: 5px 0; }
    
    /* Hide streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    .stDeployButton {display:none;}
</style>
""", unsafe_allow_html=True)

# ══════════════════════════════════════════════
# نظام المصادقة والصلاحيات
# ══════════════════════════════════════════════
USERS = {
    "admin":   {"password": "admin123",  "role": "admin",   "name": "المدير"},
    "editor":  {"password": "edit123",   "role": "editor",  "name": "المحرر"},
    "viewer":  {"password": "view123",   "role": "viewer",  "name": "مشاهد"},
}

ROLES = {
    "admin":  {"label": "🔑 مدير",    "color": "#1E7145", "can_edit": True,  "can_delete": True},
    "editor": {"label": "✏️ محرر",   "color": "#1565C0", "can_edit": True,  "can_delete": False},
    "viewer": {"label": "👁️ مشاهد", "color": "#404040", "can_edit": False, "can_delete": False},
}

# ══════════════════════════════════════════════
# قاعدة البيانات (ملف JSON محلي)
# ══════════════════════════════════════════════
DATA_FILE = "data.json"

WORKERS_DEFAULT = [
    "MD TARIK", "MOHAMMAD JISAN", "Reehan Akbar Akbar Ali",
    "Ali Haider Muhammad Yaqoob", "MD Ashraful Islam", "MD Ataur Rahman",
    "Hassan Muhammad Safdar", "MAHFUZ HASAN", "Muhammad Mohsin Mia",
    "MD PARBEZ", "MD YASIN ALI", "MD SOFIR", "SOFIKUL LSLAM SAGOR",
    "MOHAMMAD MOYAJJAM", "MD JANNATUL FERDUS", "MD ESRAFIL HOSSIN",
    "MD FARIDUL ISLAM AKAS", "MUHAMMAD USMAN", "MD TUHIN ALAM",
    "MD REZAUL HAQUE", "MUHAMMAD ISTIKHAR", "AL MAMUN",
    "JISSAN HOSSAN ASIF", "MD AULLE ULLHA"
]
IQAMA_DEFAULT = [
    "2626999490","2626439638","2626194373","2629185873","2629170594",
    "2629264801","2625979436","2626329540","2623235666","2603872579",
    "2623438807","2603844130","2604813549","2618439299","2624056053",
    "2618285429","2628410611","2630584155","2630931893","2622553192",
    "2612680542","2626177568","2622185649","2629182979"
]

def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    # بيانات افتراضية
    workers = []
    for i, (name, iqama) in enumerate(zip(WORKERS_DEFAULT, IQAMA_DEFAULT)):
        workers.append({
            "id": i+1, "name": name, "iqama": iqama,
            "eval_date": "", "eval_time": "", "eval_hours": "", "eval_result": "",
            "train_n1_date": "", "train_n1_time": "",
            "train_n2_date": "", "train_n2_time": "",
            "train_n_attend": "",
            "exam_n1_date": "", "exam_n1_time": "", "exam_n1_result": "",
            "exam_n2_date": "", "exam_n2_time": "", "exam_n2_result": "",
            "exam_n3_date": "", "exam_n3_time": "", "exam_n3_result": "",
            "train_e_date": "", "train_e_time": "", "train_e_attend": "",
            "exam_e1_date": "", "exam_e1_time": "", "exam_e1_result": "",
            "exam_e2_date": "", "exam_e2_time": "", "exam_e2_result": "",
            "exam_e3_date": "", "exam_e3_time": "", "exam_e3_result": "",
            "license_date": "", "notes": "", "email": ""
        })
    return {"workers": workers, "company_note": ""}

def save_data(data):
    with open(DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def get_status(w):
    if w.get("license_date"): return "✅ أصدر رخصة"
    e_results = [w.get("exam_e1_result",""), w.get("exam_e2_result",""), w.get("exam_e3_result","")]
    if "ناجح" in e_results: return "✅ اكتمل العملي"
    if w.get("exam_e1_date") or w.get("train_e_date"): return "🔄 مرحلة العملي"
    n_results = [w.get("exam_n1_result",""), w.get("exam_n2_result",""), w.get("exam_n3_result","")]
    if "ناجح" in n_results: return "✅ اكتمل النظري"
    if w.get("exam_n1_date") or w.get("train_n1_date"): return "🔄 مرحلة النظري"
    if w.get("eval_date"): return "🔄 التقييم"
    return "⛔ لم يبدأ"

def get_fail_n(w):
    return sum(1 for r in [w.get("exam_n1_result",""), w.get("exam_n2_result",""), w.get("exam_n3_result","")] if r == "راسب")

def get_fail_e(w):
    return sum(1 for r in [w.get("exam_e1_result",""), w.get("exam_e2_result",""), w.get("exam_e3_result","")] if r == "راسب")

def get_stagnant_days(w):
    dates = []
    for key in ["eval_date","train_n1_date","exam_n1_date","train_e_date","exam_e1_date","license_date"]:
        v = w.get(key,"")
        if v:
            try: dates.append(datetime.strptime(v, "%Y-%m-%d").date())
            except: pass
    if not dates: return None
    return (date.today() - max(dates)).days

def get_appointments(workers):
    appts = []
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
    for w in workers:
        for date_key, time_key, appt_name in appt_fields:
            v = w.get(date_key,"")
            if v:
                try:
                    d = datetime.strptime(v, "%Y-%m-%d").date()
                    diff = (d - today).days
                    if -30 <= diff <= 14:
                        if diff < 0:   status = "🔴 فات الموعد"
                        elif diff == 0: status = "🔴 اليوم!"
                        elif diff == 1: status = "🟠 غداً"
                        elif diff <= 3: status = "⚠️ قريب"
                        else:           status = "✅ الأسبوعان"
                        appts.append({
                            "name": w["name"], "iqama": w["iqama"],
                            "type": appt_name, "date": d,
                            "time": w.get(time_key,"--"),
                            "status": status, "diff": diff
                        })
                except: pass
    return sorted(appts, key=lambda x: x["date"])

# ══════════════════════════════════════════════
# صفحة تسجيل الدخول
# ══════════════════════════════════════════════
def login_page():
    st.markdown("""
    <div style="text-align:center; margin-top: 40px;">
        <div style="font-size:60px;">🪪</div>
        <h2 style="color:#1F3864; font-weight:800;">نظام متابعة مراحل الرخصة</h2>
        <p style="color:#666;">قتاد اللوجستية</p>
    </div>
    """, unsafe_allow_html=True)

    col1, col2, col3 = st.columns([1,1.5,1])
    with col2:
        with st.container():
            st.markdown("### 🔐 تسجيل الدخول")
            username = st.text_input("اسم المستخدم", placeholder="username")
            password = st.text_input("كلمة المرور", type="password", placeholder="••••••••")
            
            if st.button("دخول →", use_container_width=True, type="primary"):
                if username in USERS and USERS[username]["password"] == password:
                    st.session_state.logged_in = True
                    st.session_state.username = username
                    st.session_state.user = USERS[username]
                    st.rerun()
                else:
                    st.error("❌ اسم المستخدم أو كلمة المرور خاطئة")
            
            st.markdown("---")
            st.markdown("""
            <div style="font-size:12px; color:#999; text-align:center;">
            🔑 admin / admin123 &nbsp;|&nbsp; ✏️ editor / edit123 &nbsp;|&nbsp; 👁️ viewer / view123
            </div>
            """, unsafe_allow_html=True)

# ══════════════════════════════════════════════
# الصفحة الرئيسية — Dashboard
# ══════════════════════════════════════════════
def dashboard_page(data):
    workers = data["workers"]
    today = date.today()
    
    # إحصائيات
    total     = len([w for w in workers if w["name"]])
    licensed  = len([w for w in workers if w.get("license_date")])
    in_prog   = len([w for w in workers if "🔄" in get_status(w)])
    not_start = len([w for w in workers if get_status(w) == "⛔ لم يبدأ"])
    fail_n    = sum(get_fail_n(w) for w in workers)
    fail_e    = sum(get_fail_e(w) for w in workers)
    appts     = get_appointments(workers)
    today_appts = [a for a in appts if a["diff"] == 0]
    pct = round(licensed/max(1,total)*100)

    # ملاحظات الشركة
    if data.get("company_note"):
        st.info(f"📢 {data['company_note']}")

    # KPI Cards
    cols = st.columns(4)
    kpis = [
        (total,    "👷 إجمالي العمال", "#1F3864", "#BF8F00"),
        (licensed, "✅ أصدر رخصة",     "#1E7145", "white"),
        (in_prog,  "🔄 قيد التنفيذ",   "#2E5496", "white"),
        (not_start,"⛔ لم يبدأ",       "#404040", "white"),
    ]
    for col, (val, lbl, bg, fg) in zip(cols, kpis):
        col.markdown(f"""
        <div class="kpi-card" style="border-top-color:{bg};">
            <div class="kpi-value" style="color:{bg};">{val}</div>
            <div class="kpi-label">{lbl}</div>
        </div>""", unsafe_allow_html=True)

    cols2 = st.columns(4)
    kpis2 = [
        (fail_n,        "⚠️ رسوب نظري",   "#C55A11", "white"),
        (fail_e,        "⚠️ رسوب عملي",   "#C00000", "white"),
        (len(today_appts),"📅 موعد اليوم", "#00695C", "white"),
        (f"{pct}%",     "📈 نسبة الإنجاز","#7030A0", "white"),
    ]
    for col, (val, lbl, bg, fg) in zip(cols2, kpis2):
        col.markdown(f"""
        <div class="kpi-card" style="border-top-color:{bg};">
            <div class="kpi-value" style="color:{bg};">{val}</div>
            <div class="kpi-label">{lbl}</div>
        </div>""", unsafe_allow_html=True)

    st.markdown("---")

    # مواعيد اليوم
    col_l, col_r = st.columns([1.5, 1])
    
    with col_l:
        st.markdown("### 📅 مواعيد اليوم")
        if today_appts:
            for a in today_appts:
                st.markdown(f"""
                <div class="alert-today">
                    <strong>🔴 {a['name']}</strong> — {a['type']}
                    &nbsp;&nbsp; ⏰ {a['time'] or '--'}
                </div>""", unsafe_allow_html=True)
        else:
            st.markdown('<div class="alert-ok">✅ لا توجد مواعيد اليوم</div>', unsafe_allow_html=True)

        # مواعيد قريبة (2 يوم)
        soon = [a for a in appts if 0 < a["diff"] <= 3]
        if soon:
            st.markdown("### ⚠️ مواعيد قريبة")
            for a in soon[:5]:
                days_text = "غداً" if a["diff"]==1 else f"بعد {a['diff']} أيام"
                st.markdown(f"""
                <div class="alert-soon">
                    <strong>{a['name']}</strong> — {a['type']}
                    &nbsp;&nbsp; 📅 {a['date']} ({days_text})
                </div>""", unsafe_allow_html=True)

    with col_r:
        st.markdown("### 📊 توزيع المراحل")
        stage_counts = {}
        for w in workers:
            s = get_status(w)
            stage_counts[s] = stage_counts.get(s, 0) + 1
        
        stage_colors = {
            "⛔ لم يبدأ": "#404040", "🔄 التقييم": "#7030A0",
            "🔄 مرحلة النظري": "#2E5496", "✅ اكتمل النظري": "#4472C4",
            "🔄 مرحلة العملي": "#00695C", "✅ اكتمل العملي": "#1E7145",
            "✅ أصدر رخصة": "#1E7145"
        }
        for stage, count in stage_counts.items():
            pct_s = round(count/max(1,total)*100)
            color = stage_colors.get(stage, "#666")
            bar = "█" * round(pct_s/5) + "░" * (20 - round(pct_s/5))
            st.markdown(f"""
            <div style="margin:6px 0; display:flex; align-items:center; gap:10px;">
                <span style="min-width:160px; font-size:13px; font-weight:600;">{stage}</span>
                <span style="color:{color}; font-family:monospace; font-size:11px;">{bar}</span>
                <span style="font-weight:700; color:{color};">{count}</span>
            </div>""", unsafe_allow_html=True)

# ══════════════════════════════════════════════
# صفحة المتابعة
# ══════════════════════════════════════════════
def tracking_page(data, can_edit):
    workers = data["workers"]
    
    st.markdown("### 📋 متابعة مراحل الرخصة")
    
    # فلترة وبحث
    col1, col2, col3 = st.columns([2,1,1])
    with col1:
        search = st.text_input("🔍 بحث بالاسم أو رقم الإقامة", placeholder="اكتب للبحث...")
    with col2:
        filter_status = st.selectbox("فلتر الحالة", ["الكل","⛔ لم يبدأ","🔄 التقييم",
            "🔄 مرحلة النظري","✅ اكتمل النظري","🔄 مرحلة العملي","✅ اكتمل العملي","✅ أصدر رخصة"])
    with col3:
        filter_fail = st.checkbox("الراسبون فقط")

    # تصفية
    filtered = []
    for w in workers:
        if search and search.lower() not in w["name"].lower() and search not in w.get("iqama",""):
            continue
        status = get_status(w)
        if filter_status != "الكل" and status != filter_status:
            continue
        if filter_fail and get_fail_n(w) == 0 and get_fail_e(w) == 0:
            continue
        filtered.append(w)

    st.caption(f"عرض {len(filtered)} من {len(workers)} عامل")

    # جدول ملخص
    status_badge = {
        "✅ أصدر رخصة":"badge-green","🔄 مرحلة النظري":"badge-blue",
        "🔄 مرحلة العملي":"badge-blue","✅ اكتمل النظري":"badge-blue",
        "✅ اكتمل العملي":"badge-green","🔄 التقييم":"badge-purple",
        "⛔ لم يبدأ":"badge-gray"
    }
    
    rows = ""
    for w in filtered:
        status = get_status(w)
        badge_cls = status_badge.get(status, "badge-gray")
        fn = get_fail_n(w); fe = get_fail_e(w)
        stag = get_stagnant_days(w)
        stag_str = f"{stag} يوم" if isinstance(stag, int) else "لم يبدأ"
        stag_color = "#C00000" if isinstance(stag,int) and stag>30 else "#C55A11" if isinstance(stag,int) and stag>15 else "#404040"
        rows += f"""<tr>
            <td style="font-weight:700;color:#1F3864;">{w['id']}</td>
            <td style="text-align:right;font-weight:600;">{w['name']}</td>
            <td>{w.get('iqama','')}</td>
            <td><span class="badge {badge_cls}">{status}</span></td>
            <td>{'<span style="color:#C00000;font-weight:700;">'+str(fn)+'</span>' if fn>0 else '—'}</td>
            <td>{'<span style="color:#C00000;font-weight:700;">'+str(fe)+'</span>' if fe>0 else '—'}</td>
            <td style="color:{stag_color};font-weight:600;">{stag_str}</td>
        </tr>"""
    
    st.markdown(f"""
    <table class="styled-table">
        <thead><tr>
            <th>#</th><th>الاسم</th><th>الإقامة</th><th>الحالة</th>
            <th>رسوب نظري</th><th>رسوب عملي</th><th>أيام التعطل</th>
        </tr></thead>
        <tbody>{rows}</tbody>
    </table>""", unsafe_allow_html=True)

    # تعديل بيانات عامل
    if can_edit:
        st.markdown("---")
        st.markdown("### ✏️ تعديل بيانات عامل")
        
        worker_names = [w["name"] for w in workers]
        selected = st.selectbox("اختر العامل", worker_names)
        w_idx = worker_names.index(selected)
        w = workers[w_idx]
        
        with st.expander(f"📝 بيانات {selected}", expanded=True):
            tabs = st.tabs(["① التقييم", "② النظري", "③ العملي", "④ الرخصة", "ملاحظات"])
            
            with tabs[0]:
                c1,c2,c3,c4 = st.columns(4)
                w["eval_date"]   = c1.date_input("تاريخ التقييم", value=datetime.strptime(w["eval_date"],"%Y-%m-%d").date() if w.get("eval_date") else None, key="ed").strftime("%Y-%m-%d") if c1.date_input("تاريخ التقييم", value=datetime.strptime(w["eval_date"],"%Y-%m-%d").date() if w.get("eval_date") else None, key="ed2") else ""
                w["eval_hours"]  = c2.selectbox("الساعات", ["","6 ساعات","15 ساعة","30 ساعة"], index=["","6 ساعات","15 ساعة","30 ساعة"].index(w.get("eval_hours","")) if w.get("eval_hours") in ["","6 ساعات","15 ساعة","30 ساعة"] else 0)
                w["eval_result"] = c3.selectbox("النتيجة", ["","ناجح","راسب","غائب","لم يتم الحجز"], index=["","ناجح","راسب","غائب","لم يتم الحجز"].index(w.get("eval_result","")) if w.get("eval_result","") in ["","ناجح","راسب","غائب","لم يتم الحجز"] else 0)

            with tabs[1]:
                c1,c2 = st.columns(2)
                with c1:
                    st.markdown("**تدريب نظري**")
                    d1 = st.date_input("موعد 1", value=datetime.strptime(w["train_n1_date"],"%Y-%m-%d").date() if w.get("train_n1_date") else None, key="tn1")
                    w["train_n1_date"] = d1.strftime("%Y-%m-%d") if d1 else ""
                    d2 = st.date_input("موعد 2", value=datetime.strptime(w["train_n2_date"],"%Y-%m-%d").date() if w.get("train_n2_date") else None, key="tn2")
                    w["train_n2_date"] = d2.strftime("%Y-%m-%d") if d2 else ""
                    w["train_n_attend"] = st.selectbox("الحضور", ["","حضر","غائب","مؤجل"], key="tna")
                with c2:
                    st.markdown("**اختبار نظري**")
                    for i, (dk,rk,label) in enumerate([("exam_n1_date","exam_n1_result","محاولة 1"),("exam_n2_date","exam_n2_result","محاولة 2"),("exam_n3_date","exam_n3_result","محاولة 3")]):
                        cc1,cc2 = st.columns(2)
                        d = cc1.date_input(label, value=datetime.strptime(w[dk],"%Y-%m-%d").date() if w.get(dk) else None, key=f"en{i}")
                        w[dk] = d.strftime("%Y-%m-%d") if d else ""
                        w[rk] = cc2.selectbox("النتيجة", ["","ناجح","راسب","غائب","لم يتم الحجز"], key=f"er{i}")

            with tabs[2]:
                c1,c2 = st.columns(2)
                with c1:
                    st.markdown("**تدريب عملي**")
                    d = st.date_input("التاريخ", value=datetime.strptime(w["train_e_date"],"%Y-%m-%d").date() if w.get("train_e_date") else None, key="te")
                    w["train_e_date"] = d.strftime("%Y-%m-%d") if d else ""
                    w["train_e_attend"] = st.selectbox("الحضور", ["","حضر","غائب","مؤجل"], key="tea")
                with c2:
                    st.markdown("**اختبار عملي**")
                    for i, (dk,rk,label) in enumerate([("exam_e1_date","exam_e1_result","محاولة 1"),("exam_e2_date","exam_e2_result","محاولة 2"),("exam_e3_date","exam_e3_result","محاولة 3")]):
                        cc1,cc2 = st.columns(2)
                        d = cc1.date_input(label, value=datetime.strptime(w[dk],"%Y-%m-%d").date() if w.get(dk) else None, key=f"ee{i}")
                        w[dk] = d.strftime("%Y-%m-%d") if d else ""
                        w[rk] = cc2.selectbox("النتيجة", ["","ناجح","راسب","غائب","لم يتم الحجز"], key=f"eer{i}")

            with tabs[3]:
                d = st.date_input("تاريخ إصدار الرخصة", value=datetime.strptime(w["license_date"],"%Y-%m-%d").date() if w.get("license_date") else None, key="lic")
                w["license_date"] = d.strftime("%Y-%m-%d") if d else ""

            with tabs[4]:
                w["notes"] = st.text_area("ملاحظات", value=w.get("notes",""), key="notes")
                w["email"] = st.text_input("📧 الإيميل", value=w.get("email",""), key="email")

            if st.button("💾 حفظ", type="primary", use_container_width=True):
                workers[w_idx] = w
                data["workers"] = workers
                save_data(data)
                st.success("✅ تم الحفظ بنجاح!")
                st.rerun()

# ══════════════════════════════════════════════
# صفحة المواعيد
# ══════════════════════════════════════════════
def schedule_page(data):
    workers = data["workers"]
    appts = get_appointments(workers)
    today = date.today()
    
    st.markdown("### 📅 مواعيد الأسبوعين")
    
    # KPIs
    c1,c2,c3,c4 = st.columns(4)
    today_c = len([a for a in appts if a["diff"]==0])
    week_c  = len([a for a in appts if 0<=a["diff"]<=14])
    past_c  = len([a for a in appts if a["diff"]<0])
    c1.metric("🔴 اليوم", today_c)
    c2.metric("📅 الأسبوعان", week_c)
    c3.metric("🔴 فات موعده", past_c)
    c4.metric("📆 التاريخ", today.strftime("%Y/%m/%d"))

    st.markdown("---")

    if not appts:
        st.info("لا توجد مواعيد في هذه الفترة")
        return

    # جدول المواعيد
    rows = ""
    for a in appts:
        status_colors = {
            "🔴 اليوم!": ("#FDECEA","#C00000"),
            "🔴 فات الموعد": ("#FDECEA","#C00000"),
            "🟠 غداً": ("#FCE4D6","#C55A11"),
            "⚠️ قريب": ("#FFF2CC","#BF8F00"),
            "✅ الأسبوعان": ("#E2EFDA","#1E7145"),
        }
        bg, fg = status_colors.get(a["status"], ("#F2F2F2","#404040"))
        type_colors = {
            "تدريب نظري 1":"#1565C0","تدريب نظري 2":"#1565C0",
            "اختبار نظري 1":"#7030A0","اختبار نظري 2":"#7030A0","اختبار نظري 3":"#7030A0",
            "تدريب عملي":"#00695C",
            "اختبار عملي 1":"#1E7145","اختبار عملي 2":"#1E7145","اختبار عملي 3":"#1E7145",
        }
        tc = type_colors.get(a["type"],"#404040")
        day_ar = ["الاثنين","الثلاثاء","الأربعاء","الخميس","الجمعة","السبت","الأحد"][a["date"].weekday()]
        diff_str = f"({a['diff']} يوم)" if a["diff"] > 0 else ("(اليوم)" if a["diff"]==0 else f"({a['diff']} يوم)")
        rows += f"""<tr>
            <td style="text-align:right;font-weight:600;">{a['name']}</td>
            <td><span style="background:{tc}22;color:{tc};padding:3px 8px;border-radius:12px;font-size:12px;font-weight:700;">{a['type']}</span></td>
            <td style="font-weight:600;">{a['date'].strftime('%Y/%m/%d')}</td>
            <td style="color:#7030A0;font-weight:700;">{a['time'] or '--'}</td>
            <td>{day_ar} {diff_str}</td>
            <td><span style="background:{bg};color:{fg};padding:3px 10px;border-radius:12px;font-size:12px;font-weight:700;">{a['status']}</span></td>
        </tr>"""

    st.markdown(f"""
    <table class="styled-table">
        <thead><tr>
            <th>اسم العامل</th><th>نوع الموعد</th><th>التاريخ</th>
            <th>الوقت</th><th>اليوم</th><th>الحالة</th>
        </tr></thead>
        <tbody>{rows}</tbody>
    </table>""", unsafe_allow_html=True)

# ══════════════════════════════════════════════
# صفحة المؤشرات
# ══════════════════════════════════════════════
def indicators_page(data):
    workers = data["workers"]
    today = date.today()
    
    st.markdown("### 📊 المؤشرات الشاملة")

    total    = len([w for w in workers if w["name"]])
    licensed = len([w for w in workers if w.get("license_date")])
    evaluated= len([w for w in workers if w.get("eval_date")])
    fail_n   = sum(get_fail_n(w) for w in workers)
    fail_e   = sum(get_fail_e(w) for w in workers)
    stagnant = [w for w in workers if isinstance(get_stagnant_days(w), int) and get_stagnant_days(w) > 30]
    
    # نسبة النجاح
    all_n_results = []
    all_e_results = []
    for w in workers:
        for rk in ["exam_n1_result","exam_n2_result","exam_n3_result"]:
            v = w.get(rk,"")
            if v in ["ناجح","راسب"]: all_n_results.append(v)
        for rk in ["exam_e1_result","exam_e2_result","exam_e3_result"]:
            v = w.get(rk,"")
            if v in ["ناجح","راسب"]: all_e_results.append(v)
    
    pass_n_pct = round(all_n_results.count("ناجح")/max(1,len(all_n_results))*100) if all_n_results else 0
    pass_e_pct = round(all_e_results.count("ناجح")/max(1,len(all_e_results))*100) if all_e_results else 0

    c1,c2,c3,c4 = st.columns(4)
    c1.metric("✅ نجاح النظري", f"{pass_n_pct}%")
    c2.metric("✅ نجاح العملي", f"{pass_e_pct}%")
    c3.metric("❌ رسوب نظري", f"{100-pass_n_pct}%" if all_n_results else "—")
    c4.metric("😴 معطل +30 يوم", len(stagnant))

    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### توزيع المراحل")
        stage_data = {}
        for w in workers:
            s = get_status(w)
            stage_data[s] = stage_data.get(s, 0) + 1
        
        for stage, count in stage_data.items():
            pct_s = round(count/max(1,total)*100)
            st.markdown(f"**{stage}**: {count} ({pct_s}%)")
            st.progress(pct_s/100)

    with col2:
        st.markdown("#### 🚨 العمال الجامدون (+30 يوم)")
        if stagnant:
            for w in stagnant:
                days = get_stagnant_days(w)
                st.markdown(f"""
                <div class="alert-today">
                    <strong>{w['name']}</strong> — {days} يوم بدون تحديث
                    <br><small>{get_status(w)}</small>
                </div>""", unsafe_allow_html=True)
        else:
            st.success("✅ لا يوجد عمال جامدون")

        st.markdown("#### 🚨 الراسبون")
        failed = [w for w in workers if get_fail_n(w)>0 or get_fail_e(w)>0]
        if failed:
            for w in failed:
                fn,fe = get_fail_n(w), get_fail_e(w)
                st.markdown(f"""
                <div class="alert-today">
                    <strong>{w['name']}</strong>
                    {f'— رسوب نظري: {fn}' if fn else ''}
                    {f'— رسوب عملي: {fe}' if fe else ''}
                </div>""", unsafe_allow_html=True)
        else:
            st.success("✅ لا يوجد راسبون")

# ══════════════════════════════════════════════
# البرنامج الرئيسي
# ══════════════════════════════════════════════
def main():
    # تهيئة الجلسة
    if "logged_in" not in st.session_state:
        st.session_state.logged_in = False

    # صفحة تسجيل الدخول
    if not st.session_state.logged_in:
        login_page()
        return

    user = st.session_state.user
    role = user["role"]
    can_edit = ROLES[role]["can_edit"]

    # تحميل البيانات
    data = load_data()

    # الشريط الجانبي
    with st.sidebar:
        st.markdown(f"""
        <div style="text-align:center; padding:20px 0;">
            <div style="font-size:40px;">🪪</div>
            <h3 style="color:white;">قتاد اللوجستية</h3>
            <div style="background:#2E5496;padding:8px;border-radius:8px;margin:10px 0;">
                <span style="color:white;font-size:13px;">{ROLES[role]['label']}: {user['name']}</span>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("---")
        page = st.radio("", ["🏠 الرئيسية","📋 المتابعة","📅 المواعيد","📊 المؤشرات"], label_visibility="hidden")
        st.markdown("---")
        st.caption(f"آخر تحديث: {datetime.now().strftime('%Y/%m/%d %H:%M')}")
        
        if can_edit:
            st.markdown("---")
            note = st.text_area("📢 ملاحظات الشركة", value=data.get("company_note",""), key="cn")
            if st.button("حفظ الملاحظة"):
                data["company_note"] = note
                save_data(data)
                st.success("✅ تم")
        
        if st.button("🚪 تسجيل الخروج", use_container_width=True):
            st.session_state.logged_in = False
            st.session_state.username = None
            st.rerun()

    # محتوى الصفحة
    if page == "🏠 الرئيسية":
        dashboard_page(data)
    elif page == "📋 المتابعة":
        tracking_page(data, can_edit)
    elif page == "📅 المواعيد":
        schedule_page(data)
    elif page == "📊 المؤشرات":
        indicators_page(data)

if __name__ == "__main__":
    main()
