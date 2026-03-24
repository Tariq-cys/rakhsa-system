import streamlit as st
from datetime import datetime, date
import os

# ══════════════════════════════════════════════
# Supabase
# ══════════════════════════════════════════════
from supabase import create_client, Client

SUPABASE_URL = "https://pxsjqtyhiucqrjbrebbu.supabase.co"
SUPABASE_KEY = os.environ.get("SUPABASE_KEY", "sb_publishable_2S4BOn8mtk_pcT7nYDZ2dQ_rUJJO9ja")

@st.cache_resource
def get_supabase():
    return create_client(SUPABASE_URL, SUPABASE_KEY)

def db_get_workers():
    sb = get_supabase()
    res = sb.table("workers").select("*").order("id").execute()
    return res.data or []

def db_save_worker(w):
    sb = get_supabase()
    w["updated_at"] = datetime.now().isoformat()
    if w.get("id"):
        sb.table("workers").update(w).eq("id", w["id"]).execute()
    else:
        sb.table("workers").insert(w).execute()

def db_delete_worker(wid):
    sb = get_supabase()
    sb.table("workers").delete().eq("id", wid).execute()

def db_get_note():
    sb = get_supabase()
    res = sb.table("settings").select("value").eq("key","company_note").execute()
    return res.data[0]["value"] if res.data else ""

