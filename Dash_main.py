import os
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

_DIR = os.path.dirname(os.path.abspath(__file__))

# ── Page config ──
st.set_page_config(page_title="Car Insurance Analytics", layout="wide", initial_sidebar_state="collapsed")

# ── Google Font via link (non-blocking, unlike @import) ──
st.markdown('<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin><link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap" rel="stylesheet">', unsafe_allow_html=True)

# ── Zero-scroll dark theme CSS ──
st.markdown("""
<style>
    :root {
        --bg: #0a0e1a; --card: #111827; --accent: #6366f1; --accent2: #a78bfa;
        --accent3: #818cf8; --txt: #f1f5f9; --txt2: #94a3b8; --muted: #64748b;
        --border: #2d3148;
    }

    /* Hide streamlit chrome — fully removed from layout */
    #MainMenu, footer, header { display: none !important; }
    div[data-testid="stToolbar"] { display: none !important; }
    div[data-testid="stDecoration"] { display: none !important; }
    div[data-testid="stStatusWidget"] { display: none !important; }

    /* Nuke every possible top padding source */
    div[data-testid="stAppViewBlockContainer"] { padding-top: 0 !important; margin-top: 0 !important; }
    div[data-testid="stAppViewContainer"] { padding-top: 0 !important; margin-top: 0 !important; }
    div[data-testid="stVerticalBlockBorderWrapper"] { padding-top: 0 !important; margin-top: 0 !important; }
    div[data-testid="stVerticalBlock"] { padding: 0 !important; margin-top: 0 !important; row-gap: 0.3rem !important; }
    section.main { padding-top: 0 !important; margin-top: 0 !important; }
    section.main > div { padding-top: 0 !important; margin-top: 0 !important; }
    .main > div:first-child { padding-top: 0 !important; margin-top: 0 !important; }
    .stApp > div:first-child { padding-top: 0 !important; margin-top: 0 !important; }
    .stMainBlockContainer { padding-top: 0 !important; margin-top: 0 !important; }

    /* Force viewport fit — no scroll */
    html, body, .stApp { height: 100vh !important; max-height: 100vh !important; overflow: hidden !important; margin: 0 !important; padding: 0 !important; }
    .stApp { background: var(--bg) !important; font-family: 'Inter', sans-serif !important; }
    .block-container {
        padding: 0 0.5rem 0.3rem 0.5rem !important;
        max-width: 100% !important; max-height: 100vh !important; overflow: hidden !important;
        margin-top: 0 !important;
    }

    /* Nuke all spacing */
    .element-container { margin: 0 !important; padding: 0 !important; }
    .stPlotlyChart { margin: 0 !important; padding: 0 !important; }
    div[data-testid="stVerticalBlock"] > div { gap: 0rem !important; margin: 0 !important; padding: 0 !important; }
    div[data-testid="column"] { padding: 0 0.4rem !important; }
    div[data-testid="stHorizontalBlock"] { gap: 0.5rem !important; align-items: center !important; margin: 0 !important; padding: 0 !important; }
    div[data-testid="stVerticalBlockBorderWrapper"] > div { padding: 0 !important; margin: 0 !important; }
    div[data-testid="stElementContainer"] { margin: 0 !important; padding: 0 !important; }
    .stMarkdown { margin: 0 !important; padding: 0 !important; }
    iframe { display: block !important; }

    /* Title */
    .dash-title {
        font-size: 1.3rem; font-weight: 800; margin: 0; padding: 0.1rem 0; line-height: 1; white-space: nowrap;
        background: linear-gradient(135deg, #6366f1, #a78bfa);
        -webkit-background-clip: text; -webkit-text-fill-color: transparent;
        background-clip: text;
    }

    /* KPI bar */
    .kpi-bar { display:flex; align-items:center; gap:0.6rem; padding:0.15rem 0; }
    .kpi-item {
        display:flex; flex-direction:column; align-items:center; justify-content:center; line-height:1.3;
        min-width:4rem; padding:0.35rem 0.7rem;
        background:rgba(45,49,72,0.55); border-radius:4px;
        border:1px solid rgba(45,49,72,0.9);
    }
    .kpi-label { display:block; width:100%; font-size:0.55rem; color:var(--muted); text-transform:uppercase; letter-spacing:0.04em; font-weight:600; white-space:nowrap; text-align:center; }
    .kpi-value { display:block; width:100%; font-size:0.9rem; color:var(--txt); font-weight:700; white-space:nowrap; text-align:center; }
    .kpi-delta-pos { font-size:0.5rem; color:#22c55e; }
    .kpi-delta-neg { font-size:0.5rem; color:#ef4444; }
    .kpi-sep { color:var(--border); font-size:0.8rem; margin:0 0.4rem; }

    /* Filter button — match KPI chip height */
    .stPopover button {
        padding: 0.35rem 0.6rem !important; font-size: 0.6rem !important;
        background: rgba(45,49,72,0.55) !important; color: var(--txt2) !important;
        border: 1px solid rgba(45,49,72,0.9) !important; border-radius: 4px !important;
        min-height: 0 !important; line-height: 1.25 !important;
        font-weight: 600 !important; letter-spacing: 0.03em !important;
        text-transform: uppercase !important; white-space: nowrap !important;
        transition: border-color 0.2s, color 0.2s, box-shadow 0.2s !important;
    }
    /* Active filter highlight applied via JS when label contains · */
    .stPopover button.filter-active-btn {
        border-color: var(--accent) !important;
        color: var(--accent2) !important;
        box-shadow: 0 0 6px rgba(99,102,241,0.4) !important;
        background: rgba(99,102,241,0.12) !important;
    }
    .stPopover { display:flex; align-items:center; height:100%; }
    .stButton > button {
        padding: 0 0.2rem !important; font-size: 0.4rem !important; border-radius: 2px !important;
        height: 1.05rem !important; min-height: 0 !important; line-height: 1 !important;
    }

    /* Sidebar */
    section[data-testid="stSidebar"] { width: 200px !important; }

    /* Kill dividers */
    hr { display: none !important; }

    /* Plotly modebar hidden */
    .modebar { display: none !important; }

    /* Scrollbar fallback */
    ::-webkit-scrollbar { width: 0; height: 0; }
</style>
""", unsafe_allow_html=True)

