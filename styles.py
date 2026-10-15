"""Puzzle World visual style."""
CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=Outfit:wght@500;600;700;800&display=swap');
:root { --indigo:#5146db; --ink:#192447; --cyan:#41d9e5; }
html, body, [class*="css"], [data-testid="stApp"] { font-family:'DM Sans',sans-serif; }
[data-testid="stApp"] { background:linear-gradient(145deg,#f7f8ff 0%,#ecf5ff 55%,#f9fbff 100%); color:var(--ink); }
[data-testid="stSidebar"] { background:linear-gradient(180deg,#25216c,#493fbe); }
[data-testid="stSidebar"] * { color:#fff !important; }
h1,h2,h3 { font-family:'Outfit',sans-serif; letter-spacing:-.025em; }
h1 { color:#242268 !important; }
.block-container { max-width:1250px; padding-top:2.2rem; }
.pw-kicker { color:#635bd2; font-size:.82rem; font-weight:800; letter-spacing:.16em; text-transform:uppercase; }
.pw-hero { padding:2.5rem 2.8rem; border-radius:28px; background:linear-gradient(110deg,#342c98,#5f51df 62%,#3c87d9); color:white; box-shadow:0 18px 46px rgba(47,50,136,.18); }
.pw-hero h1 { color:white !important; font-size:3rem; line-height:1.1; margin:.5rem 0; }
.pw-hero p { color:#e6e6ff; font-size:1.1rem; max-width:650px; }
.pw-card { background:white; padding:1.35rem 1.5rem; border:1px solid #e9ebf8; border-radius:20px; box-shadow:0 8px 28px rgba(33,43,102,.06); margin:.4rem 0 1rem; }
.pw-card h3 { margin:0 0 .5rem; color:#292d69; }
.pw-label { font-size:.75rem; font-weight:800; letter-spacing:.14em; color:#6663bd; text-transform:uppercase; }
[data-testid="stBaseButton-secondary"] { background:#fff !important; color:#37339a !important; border:1px solid #d8dcf3 !important; border-radius:12px; font-weight:700; }
[data-testid="stBaseButton-primary"] { background:#5548dc !important; color:white !important; border:0 !important; border-radius:12px; font-weight:700; }
[data-testid="stBaseButton-secondary"] *, [data-testid="stBaseButton-primary"] * { color:inherit !important; }
[data-testid="stMetric"] { background:white; padding:1rem; border-radius:16px; border:1px solid #e6e8f6; }
</style>
"""