def db_save_note(note):
    sb = get_supabase()
    sb.table("settings").upsert({"key":"company_note","value":note}).execute()

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
    background: white; border-radius: 16px; padding: 22px 18px;
    text-align: center;
    box-shadow: 0 4px 20px rgba(0,0,0,0.08);
    border-top: 5px solid; margin-bottom: 12px;
    transition: transform 0.2s, box-shadow 0.2s;
}
.kpi-card:hover { transform: translateY(-3px); box-shadow: 0 8px 25px rgba(0,0,0,0.12); }
.kpi-card .val { font-size: 44px; font-weight: 800; line-height: 1.1; }
.kpi-card .lbl { font-size: 13px; color: #555; margin-top: 6px; font-weight: 700; letter-spacing: 0.3px; }
.styled-table {
    width:100%; border-collapse:collapse; background:white;
    border-radius:12px; overflow:hidden;
    box-shadow:0 4px 15px rgba(0,0,0,0.08); font-size:15px;
}
.styled-table th {
    background:#1F3864; color:white;
    padding:14px 16px; text-align:center;
    font-weight:700; font-size:14px;
    border-bottom: 3px solid #BF8F00;
}
.styled-table td {
    padding:13px 16px; border-bottom:1px solid #E8EEF4;
    text-align:center; font-size:14px;
}
.styled-table tr:nth-child(even) { background:#F4F7FB; }
.styled-table tr:hover { background:#E3EDFF; transition: background 0.2s; }
.styled-table td:nth-child(2) { text-align:right; font-weight:600; font-size:15px; }
.alert-r { background:#FFF0EE; border-right:5px solid #C00000; padding:12px 16px; border-radius:10px; margin:5px 0; box-shadow:0 2px 8px rgba(192,0,0,0.08); }
.alert-o { background:#FFFBEE; border-right:5px solid #BF8F00; padding:12px 16px; border-radius:10px; margin:5px 0; box-shadow:0 2px 8px rgba(191,143,0,0.08); }
.alert-g { background:#F0FFF4; border-right:5px solid #1E7145; padding:12px 16px; border-radius:10px; margin:5px 0; box-shadow:0 2px 8px rgba(30,113,69,0.08); }
section[data-testid="stSidebar"] { background:#1F3864 !important; }
section[data-testid="stSidebar"] * { color:white !important; }
#MainMenu,footer,.stDeployButton { visibility:hidden; }
</style>
""", unsafe_allow_html=True)

# ══════════════════════════════════════════════
# المستخدمون
# ══════════════════════════════════════════════
USERS = {
    "admin":  {"password":"Qitad@2026!", "role":"admin",  "name":"المدير"},
    "editor": {"password":"Edit@Qitad1", "role":"editor", "name":"المحرر"},
    "viewer": {"password":"View@Qitad1", "role":"viewer", "name":"مشاهد"},
}
ROLES = {
    "admin":  {"label":"🔑 مدير",   "can_edit":True,  "can_add":True,  "can_delete":True},
    "editor": {"label":"✏️ محرر",  "can_edit":True,  "can_add":False, "can_delete":False},
    "viewer": {"label":"👁️ مشاهد","can_edit":False, "can_add":False, "can_delete":False},
}

# ══════════════════════════════════════════════
# دوال مساعدة
# ══════════════════════════════════════════════
def get_status(w):
    if w.get("has_license_already") == "نعم": return "✅ يملك رخصة مسبقاً"
    if w.get("license_date"):                  return "✅ أصدر رخصة"
    if any(w.get(f"exam_e{i}_result")=="ناجح" for i in range(1,4)): return "✅ اكتمل العملي"
    if any(w.get(f) for f in ["exam_e1_date","train_e_date"]):       return "🔄 مرحلة العملي"
    if any(w.get(f"exam_n{i}_result")=="ناجح" for i in range(1,4)): return "✅ اكتمل النظري"
    if any(w.get(f) for f in ["exam_n1_date","train_n1_date"]):      return "🔄 مرحلة النظري"
    if w.get("eval_date"):                     return "🔄 التقييم"
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

def fmt_date(d): return d.strftime("%Y-%m-%d") if d else ""

def get_appointments(workers):
    today = date.today()
    fields = [
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
        for dk,tk,name in fields:
            d = parse_date(w.get(dk,""))
            if d:
                diff = (d-today).days
                if -30 <= diff <= 14:
                    if diff<0:    status="🔴 فات الموعد"
                    elif diff==0: status="🔴 اليوم!"
                    elif diff==1: status="🟠 غداً"
                    elif diff<=3: status="⚠️ قريب"
                    else:         status="✅ الأسبوعان"
                    appts.append({"name":w["name"],"iqama":w.get("iqama",""),
                        "type":name,"date":d,"time":w.get(tk,"--") or "--",
                        "status":status,"diff":diff})
    return sorted(appts, key=lambda x: x["date"])

STATUS_COLORS = {
    "✅ يملك رخصة مسبقاً":"#1E7145",
    "✅ أصدر رخصة":"#1E7145",
    "🔄 مرحلة النظري":"#2E5496","🔄 مرحلة العملي":"#00695C",
    "✅ اكتمل النظري":"#4472C4","✅ اكتمل العملي":"#1E7145",
    "🔄 التقييم":"#7030A0","⛔ لم يبدأ":"#404040"
}

def sel_idx(opts, val): return opts.index(val) if val in opts else 0

# ══════════════════════════════════════════════
# نموذج بيانات العامل الكامل
# ══════════════════════════════════════════════
def worker_form(w, key_prefix=""):
    RES    = ["","ناجح","راسب","غائب","لم يتم الحجز"]
    ATTEND = ["","حضر","غائب","مؤجل"]
    HOURS  = ["","6 ساعات","15 ساعة","30 ساعة"]

    # معلومات أساسية
    st.markdown("#### 👤 معلومات العامل")
    c1,c2 = st.columns(2)
    w["name"]  = c1.text_input("الاسم الكامل *", value=w.get("name",""), key=f"{key_prefix}_name")
    w["iqama"] = c2.text_input("رقم الإقامة", value=w.get("iqama",""), key=f"{key_prefix}_iqama")
    w["email"] = c1.text_input("📧 الإيميل", value=w.get("email",""), key=f"{key_prefix}_email")

    st.markdown("---")
    tabs = st.tabs(["⓪ رخصة مسبقة","① التقييم","② تدريب نظري",
                    "③ اختبار نظري","④ تدريب عملي","⑤ اختبار عملي","⑥ الرخصة","📝 ملاحظات"])

    # ⓪ رخصة مسبقة
    with tabs[0]:
        st.markdown("**هل يملك العامل رخصة قيادة مسبقاً؟**")
        has = st.radio("الحالة",["لا يملك رخصة","نعم — يملك رخصة مسبقاً"],
            index=1 if w.get("has_license_already")=="نعم" else 0,
            key=f"{key_prefix}_hl", horizontal=True)
        w["has_license_already"] = "نعم" if "نعم" in has else ""
        if w["has_license_already"]=="نعم":
            st.success("✅ يملك رخصة مسبقاً — لا يحتاج لاجتياز المراحل")
            d = st.date_input("تاريخ الرخصة المسبقة", value=parse_date(w.get("existing_license_date")), key=f"{key_prefix}_eld")
            w["existing_license_date"] = fmt_date(d)
        else:
            st.info("ℹ️ سيمر العامل بكل مراحل التقييم والتدريب والاختبار")

    # ① التقييم
    with tabs[1]:
        st.markdown("**بيانات التقييم**")
        c1,c2,c3,c4 = st.columns(4)
        d = c1.date_input("تاريخ التقييم", value=parse_date(w.get("eval_date")), key=f"{key_prefix}_ed")
        w["eval_date"]   = fmt_date(d)
        w["eval_time"]   = c2.text_input("الوقت", value=w.get("eval_time",""), placeholder="10:00", key=f"{key_prefix}_et")
        w["eval_hours"]  = c3.selectbox("الساعات", HOURS, index=sel_idx(HOURS,w.get("eval_hours","")), key=f"{key_prefix}_eh")
        w["eval_result"] = c4.selectbox("النتيجة", RES, index=sel_idx(RES,w.get("eval_result","")), key=f"{key_prefix}_er")

    # ② تدريب نظري
    with tabs[2]:
        st.markdown("**التدريب النظري — موعدان**")
        c1,c2 = st.columns(2)
        with c1:
            st.markdown("**موعد 1**")
            d = st.date_input("التاريخ", value=parse_date(w.get("train_n1_date")), key=f"{key_prefix}_tn1d")
            w["train_n1_date"] = fmt_date(d)
            w["train_n1_time"] = st.text_input("الوقت", value=w.get("train_n1_time",""), placeholder="09:00", key=f"{key_prefix}_tn1t")
        with c2:
            st.markdown("**موعد 2**")
            d = st.date_input("التاريخ", value=parse_date(w.get("train_n2_date")), key=f"{key_prefix}_tn2d")
            w["train_n2_date"] = fmt_date(d)
            w["train_n2_time"] = st.text_input("الوقت", value=w.get("train_n2_time",""), placeholder="09:00", key=f"{key_prefix}_tn2t")
        w["train_n_attend"] = st.selectbox("الحضور", ATTEND, index=sel_idx(ATTEND,w.get("train_n_attend","")), key=f"{key_prefix}_tna")

    # ③ اختبار نظري
    with tabs[3]:
        st.markdown("**اختبار نظري — 3 محاولات**")
        for i in range(1,4):
            with st.expander(f"محاولة {i}", expanded=(i==1)):
                c1,c2,c3 = st.columns(3)
                d = c1.date_input("التاريخ", value=parse_date(w.get(f"exam_n{i}_date")), key=f"{key_prefix}_en{i}d")
                w[f"exam_n{i}_date"]   = fmt_date(d)
                w[f"exam_n{i}_time"]   = c2.text_input("الوقت", value=w.get(f"exam_n{i}_time",""), placeholder="10:00", key=f"{key_prefix}_en{i}t")
                w[f"exam_n{i}_result"] = c3.selectbox("النتيجة", RES, index=sel_idx(RES,w.get(f"exam_n{i}_result","")), key=f"{key_prefix}_en{i}r")

    # ④ تدريب عملي
    with tabs[4]:
        st.markdown("**التدريب العملي — موعد واحد**")
        c1,c2,c3 = st.columns(3)
        d = c1.date_input("التاريخ", value=parse_date(w.get("train_e_date")), key=f"{key_prefix}_ted")
        w["train_e_date"]   = fmt_date(d)
        w["train_e_time"]   = c2.text_input("الوقت", value=w.get("train_e_time",""), placeholder="14:00", key=f"{key_prefix}_tet")
        w["train_e_attend"] = c3.selectbox("الحضور", ATTEND, index=sel_idx(ATTEND,w.get("train_e_attend","")), key=f"{key_prefix}_tea")

    # ⑤ اختبار عملي
    with tabs[5]:
        st.markdown("**اختبار عملي — 3 محاولات**")
        for i in range(1,4):
            with st.expander(f"محاولة {i}", expanded=(i==1)):
                c1,c2,c3 = st.columns(3)
                d = c1.date_input("التاريخ", value=parse_date(w.get(f"exam_e{i}_date")), key=f"{key_prefix}_ee{i}d")
                w[f"exam_e{i}_date"]   = fmt_date(d)
                w[f"exam_e{i}_time"]   = c2.text_input("الوقت", value=w.get(f"exam_e{i}_time",""), placeholder="10:00", key=f"{key_prefix}_ee{i}t")
                w[f"exam_e{i}_result"] = c3.selectbox("النتيجة", RES, index=sel_idx(RES,w.get(f"exam_e{i}_result","")), key=f"{key_prefix}_ee{i}r")

    # ⑥ الرخصة
    with tabs[6]:
        d = st.date_input("تاريخ إصدار الرخصة", value=parse_date(w.get("license_date")), key=f"{key_prefix}_ld")
        w["license_date"] = fmt_date(d)
        st.info(f"الحالة: **{get_status(w)}**")

    # 📝 ملاحظات
    with tabs[7]:
        w["notes"] = st.text_area("ملاحظات", value=w.get("notes",""), height=120, key=f"{key_prefix}_notes")

    return w

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
            <h2 style="color:#1F3864;font-weight:800;">نظام متابعة مراحل الرخصة</h2>
            <p style="color:#666;">قتاد اللوجستية</p>
        </div>""", unsafe_allow_html=True)
        with st.form("login"):
            username = st.text_input("👤 اسم المستخدم")
            password = st.text_input("🔒 كلمة المرور", type="password")
            if st.form_submit_button("دخول ←", use_container_width=True, type="primary"):
                if username in USERS and USERS[username]["password"]==password:
                    st.session_state.logged_in = True
                    st.session_state.user = USERS[username]
                    st.rerun()
                else:
                    st.error("❌ اسم المستخدم أو كلمة المرور غير صحيحة")

# ══════════════════════════════════════════════
# الصفحة الرئيسية
# ══════════════════════════════════════════════
def dashboard_page(workers, note):
    today = date.today()
    total     = len(workers)
    licensed  = len([w for w in workers if w.get("license_date") or w.get("has_license_already")=="نعم"])
    in_prog   = len([w for w in workers if "🔄" in get_status(w)])
    not_start = len([w for w in workers if get_status(w)=="⛔ لم يبدأ"])
    evaluated = len([w for w in workers if w.get("eval_date")])
    fail_n    = sum(get_fail_n(w) for w in workers)
    appts     = get_appointments(workers)
    today_ap  = [a for a in appts if a["diff"]==0]
    pct = round(licensed/max(1,total)*100)

    if note:
        st.info(f"📢 {note}")

    cols = st.columns(4)
    for col,(val,lbl,color) in zip(cols,[
        (total,"👷 إجمالي العمال","#1F3864"),
        (evaluated,"📋 المُقيَّمون","#7030A0"),
        (licensed,"✅ أصدر/يملك رخصة","#1E7145"),
        (in_prog,"🔄 قيد التنفيذ","#2E5496"),
    ]):
        col.markdown(f'<div class="kpi-card" style="border-top-color:{color};"><div class="val" style="color:{color};">{val}</div><div class="lbl">{lbl}</div></div>', unsafe_allow_html=True)

    cols2 = st.columns(4)
    for col,(val,lbl,color) in zip(cols2,[
        (not_start,"⛔ لم يبدأ","#404040"),
        (fail_n,"⚠️ رسوب نظري","#C55A11"),
        (len(today_ap),"📅 موعد اليوم","#00695C"),
        (f"{pct}%","📈 نسبة الإنجاز","#7030A0"),
    ]):
        col.markdown(f'<div class="kpi-card" style="border-top-color:{color};"><div class="val" style="color:{color};">{val}</div><div class="lbl">{lbl}</div></div>', unsafe_allow_html=True)

    st.markdown("---")
    col_l,col_r = st.columns([1.5,1])
    with col_l:
        st.markdown("### 📅 مواعيد اليوم")
        if today_ap:
            for a in today_ap:
                st.markdown(f'<div class="alert-r"><strong>🔴 {a["name"]}</strong> — {a["type"]} ⏰ {a["time"]}</div>', unsafe_allow_html=True)
        else:
            st.markdown('<div class="alert-g">✅ لا توجد مواعيد اليوم</div>', unsafe_allow_html=True)
        soon = [a for a in appts if 0<a["diff"]<=3]
        if soon:
            st.markdown("### ⚠️ مواعيد قريبة")
            for a in soon[:5]:
                txt = "غداً" if a["diff"]==1 else f"بعد {a['diff']} أيام"
                st.markdown(f'<div class="alert-o"><strong>{a["name"]}</strong> — {a["type"]} | {a["date"]} ({txt})</div>', unsafe_allow_html=True)
    with col_r:
        st.markdown("### 📊 توزيع المراحل")
        stage_counts = {}
        for w in workers:
            s = get_status(w); stage_counts[s] = stage_counts.get(s,0)+1
        for stage,count in stage_counts.items():
            pct_s = round(count/max(1,total)*100)
            color = STATUS_COLORS.get(stage,"#666")
            bar = "█"*round(pct_s/5)+"░"*(20-round(pct_s/5))
            st.markdown(f'<div style="margin:5px 0;display:flex;align-items:center;gap:8px;"><span style="min-width:170px;font-size:13px;font-weight:600;">{stage}</span><span style="color:{color};font-family:monospace;font-size:10px;">{bar}</span><span style="font-weight:700;color:{color};">{count}</span></div>', unsafe_allow_html=True)

# ══════════════════════════════════════════════
# صفحة المتابعة
# ══════════════════════════════════════════════
def tracking_page(workers, role):
    can_edit = ROLES[role]["can_edit"]
    can_add  = ROLES[role]["can_add"]
    can_del  = ROLES[role]["can_delete"]

    st.markdown("### 📋 متابعة مراحل الرخصة")
    
    # debug: تحقق من البيانات
    if workers and not workers[0].get("name"):
        st.error("⚠️ مشكلة في تحميل البيانات — تحقق من Supabase")
        st.write("عدد السجلات:", len(workers))
        st.write("أول سجل:", workers[0] if workers else "لا يوجد")

    # إضافة عامل (مدير فقط)
    if can_add:
        with st.expander("➕ إضافة عامل جديد"):
            new_w = {}
            new_w = worker_form(new_w, key_prefix="new")
            if st.button("✅ إضافة", type="primary"):
                if not new_w.get("name"):
                    st.error("❌ يرجى إدخال الاسم")
                else:
                    db_save_worker(new_w)
                    st.success(f"✅ تم إضافة {new_w['name']}")
                    st.rerun()

    st.markdown("---")

    # بحث وفلترة
    c1,c2,c3 = st.columns([2,1.2,1])
    search = c1.text_input("🔍 بحث بالاسم أو رقم الإقامة")
    filter_s = c2.selectbox("فلتر الحالة",["الكل","⛔ لم يبدأ","🔄 التقييم",
        "🔄 مرحلة النظري","✅ اكتمل النظري","🔄 مرحلة العملي",
        "✅ اكتمل العملي","✅ أصدر رخصة","✅ يملك رخصة مسبقاً"])
    filter_fail = c3.checkbox("الراسبون فقط")

    filtered = [w for w in workers if
        (not search or search.lower() in w["name"].lower() or search in w.get("iqama","")) and
        (filter_s=="الكل" or get_status(w)==filter_s) and
        (not filter_fail or get_fail_n(w)>0 or get_fail_e(w)>0)
    ]
    st.caption(f"عرض {len(filtered)} من {len(workers)} عامل")

    # جدول
    rows = ""
    for w in filtered:
        status = get_status(w)
        color  = STATUS_COLORS.get(status,"#666")
        fn,fe  = get_fail_n(w), get_fail_e(w)
        stag   = get_stagnant(w)
        stag_s = f"{stag} يوم" if isinstance(stag,int) else "لم يبدأ"
        sc     = "#C00000" if isinstance(stag,int) and stag>30 else "#C55A11" if isinstance(stag,int) and stag>15 else "#404040"
        fn_s   = f'<span style="color:#C00000;font-weight:700;">{fn}</span>' if fn>0 else "—"
        fe_s   = f'<span style="color:#C00000;font-weight:700;">{fe}</span>' if fe>0 else "—"
        rows  += f"""<tr>
            <td style="font-weight:800;color:#1F3864;font-size:15px;width:40px;">{w.get('id','')}</td>
            <td style="text-align:right;font-weight:700;font-size:15px;color:#1a1a2e;">{w.get('name','—')}</td>
            <td style="color:#555;font-size:14px;">{w.get('iqama','—')}</td>
            <td><span style="background:{color}18;color:{color};padding:5px 12px;border-radius:20px;font-size:13px;font-weight:700;white-space:nowrap;">{status}</span></td>
            <td style="font-size:14px;">{fn_s}</td>
            <td style="font-size:14px;">{fe_s}</td>
            <td style="color:{sc};font-weight:700;font-size:14px;">{stag_s}</td>
        </tr>"""

    st.markdown(f"""<table class="styled-table"><thead><tr>
        <th style="width:50px;">#</th>
        <th style="text-align:right;min-width:180px;">👤 الاسم</th>
        <th>🪪 رقم الإقامة</th>
        <th style="min-width:160px;">📊 الحالة</th>
        <th>⚠️ رسوب نظري</th>
        <th>⚠️ رسوب عملي</th>
        <th>⏱️ أيام التعطل</th>
    </tr></thead><tbody>{rows}</tbody></table>""", unsafe_allow_html=True)

    # تعديل
    if can_edit and filtered:
        st.markdown("---")
        st.markdown("### ✏️ تعديل بيانات عامل")
        names = [f"{w['id']}. {w['name']}" for w in workers]
        sel   = st.selectbox("اختر العامل", names)
        wid   = int(sel.split(".")[0])
        w     = next((x for x in workers if x["id"]==wid), None)
        if w:
            with st.expander(f"📝 {w['name']}", expanded=True):
                w_edit = dict(w)
                w_edit = worker_form(w_edit, key_prefix=f"e{wid}")
                cb1,cb2 = st.columns([1,4])
                if cb1.button("💾 حفظ", type="primary"):
                    db_save_worker(w_edit)
                    st.success("✅ تم الحفظ!")
                    st.rerun()
                if can_del:
                    if cb1.button("🗑️ حذف"):
                        if st.session_state.get("del_confirm")==wid:
                            db_delete_worker(wid)
                            st.success("✅ تم الحذف")
                            st.session_state.del_confirm = None
                            st.rerun()
                        else:
                            st.session_state.del_confirm = wid
                            st.warning("اضغط مجدداً للتأكيد")

# ══════════════════════════════════════════════
# صفحة المواعيد
# ══════════════════════════════════════════════
def schedule_page(workers):
    appts = get_appointments(workers)
    today = date.today()
    st.markdown("### 📅 مواعيد الأسبوعين")

    c1,c2,c3,c4 = st.columns(4)
    c1.metric("🔴 اليوم",         len([a for a in appts if a["diff"]==0]))
    c2.metric("📅 الأسبوعان",     len([a for a in appts if 0<=a["diff"]<=14]))
    c3.metric("🔴 فات موعده",     len([a for a in appts if a["diff"]<0]))
    c4.metric("📆 اليوم",         today.strftime("%Y/%m/%d"))

    if not appts:
        st.info("لا توجد مواعيد"); return

    type_c = {
        "تدريب نظري 1":"#1565C0","تدريب نظري 2":"#1565C0",
        "اختبار نظري 1":"#7030A0","اختبار نظري 2":"#7030A0","اختبار نظري 3":"#7030A0",
        "تدريب عملي":"#00695C",
        "اختبار عملي 1":"#1E7145","اختبار عملي 2":"#1E7145","اختبار عملي 3":"#1E7145",
    }
    stat_c = {
        "🔴 اليوم!":     ("#FDECEA","#C00000"),
        "🔴 فات الموعد": ("#FDECEA","#C00000"),
        "🟠 غداً":       ("#FCE4D6","#C55A11"),
        "⚠️ قريب":      ("#FFF2CC","#BF8F00"),
        "✅ الأسبوعان":  ("#E2EFDA","#1E7145"),
    }
    days_ar = ["الاثنين","الثلاثاء","الأربعاء","الخميس","الجمعة","السبت","الأحد"]
    rows = ""
    for a in appts:
        bg,fg = stat_c.get(a["status"],("#F2F2F2","#404040"))
        tc    = type_c.get(a["type"],"#404040")
        day   = days_ar[a["date"].weekday()]
        diff_s= "اليوم" if a["diff"]==0 else f"{a['diff']:+d} يوم"
        rows += f"""<tr>
            <td style="text-align:right;font-weight:600;">{a['name']}</td>
            <td><span style="background:{tc}22;color:{tc};padding:3px 8px;border-radius:10px;font-size:11px;font-weight:700;">{a['type']}</span></td>
            <td style="font-weight:600;">{a['date'].strftime('%Y/%m/%d')}</td>
            <td style="color:#7030A0;font-weight:700;">{a['time']}</td>
            <td>{day} ({diff_s})</td>
            <td><span style="background:{bg};color:{fg};padding:3px 10px;border-radius:10px;font-size:11px;font-weight:700;">{a['status']}</span></td>
        </tr>"""
    st.markdown(f"""<table class="styled-table"><thead><tr>
        <th>اسم العامل</th><th>نوع الموعد</th><th>التاريخ</th>
        <th>الوقت</th><th>اليوم</th><th>الحالة</th>
    </tr></thead><tbody>{rows}</tbody></table>""", unsafe_allow_html=True)

# ══════════════════════════════════════════════
# صفحة المؤشرات
# ══════════════════════════════════════════════
def indicators_page(workers):
    total    = len(workers)
    licensed = len([w for w in workers if w.get("license_date") or w.get("has_license_already")=="نعم"])
    stagnant = [w for w in workers if isinstance(get_stagnant(w),int) and get_stagnant(w)>30]

    all_n = [v for w in workers for i in range(1,4) if (v:=w.get(f"exam_n{i}_result","")) in ["ناجح","راسب"]]
    all_e = [v for w in workers for i in range(1,4) if (v:=w.get(f"exam_e{i}_result","")) in ["ناجح","راسب"]]
    pass_n = round(all_n.count("ناجح")/max(1,len(all_n))*100) if all_n else 0
    pass_e = round(all_e.count("ناجح")/max(1,len(all_e))*100) if all_e else 0

    st.markdown("### 📊 المؤشرات الشاملة")
    c1,c2,c3,c4 = st.columns(4)
    c1.metric("✅ نجاح النظري",    f"{pass_n}%")
    c2.metric("✅ نجاح العملي",    f"{pass_e}%")
    c3.metric("❌ رسوب النظري",   f"{100-pass_n}%" if all_n else "—")
    c4.metric("😴 معطل +30 يوم",  len(stagnant))

    st.markdown("---")
    col1,col2 = st.columns(2)
    with col1:
        st.markdown("#### 📊 توزيع المراحل")
        sd = {}
        for w in workers: s=get_status(w); sd[s]=sd.get(s,0)+1
        for stage,count in sd.items():
            pct_s = round(count/max(1,total)*100)
            st.markdown(f"**{stage}** — {count} ({pct_s}%)")
            st.progress(pct_s/100)
    with col2:
        st.markdown("#### 😴 الجامدون (+30 يوم)")
        if stagnant:
            for w in stagnant:
                st.markdown(f'<div class="alert-r"><strong>{w["name"]}</strong> — {get_stagnant(w)} يوم | {get_status(w)}</div>', unsafe_allow_html=True)
        else:
            st.markdown('<div class="alert-g">✅ لا يوجد جامدون</div>', unsafe_allow_html=True)

        st.markdown("#### 🚨 الراسبون")
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

# ══════════════════════════════════════════════
# صفحة البحث
# ══════════════════════════════════════════════
def search_page(workers):
    st.markdown("### 🔍 البحث السريع")
    c1,c2 = st.columns(2)
    s_name = c1.text_input("🔍 بحث بالاسم")
    s_iq   = c2.text_input("🔍 بحث برقم الإقامة")

    if not s_name and not s_iq:
        st.info("اكتب في أحد حقول البحث"); return

    results = [w for w in workers if
        (s_name and s_name.lower() in w["name"].lower()) or
        (s_iq and s_iq in w.get("iqama",""))
    ]
    if not results:
        st.warning("لم يُعثر على نتائج"); return

    for w in results:
        status = get_status(w)
        color  = STATUS_COLORS.get(status,"#666")
        fn,fe  = get_fail_n(w), get_fail_e(w)
        stag   = get_stagnant(w)
        with st.expander(f"👤 {w['name']} — {w.get('iqama','')}", expanded=True):
            c1,c2,c3,c4 = st.columns(4)
            c1.markdown(f'<span style="background:{color}22;color:{color};padding:5px 12px;border-radius:12px;font-weight:700;">{status}</span>', unsafe_allow_html=True)
            c2.metric("رسوب نظري", fn)
            c3.metric("رسوب عملي", fe)
            c4.metric("أيام التعطل", stag if isinstance(stag,int) else "لم يبدأ")
            if w.get("notes"): st.info(f"📝 {w['notes']}")
            appts = get_appointments([w])
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
        login_page(); return

    user = st.session_state.user
    role = user["role"]

    # تحميل البيانات من Supabase
    workers = db_get_workers()
    note    = db_get_note()

    with st.sidebar:
        st.markdown(f"""
        <div style="text-align:center;padding:15px 0;">
            <div style="font-size:40px;">🪪</div>
            <h3 style="color:white;margin:5px 0;">قتاد اللوجستية</h3>
            <div style="background:#2E5496;padding:6px 12px;border-radius:8px;margin:8px 0;">
                <span style="font-size:13px;">{ROLES[role]['label']}: {user['name']}</span>
            </div>
            <small style="color:#FFFFFF88;">{datetime.now().strftime('%Y/%m/%d %H:%M')}</small>
        </div>""", unsafe_allow_html=True)

        st.markdown("---")
        page = st.radio("", ["🏠 الرئيسية","📋 المتابعة","📅 المواعيد","📊 المؤشرات","🔍 البحث"], label_visibility="hidden")

        if ROLES[role]["can_edit"]:
            st.markdown("---")
            new_note = st.text_area("📢 ملاحظات الشركة", value=note, height=80, key="cn")
            if st.button("💾 حفظ", use_container_width=True):
                db_save_note(new_note)
                st.success("✅")

        st.markdown("---")
        if st.button("🚪 خروج", use_container_width=True):
            for k in ["logged_in","user"]: st.session_state.pop(k,None)
            st.rerun()

    if page   == "🏠 الرئيسية": dashboard_page(workers, note)
    elif page == "📋 المتابعة":  tracking_page(workers, role)
    elif page == "📅 المواعيد":  schedule_page(workers)
    elif page == "📊 المؤشرات": indicators_page(workers)
    elif page == "🔍 البحث":    search_page(workers)

if __name__ == "__main__":
    main()