# ── Load data ──
@st.cache_data
def load_data():
    return pd.read_csv(os.path.join(_DIR, "carInsurance_data.csv"))

df = load_data()

# ── Session state ──
_age_min, _age_max = int(df["Age"].min()), int(df["Age"].max())
for key, default in [("age_filter", (_age_min, _age_max)),
                     ("marital_filter", []), ("education_filter", []),
                     ("communication_filter", []), ("month_filter", [])]:
    if key not in st.session_state:
        st.session_state[key] = default
# Clamp age_filter to actual data bounds in case the dataset was reloaded
lo, hi = st.session_state.age_filter
st.session_state.age_filter = (max(lo, _age_min), min(hi, _age_max))

# ── Active filter indicators ──
_active_filters = {
    "Age":  st.session_state.get("age_filter", (_age_min, _age_max)) != (_age_min, _age_max),
    "Mar":  bool(st.session_state.get("marital_filter")),
    "Edu":  bool(st.session_state.get("education_filter")),
    "Comm": bool(st.session_state.get("communication_filter")),
    "Mon":  bool(st.session_state.get("month_filter")),
}
_active_names = [k for k, v in _active_filters.items() if v]
_any_active   = bool(_active_names)
_filter_label = "⚙ Filters" + (f" · {len(_active_names)}" if _any_active else "")

