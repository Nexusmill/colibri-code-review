"""Visual system for the console: injected CSS + the masthead and the signature
'run meter'. Colours are the hummingbird-throat palette (teal -> violet) on a cool
near-black; Space Grotesk / Inter / JetBrains Mono."""
import html
import streamlit as st

TEAL = "#24C6AD"
VIOLET = "#7C6BFF"
TEXT = "#E6E9EF"
MUTED = "#9BA3B0"
LINE = "#2A2F38"

_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@500;600;700&family=Inter:wght@400;500;600&family=JetBrains+Mono:wght@400;500;600&display=swap');

html, body, [data-testid="stAppViewContainer"], .stMarkdown, p, div, span, label, input, textarea {
  font-family: 'Inter', system-ui, sans-serif;
}
h1, h2, h3, h4 { font-family: 'Space Grotesk', sans-serif; letter-spacing: -0.01em; }
code, pre, [data-testid="stMetricValue"] { font-family: 'JetBrains Mono', monospace; }

/* Hide Streamlit chrome GRANULARLY - never the whole stToolbar: in Streamlit 1.59+
   the sidebar-reopen button (stExpandSidebarButton) lives INSIDE the toolbar, and
   blanket-hiding it left a collapsed sidebar with no way to reopen it. */
#MainMenu, footer, [data-testid="stMainMenu"], [data-testid="stAppDeployButton"],
[data-testid="stStatusWidget"] { visibility: hidden; height: 0; }
[data-testid="stExpandSidebarButton"], [data-testid="stSidebarCollapseButton"] {
  visibility: visible !important; }
[data-testid="stAppViewContainer"] {
  background: radial-gradient(1100px 480px at 12% -12%, #12161d 0%, #0C0E12 62%);
}
.block-container { padding-top: 2.2rem; }

/* sidebar = instrument console */
[data-testid="stSidebar"] { background: #14171D; border-right: 1px solid #2A2F38; }
[data-testid="stSidebar"] .stMarkdown h3 {
  font-family: 'JetBrains Mono', monospace; font-size: 11px; letter-spacing: 0.18em;
  text-transform: uppercase; color: #9BA3B0; border-bottom: 1px solid #2A2F38;
  padding-bottom: 6px; margin: 14px 0 4px;
}

/* primary action = hummingbird-throat gradient */
.stButton button[kind="primary"], button[data-testid="baseButton-primary"] {
  background: linear-gradient(90deg, #24C6AD, #7C6BFF); color: #08090C; border: 0;
  font-weight: 600; letter-spacing: 0.01em;
}
.stButton button[kind="primary"]:hover { filter: brightness(1.08); }
.stButton button[kind="secondary"] { background: #1C2027; color: #E6E9EF; border: 1px solid #2A2F38; }

[data-testid="stExpander"] { border: 1px solid #2A2F38; border-radius: 8px; background: #14171D; }
[data-testid="stDataFrame"], [data-testid="stDataEditor"] { border: 1px solid #2A2F38; border-radius: 8px; }
hr { border-color: #2A2F38; }
[data-testid="stProgress"] > div > div > div { background: linear-gradient(90deg, #24C6AD, #7C6BFF); }
</style>
"""


def inject():
    st.markdown(_CSS, unsafe_allow_html=True)


def masthead(model):
    safe_model = html.escape(str(model))
    st.markdown(
        f"""<div style="display:flex;align-items:baseline;gap:14px;margin:0 0 10px;">
  <span style="font-family:'Space Grotesk';font-weight:700;font-size:30px;letter-spacing:-0.02em;color:{TEXT};">colibri</span>
  <span style="font-family:'JetBrains Mono';font-size:11px;letter-spacing:0.16em;text-transform:uppercase;color:{MUTED};">code&nbsp;review&nbsp;console</span>
  <span style="flex:1;height:1px;background:linear-gradient(90deg,{TEAL},{VIOLET},transparent);"></span>
  <span style="font-family:'JetBrains Mono';font-size:11px;color:{TEAL};">{safe_model}</span>
</div>""",
        unsafe_allow_html=True,
    )


def meter(n_files, tokens_in, max_out, price_in, price_out, unbounded):
    """The signature: a live instrument whose ceiling is set by the user's own token
    threshold. Shows the MAX possible spend for the current selection + settings."""
    in_cost = tokens_in * price_in / 1_000_000
    ceil = in_cost + n_files * max_out * price_out / 1_000_000
    reach = "unbounded reasoning" if unbounded else "bounded"
    sel = f"{n_files} file{'s' if n_files != 1 else ''}"
    st.markdown(
        f"""<div style="border:1px solid {LINE};border-radius:10px;background:
  linear-gradient(180deg,#161A21,#12151B);padding:14px 16px;margin:6px 0 12px;">
  <div style="display:flex;justify-content:space-between;align-items:center;">
    <span style="font-family:'JetBrains Mono';font-size:10px;letter-spacing:0.18em;text-transform:uppercase;color:{MUTED};">run meter · max spend</span>
    <span style="font-family:'JetBrains Mono';font-size:10px;color:{MUTED};">{reach}</span>
  </div>
  <div style="display:flex;align-items:baseline;gap:12px;margin-top:4px;">
    <span style="font-family:'JetBrains Mono';font-weight:600;font-size:30px;color:{TEXT};">&#8804;&nbsp;${ceil:,.2f}</span>
    <span style="font-family:'JetBrains Mono';font-size:12px;color:{MUTED};">{sel} &middot; {tokens_in:,} in tok &middot; &#8804;{max_out:,} out/file</span>
  </div>
  <div style="height:4px;border-radius:2px;margin-top:10px;background:linear-gradient(90deg,{TEAL},{VIOLET});opacity:{0.9 if n_files else 0.25};"></div>
  <div style="font-family:'JetBrains Mono';font-size:10px;color:{MUTED};margin-top:6px;">ceiling = input + (max output tokens x price out) x files &middot; actual is usually lower</div>
</div>""",
        unsafe_allow_html=True,
    )