# Highlight the popover button via JS when any filter is active
if _any_active:
    st.markdown("""
<script>
(function() {
    function highlight() {
        document.querySelectorAll('.stPopover button').forEach(function(btn) {
            if (btn.innerText.includes('\u00b7')) {
                btn.classList.add('filter-active-btn');
            } else {
                btn.classList.remove('filter-active-btn');
            }
        });
    }
    if (document.readyState === 'complete') { highlight(); }
    else { window.addEventListener('load', highlight); }
    setTimeout(highlight, 150);
})();
</script>
""", unsafe_allow_html=True)

# ── Single column for entire header row (HTML only, no buttons) ──
tc, fc = st.columns([9, 1], gap="small")
with fc:
    with st.popover(_filter_label, use_container_width=False):
        _dot = lambda k: ' <span style="color:#6366f1;font-size:0.55rem;">●</span>' if _active_filters.get(k) else ''
        st.markdown(f'**Age**{_dot("Age")}', unsafe_allow_html=True)
        st.session_state.age_filter = st.slider("", int(df["Age"].min()), int(df["Age"].max()), st.session_state.age_filter, label_visibility="collapsed")
        st.markdown(f'**Marital**{_dot("Mar")}', unsafe_allow_html=True)
        st.session_state.marital_filter = [o for o in sorted(df["Marital"].dropna().unique()) if st.checkbox(o, key=f"marital_{o}")]
        st.markdown(f'**Education**{_dot("Edu")}', unsafe_allow_html=True)
        st.session_state.education_filter = [o for o in df["Education"].dropna().astype(str).unique() if st.checkbox(o, key=f"edu_{o}")]
        st.markdown(f'**Communication**{_dot("Comm")}', unsafe_allow_html=True)
        st.session_state.communication_filter = [o for o in df["Communication"].dropna().astype(str).unique() if st.checkbox(o, key=f"comm_{o}")]
        st.markdown(f'**Month**{_dot("Mon")}', unsafe_allow_html=True)
        available = [m for m in ["jan","feb","mar","apr","may","jun","jul","aug","sep","oct","nov","dec"] if m in df["LastContactMonth"].dropna().unique().tolist()]
        if not isinstance(st.session_state.get("month_filter"), list):
            st.session_state.month_filter = []
        sel_m = list(st.session_state.month_filter)
        cols_m = st.columns(4)
        for i, month in enumerate(available):
            if cols_m[i % 4].button(f"{'✓ ' if month in sel_m else ''}{month[:3].title()}", key=f"month_btn_{month}"):
                new_sel = [m for m in sel_m if m != month] if month in sel_m else sel_m + [month]
                st.session_state.month_filter = new_sel
                st.rerun()
        st.divider()
        if st.button("↺ Reset"):
            for k in ["age_filter","marital_filter","education_filter","communication_filter","month_filter"]:
                st.session_state[k] = (int(df["Age"].min()), int(df["Age"].max())) if k == "age_filter" else []
            for key in [k for k in list(st.session_state.keys()) if k.startswith(("month_btn_","marital_","edu_","comm_"))]:
                del st.session_state[key]
            st.rerun()

# ── Apply filters ──
filtered_df = df.copy()
mn, mx = st.session_state.age_filter
filtered_df = filtered_df[(filtered_df["Age"] >= mn) & (filtered_df["Age"] <= mx)]
for col, filt in [("Marital","marital_filter"),("Education","education_filter"),
                  ("Communication","communication_filter"),("LastContactMonth","month_filter")]:
    if st.session_state[filt]:
        filtered_df = filtered_df[filtered_df[col].isin(st.session_state[filt])]

# ── Derived columns ──
filtered_df["CallStart"] = pd.to_datetime(filtered_df["CallStart"], format="%H:%M:%S", errors="coerce")
filtered_df["CallEnd"] = pd.to_datetime(filtered_df["CallEnd"], format="%H:%M:%S", errors="coerce")
filtered_df["CallDuration"] = (filtered_df["CallEnd"] - filtered_df["CallStart"]).dt.total_seconds()
filtered_df.loc[filtered_df["CallDuration"] < 0, "CallDuration"] += 86400
filtered_df["Age_Group"] = pd.cut(filtered_df["Age"], bins=[18,25,35,45,60,100], labels=["18-25","26-35","36-45","46-60","60+"])
dur_max = filtered_df["CallDuration"].max()
dur_upper = max(2000, dur_max + 1) if pd.notna(dur_max) else 2000
filtered_df["Duration_Bucket"] = pd.cut(filtered_df["CallDuration"], bins=[0,60,180,300,600,dur_upper], labels=["<1m","1-3m","3-5m","5-10m","10+m"])
# Reuse Duration_Bucket with coarser labels for the heatmap axis
max_d = filtered_df["CallDuration"].max()
bins_d = [-1, 60, 180, 600, max_d if pd.notna(max_d) and max_d > 600 else 601]
filtered_df["CallDurationBucket"] = pd.cut(filtered_df["CallDuration"], bins=bins_d, labels=["0-1m","1-3m","3-10m","10+m"])

# ── KPIs ──
total_n = len(filtered_df)
if total_n == 0:
    st.warning("No records match filters.")
    st.stop()
conv = int(filtered_df["CarInsurance"].sum())
cr = conv / total_n * 100
base_cr = df["CarInsurance"].mean() * 100
delta = cr - base_cr
repeat = filtered_df[filtered_df["NoOfContacts"] > 1].shape[0] / total_n * 100
avg_bal = filtered_df["Balance"].mean()
avg_bal = avg_bal if pd.notna(avg_bal) else 0
_ch_rates = filtered_df.groupby("Communication", observed=True)["CarInsurance"].mean().dropna()
best_ch = _ch_rates.idxmax() if not _ch_rates.empty else "N/A"

# ── Render title + KPI bar in one HTML line ──
delta_cls = "kpi-delta-pos" if delta >= 0 else "kpi-delta-neg"
delta_sym = "▲" if delta >= 0 else "▼"
with tc:  # tc is the wide left column
    st.markdown(f"""
<div style="display:flex;align-items:center;gap:0.6rem;padding:0.5rem 0 1.1rem 0;">
  <span class="dash-title">Car Insurance Analytics</span>
  <span class="kpi-sep">|</span>
  <span class="kpi-item"><span class="kpi-label">Leads</span><span class="kpi-value">{total_n:,}</span></span>
  <span class="kpi-item"><span class="kpi-label">Conv</span><span class="kpi-value">{conv:,}</span></span>
  <span class="kpi-item"><span class="kpi-label">Rate</span><span class="kpi-value">{cr:.1f}% <span class="{delta_cls}">{delta_sym}{abs(delta):.1f}%</span></span></span>
  <span class="kpi-item"><span class="kpi-label">Repeat</span><span class="kpi-value">{repeat:.1f}%</span></span>
  <span class="kpi-item"><span class="kpi-label">Avg Bal</span><span class="kpi-value">${avg_bal:,.0f}</span></span>
  <span class="kpi-item"><span class="kpi-label">Best Channel</span><span class="kpi-value">{best_ch.title()}</span></span>
</div>
""", unsafe_allow_html=True)

# ── Chart config ──
CH = 160  # chart height — sized to fill viewport with 3 rows + header
ACCENT = "#6366f1"
ACCENT2 = "#a78bfa"
ACCENT3 = "#818cf8"
PAL = ["#6366f1","#a78bfa","#22c55e","#f59e0b","#ef4444","#06b6d4","#ec4899","#8b5cf6"]
DL = dict(margin=dict(l=2,r=2,t=16,b=4), font=dict(size=7, color="#94a3b8", family="Inter"),
          title_font=dict(size=8, color="#e2e8f0", family="Inter"),
          paper_bgcolor="#111827", plot_bgcolor="#111827")

# ══════════════ ROW 1 — Conversion & Trends ══════════════
c1,c2,c3,c4 = st.columns([3,3,3,3], gap="small")

with c1:
    d = filtered_df.groupby("Duration_Bucket", observed=True)["CarInsurance"].mean()*100
    fig = go.Figure(go.Bar(x=d.index.astype(str), y=d.values,
        marker=dict(color=d.values, colorscale=[[0,"#312e81"],[1,"#a78bfa"]], line=dict(width=0)),
        text=[f"{v:.0f}%" for v in d.values], textposition="auto", textfont=dict(size=7, color="#e2e8f0")))
    fig.update_layout(**DL, height=CH, showlegend=False, title_text="Duration vs Conv%",
        yaxis=dict(showticklabels=False, showgrid=False, zeroline=False),
        xaxis=dict(tickfont=dict(size=7, color="#94a3b8")))
    st.plotly_chart(fig, use_container_width=True)

with c2:
    o = filtered_df.groupby("Outcome", observed=True)["CarInsurance"].mean()*100
    o = o.sort_values()
    fig = go.Figure(go.Bar(y=o.index.astype(str), x=o.values, orientation='h',
        marker=dict(color=["#ef4444" if v<25 else "#f59e0b" if v<50 else "#22c55e" for v in o.values], line=dict(width=0)),
        text=[f"{v:.1f}%" for v in o.values], textposition="auto", textfont=dict(size=7, color="#e2e8f0")))
    fig.update_layout(**DL, height=CH, showlegend=False, title_text="Outcome Conv%",
        xaxis=dict(showticklabels=False, showgrid=False, zeroline=False),
        yaxis=dict(tickfont=dict(size=7, color="#94a3b8")))
    st.plotly_chart(fig, use_container_width=True)

with c3:
    cm_d = filtered_df.groupby("Communication", observed=True)["CarInsurance"].agg(["mean","count"]).reset_index()
    cm_d["mean"] *= 100
    fig = go.Figure(go.Pie(labels=cm_d["Communication"], values=cm_d["count"], hole=0.6,
        marker=dict(colors=[ACCENT,ACCENT2,"#06b6d4"][:len(cm_d)], line=dict(color="#111827",width=2)),
        textinfo="percent", textfont=dict(size=8, color="#e2e8f0"),
        hovertemplate="%{label}<br>n=%{value}<br>Conv=%{customdata:.1f}%<extra></extra>",
        customdata=cm_d["mean"],
        domain=dict(x=[0,1], y=[0.18, 1])))
    fig.update_layout(**DL, height=CH, showlegend=True, title_text="Channel Mix",
        legend=dict(orientation="h", yanchor="bottom", y=0, xanchor="center", x=0.5,
                    font=dict(size=7, color="#e2e8f0"), bgcolor="rgba(0,0,0,0)"))
    st.plotly_chart(fig, use_container_width=True)

with c4:
    mo_map = {"jan":1,"feb":2,"mar":3,"apr":4,"may":5,"jun":6,"jul":7,"aug":8,"sep":9,"oct":10,"nov":11,"dec":12}
    mo = filtered_df.groupby("LastContactMonth", observed=True)["CarInsurance"].mean().reset_index()
    mo.columns = ["month","rate"]
    mo["rate"] *= 100
    mo["ord"] = mo["month"].map(mo_map)
    mo = mo.sort_values("ord")
    fig = go.Figure(go.Scatter(x=mo["month"], y=mo["rate"], mode="lines+markers",
        line=dict(color=ACCENT, width=2, shape="spline"),
        marker=dict(size=5, color=ACCENT, line=dict(color="#111827",width=1)),
        fill="tozeroy", fillcolor="rgba(99,102,241,0.08)",
        hovertemplate="%{x}: %{y:.1f}%<extra></extra>"))
    fig.update_layout(**DL, height=CH, showlegend=False, title_text="Monthly Trend",
        yaxis=dict(showticklabels=True, tickfont=dict(size=6, color="#64748b"), ticksuffix="%", showgrid=True, gridcolor="rgba(45,49,72,0.3)", zeroline=False),
        xaxis=dict(tickfont=dict(size=6, color="#94a3b8")))
    st.plotly_chart(fig, use_container_width=True)

# ══════════════ ROW 2 — Demographics & Segments ══════════════
c1,c2,c3,c4 = st.columns([2,4,3,3], gap="small")

with c1:
    ag = filtered_df.groupby("Age_Group", observed=True)["CarInsurance"].mean()*100
    fig = go.Figure(go.Bar(x=ag.index.astype(str), y=ag.values,
        marker=dict(color=ag.values, colorscale=[[0,"#134e4a"],[1,"#5eead4"]], line=dict(width=0)),
        text=[f"{v:.0f}%" for v in ag.values], textposition="auto", textfont=dict(size=7, color="#e2e8f0")))
    fig.update_layout(**DL, height=CH, showlegend=False, title_text="Age Group Conv%",
        yaxis=dict(showticklabels=False, showgrid=False, zeroline=False),
        xaxis=dict(tickfont=dict(size=7, color="#94a3b8")))
    st.plotly_chart(fig, use_container_width=True)

with c2:
    jk = filtered_df.groupby("Job", observed=True)["CarInsurance"].mean()*100
    jt = jk.nlargest(min(6, len(jk))).sort_values()
    fig = go.Figure(go.Bar(y=jt.index, x=jt.values, orientation='h',
        marker=dict(color=jt.values, colorscale=[[0,"#1e1b4b"],[1,"#c7d2fe"]], line=dict(width=0)),
        text=[f"{v:.1f}%" for v in jt.values], textposition="auto", textfont=dict(size=7, color="#e2e8f0")))
    fig.update_layout(**DL, height=CH, showlegend=False, title_text="Top Jobs Conv%",
        xaxis=dict(showticklabels=False, showgrid=False, zeroline=False),
        yaxis=dict(tickfont=dict(size=7, color="#94a3b8")))
    st.plotly_chart(fig, use_container_width=True)

with c3:
    edu = filtered_df.groupby("Education", observed=True).agg(conv=("CarInsurance","mean")).reset_index()
    edu["conv"] *= 100
    edu = edu.sort_values("conv")
    fig = go.Figure(go.Bar(y=edu["Education"], x=edu["conv"], orientation='h',
        marker=dict(color=edu["conv"], colorscale=[[0,"#1e1b4b"],[1,"#a5b4fc"]], line=dict(width=0)),
        text=[f"{v:.1f}%" for v in edu["conv"]], textposition="auto", textfont=dict(size=7, color="#e2e8f0")))
    fig.update_layout(**DL, height=CH, showlegend=False, title_text="Education Conv%",
        xaxis=dict(showticklabels=False, showgrid=False, zeroline=False),
        yaxis=dict(tickfont=dict(size=7, color="#94a3b8")))
    st.plotly_chart(fig, use_container_width=True)

with c4:
    hh = filtered_df.groupby("HHInsurance", observed=True)["CarInsurance"].mean()*100
    cl = filtered_df.groupby("CarLoan", observed=True)["CarInsurance"].mean()*100
    cats = ["No HH","HH Ins","No Loan","Loan"]
    vals = [hh.get(0,0), hh.get(1,0), cl.get(0,0), cl.get(1,0)]
    fig = go.Figure(go.Bar(x=cats, y=vals,
        marker=dict(color=["#3730a3",ACCENT,"#065f46","#22c55e"], line=dict(width=0)),
        text=[f"{v:.1f}%" for v in vals], textposition="auto", textfont=dict(size=7, color="#94a3b8")))
    fig.update_layout(**DL, height=CH, showlegend=False, title_text="Insurance & Loan Impact",
        yaxis=dict(showticklabels=False, showgrid=False, zeroline=False),
        xaxis=dict(tickfont=dict(size=7, color="#94a3b8")))
    st.plotly_chart(fig, use_container_width=True)

# ══════════════ ROW 3 — Contact Analysis ══════════════
c1,c2,c3 = st.columns([4,5,3], gap="small")

with c1:
    ht = filtered_df.groupby(["NoOfContacts","CallDurationBucket"], observed=True)["CarInsurance"].mean().reset_index()
    ht["CarInsurance"] *= 100
    pv = ht.pivot_table(index="CallDurationBucket", columns="NoOfContacts", values="CarInsurance", observed=True).fillna(0)
    fig = px.imshow(pv, color_continuous_scale=[[0,"#0a0e1a"],[0.3,"#312e81"],[0.6,"#6366f1"],[1,"#c7d2fe"]],
                    aspect="auto", height=CH, text_auto=".0f", labels=dict(color="Conv%"))
    fig.update_layout(**DL, title_text="Contacts x Duration", coloraxis_showscale=False,
        xaxis=dict(tickfont=dict(size=6, color="#94a3b8"), title=""),
        yaxis=dict(tickfont=dict(size=6, color="#94a3b8"), title=""))
    st.plotly_chart(fig, use_container_width=True)

with c2:
    g = filtered_df.groupby("NoOfContacts", observed=True).agg(total=("CarInsurance","count"), cv=("CarInsurance","mean")).reset_index()
    g["cv"] *= 100
    fig = make_subplots(specs=[[{"secondary_y": True}]])
    fig.add_trace(go.Bar(x=g["NoOfContacts"], y=g["total"], name="Vol",
        marker=dict(color="rgba(99,102,241,0.3)", line=dict(color=ACCENT,width=1))), secondary_y=False)
    fig.add_trace(go.Scatter(x=g["NoOfContacts"], y=g["cv"], name="Conv%", mode="lines+markers",
        line=dict(color="#22c55e",width=2), marker=dict(size=4, color="#22c55e")), secondary_y=True)
    fig.update_layout(**DL, height=CH, showlegend=True, title_text="Contacts Vol & Conv%",
        legend=dict(orientation="h", yanchor="top", y=0.98, xanchor="right", x=0.98, font=dict(size=6, color="#94a3b8"), bgcolor="rgba(0,0,0,0)"))
    fig.update_yaxes(showticklabels=False, showgrid=False, zeroline=False, secondary_y=False)
    fig.update_yaxes(showticklabels=False, showgrid=False, zeroline=False, secondary_y=True)
    fig.update_xaxes(tickfont=dict(size=6, color="#94a3b8"), title="")
    st.plotly_chart(fig, use_container_width=True)

with c3:
    bal_no = filtered_df[filtered_df["CarInsurance"]==0]["Balance"]
    bal_yes = filtered_df[filtered_df["CarInsurance"]==1]["Balance"]
    fig = go.Figure()
    fig.add_trace(go.Box(y=bal_no, name="No Conv", marker_color="#2d3148", line_color="#64748b",
        fillcolor="rgba(45,49,72,0.4)", boxmean=True))
    fig.add_trace(go.Box(y=bal_yes, name="Conv", marker_color=ACCENT, line_color=ACCENT2,
        fillcolor="rgba(99,102,241,0.25)", boxmean=True))
    q3 = max(bal_no.quantile(0.75) if len(bal_no) > 0 else 0,
             bal_yes.quantile(0.75) if len(bal_yes) > 0 else 0)
    fig.update_layout(**DL, height=CH, showlegend=False, title_text="Balance Distribution",
        yaxis=dict(tickfont=dict(size=6, color="#64748b"), showgrid=True, gridcolor="rgba(45,49,72,0.3)",
                   range=[-500, q3*3] if q3>0 else None),
        xaxis=dict(tickfont=dict(size=7, color="#94a3b8")))
    st.plotly_chart(fig, use_container_width=True)
