import streamlit as st
import duckdb
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime, timedelta
import random

# ─────────────────────────────────────────────
# PAGE CONFIG
# ─────────────────────────────────────────────
st.set_page_config(
    page_title="The Grand Library",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ─────────────────────────────────────────────
# CUSTOM CSS
# ─────────────────────────────────────────────
st.markdown("""
<style>
  @import url('https://fonts.googleapis.com/css2?family=EB+Garamond:ital,wght@0,400;0,600;1,400&family=Inter:wght@400;500;600&display=swap');

  html, body, [class*="css"] {
    font-family: 'Inter', sans-serif;
    background: #f9f8f5;
    color: #1a1a1a;
  }

  /* ── HEADER ── */
  .tgl-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 14px 0 12px 0;
    border-bottom: 1px solid #e0ddd8;
    margin-bottom: 22px;
  }
  .tgl-logo {
    font-family: 'EB Garamond', serif;
    font-size: 22px;
    font-style: italic;
    color: #1a1a1a;
    font-weight: 600;
  }
  .tgl-nav { display: flex; gap: 24px; }
  .tgl-nav a {
    font-size: 12px;
    font-weight: 600;
    letter-spacing: .08em;
    text-transform: uppercase;
    color: #555;
    text-decoration: none;
    cursor: pointer;
  }
  .tgl-nav a.active {
    color: #1a1a1a;
    border-bottom: 2px solid #1a1a1a;
    padding-bottom: 2px;
  }

  /* ── BREADCRUMB ── */
  .breadcrumb { font-size: 11px; color: #888; margin-bottom: 18px; letter-spacing:.04em; text-transform:uppercase; }
  .breadcrumb span { color: #bbb; margin: 0 5px; }

  /* ── BADGE ── */
  .badge-green {
    background: #2d6a3a; color: #fff;
    font-size: 10px; font-weight: 700;
    letter-spacing: .08em; padding: 3px 8px;
    border-radius: 2px; text-transform: uppercase;
    display: inline-block; margin-bottom: 10px;
  }
  .badge-red   { background:#b83232; color:#fff; font-size:10px; font-weight:700; letter-spacing:.08em; padding:3px 8px; border-radius:2px; text-transform:uppercase; display:inline-block; }
  .badge-orange{ background:#c97a1c; color:#fff; font-size:10px; font-weight:700; letter-spacing:.08em; padding:3px 8px; border-radius:2px; text-transform:uppercase; display:inline-block; }

  /* ── GAME TITLE ── */
  .game-publisher { font-size:11px; color:#888; letter-spacing:.06em; text-transform:uppercase; font-weight:600; margin-bottom:4px; }
  .game-title { font-family:'EB Garamond',serif; font-size:32px; font-weight:600; line-height:1.15; margin:0 0 6px 0; }

  /* ── PRICE DISPLAY ── */
  .price-label { font-size:10px; color:#888; text-transform:uppercase; letter-spacing:.08em; }
  .price-big   { font-size:30px; font-weight:700; color:#1a1a1a; }
  .price-save  { font-size:15px; color:#2d6a3a; font-weight:600; }

  /* ── MARKET SNAPSHOT ── */
  .snapshot-box {
    background:#fff;
    border:1px solid #e0ddd8;
    border-radius:8px;
    padding:16px 18px;
  }
  .snapshot-title { font-size:10px; font-weight:700; letter-spacing:.1em; text-transform:uppercase; color:#888; margin-bottom:14px; }
  .snap-grid { display:grid; grid-template-columns:1fr 1fr; gap:12px; }
  .snap-cell-label { font-size:9px; color:#aaa; text-transform:uppercase; letter-spacing:.08em; }
  .snap-cell-val   { font-size:16px; font-weight:700; color:#1a1a1a; }
  .snap-cell-val.green { color:#2d6a3a; }

  /* ── BUTTONS ── */
  .btn-primary {
    background:#2a1f1f; color:#fff;
    border:none; border-radius:5px;
    padding:11px 20px; font-size:13px; font-weight:600;
    cursor:pointer; display:inline-flex; align-items:center; gap:7px;
  }
  .btn-secondary {
    background:#fff; color:#333;
    border:1px solid #ccc; border-radius:5px;
    padding:10px 16px; font-size:13px; font-weight:500;
    cursor:pointer; display:inline-flex; align-items:center; gap:6px;
  }

  /* ── DEAL ROW ── */
  .deal-header {
    display:flex; justify-content:space-between; align-items:center;
    margin-bottom:12px;
  }
  .deal-title { font-size:16px; font-weight:700; }
  .sellers-tag { font-size:11px; color:#888; }
  .deal-row {
    display:flex; justify-content:space-between; align-items:center;
    padding:12px 14px; border:1px solid #eee; border-radius:7px;
    margin-bottom:8px; background:#fff;
  }
  .deal-seller { font-size:14px; font-weight:600; }
  .deal-status-green { font-size:11px; color:#2d6a3a; }
  .deal-status-red   { font-size:11px; color:#b83232; }
  .deal-price { font-size:17px; font-weight:700; }
  .deal-ship  { font-size:11px; color:#888; }
  .deal-btn-buy   { background:#2a1f1f; color:#fff; border:none; border-radius:4px; padding:7px 12px; font-size:12px; cursor:pointer; }
  .deal-btn-oos   { background:#eee;    color:#aaa; border:none; border-radius:4px; padding:7px 12px; font-size:12px; cursor:default; }

  /* ── SECTION HEADINGS ── */
  .section-header {
    display:flex; justify-content:space-between; align-items:baseline;
    border-top:2px solid #1a1a1a; padding-top:14px; margin: 28px 0 18px 0;
  }
  .section-heading { font-size:19px; font-weight:700; }
  .section-link    { font-size:11px; color:#888; letter-spacing:.06em; text-transform:uppercase; cursor:pointer; }

  /* ── CARD ── */
  .game-card { background:#fff; border:1px solid #e8e5e0; border-radius:8px; overflow:hidden; }
  .card-img   { width:100%; height:175px; object-fit:cover; background:#ddd; }
  .card-body  { padding:12px; }
  .card-tag   { font-size:9px; color:#888; text-transform:uppercase; letter-spacing:.08em; }
  .card-name  { font-size:14px; font-weight:700; margin:2px 0; }
  .card-price { font-size:14px; font-weight:700; }
  .card-stock-green  { font-size:10px; color:#2d6a3a; font-weight:600; }
  .card-stock-red    { font-size:10px; color:#b83232; font-weight:600; }
  .card-stock-orange { font-size:10px; color:#c97a1c; font-weight:600; }

  /* ── SEARCH ── */
  .search-bar input {
    border:1px solid #ddd !important;
    border-radius:6px !important;
    font-size:14px !important;
  }

  /* ── FILTER PILL ── */
  .filter-pill {
    display:inline-block; background:#f0ede8; border:1px solid #ddd;
    border-radius:20px; padding:4px 12px; font-size:12px; margin:3px; cursor:pointer;
  }
  .filter-pill.active { background:#2a1f1f; color:#fff; border-color:#2a1f1f; }

  /* hide streamlit branding */
  #MainMenu, footer, header { visibility: hidden; }
  .block-container { padding-top: 1rem; max-width:1200px; }

  /* ── FOOTER ── */
  .tgl-footer {
    margin-top:60px; padding:20px 0; border-top:1px solid #e0ddd8;
    display:flex; justify-content:space-between; align-items:center;
  }
  .tgl-footer-logo { font-family:'EB Garamond',serif; font-style:italic; font-size:18px; }
  .tgl-footer-links { display:flex; gap:16px; }
  .tgl-footer-links a { font-size:12px; color:#888; text-decoration:none; }
  .tgl-footer-copy { font-size:11px; color:#bbb; }
</style>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────────
# DATABASE SETUP
# ─────────────────────────────────────────────
@st.cache_resource
def get_db():
    con = duckdb.connect(":memory:")
    _seed_db(con)
    return con


def _seed_db(con: duckdb.DuckDBPyConnection):
    con.execute("""
    CREATE TABLE IF NOT EXISTS games (
        id INTEGER PRIMARY KEY,
        name VARCHAR,
        publisher VARCHAR,
        category VARCHAR,
        description VARCHAR,
        image_url VARCHAR,
        avg_rating DOUBLE,
        min_players INTEGER,
        max_players INTEGER,
        play_time INTEGER,
        complexity DOUBLE
    )""")

    con.execute("""
    CREATE TABLE IF NOT EXISTS prices (
        id INTEGER PRIMARY KEY,
        game_id INTEGER,
        date DATE,
        price DOUBLE
    )""")

    con.execute("""
    CREATE TABLE IF NOT EXISTS sellers (
        id INTEGER PRIMARY KEY,
        game_id INTEGER,
        seller_name VARCHAR,
        price DOUBLE,
        in_stock BOOLEAN,
        shipping VARCHAR
    )""")

    con.execute("""
    CREATE TABLE IF NOT EXISTS expansions (
        id INTEGER PRIMARY KEY,
        base_game_id INTEGER,
        name VARCHAR,
        price DOUBLE,
        image_url VARCHAR,
        stock_status VARCHAR
    )""")

    con.execute("""
    CREATE TABLE IF NOT EXISTS watchlist (
        id INTEGER PRIMARY KEY,
        game_id INTEGER,
        added_date DATE
    )""")

    # ── games ──────────────────────────────────────────
    games = [
        (1,  "Root: A Game of Woodland Might and Right", "Leder Games",   "Strategy",   "An asymmetric woodland war game of adventure and war.",  "🌲", 4.7, 2, 4, 90,  3.7),
        (2,  "Everdell",                                 "Starling Games", "Strategy",   "Build a city of critters and constructions in an enchanting woodland.",  "🍂", 4.6, 1, 4, 80, 2.8),
        (3,  "Oath: Chronicles of Empire",               "Leder Games",   "Strategy",   "A game of empire and exile for 1–6 players.",           "⚔️", 4.5, 1, 6, 120, 4.2),
        (4,  "Pax Pamir: 2nd Edition",                  "Wehrlegig",     "Strategy",   "Players assume the role of Afghan leaders navigating the power struggle.", "🏔️", 4.7, 1, 5, 120, 4.4),
        (5,  "Ahoy",                                    "Leder Games",   "Asymmetric", "An asymmetric game of piracy and plunder.",              "⛵", 4.3, 2, 4, 60,  2.9),
        (6,  "Wingspan",                                 "Stonemaier",    "Engine",     "Attract a network of birds to your wildlife preserve.",  "🦅", 4.8, 1, 5, 70,  2.3),
        (7,  "Gloomhaven",                               "Cephalofair",   "Dungeon",    "A game of tactical combat in a persistent dungeon world.","🗡️", 4.9, 1, 4, 120, 3.9),
        (8,  "Spirit Island",                            "Greater Than",  "Cooperative","Powerful Island Spirits team up to drive colonizers away.","🌊", 4.8, 1, 4, 120, 3.8),
        (9,  "Terraforming Mars",                        "FryxGames",     "Engine",     "Compete to terraform and claim Mars as your own.",       "🔴", 4.6, 1, 5, 120, 3.2),
        (10, "Scythe",                                   "Stonemaier",    "Strategy",   "Lead your faction to dominance in an alternate 1920s Europe.","⚙️", 4.7, 1, 5, 115, 3.4),
    ]
    for g in games:
        try:
            con.execute("INSERT INTO games VALUES (?,?,?,?,?,?,?,?,?,?,?)", g)
        except Exception:
            pass

    # ── historical prices (1 year, game 1) ─────────────
    random.seed(42)
    base = datetime(2024, 1, 1)
    price = 55.0
    for i in range(365):
        d = base + timedelta(days=i)
        price += random.uniform(-2.5, 2.5)
        price = max(34.99, min(65.0, price))
        try:
            con.execute("INSERT INTO prices VALUES (?,?,?,?)", (i, 1, d.date(), round(price, 2)))
        except Exception:
            pass

    # prices for other games
    base_prices = {2:59.99, 3:72.50, 4:85.00, 5:29.99, 6:55.00, 7:140.00, 8:89.00, 9:59.00, 10:79.99}
    pid = 365
    for gid, bp in base_prices.items():
        p = bp
        for i in range(365):
            d = base + timedelta(days=i)
            p += random.uniform(-3, 3)
            p = max(bp*0.6, min(bp*1.2, p))
            try:
                con.execute("INSERT INTO prices VALUES (?,?,?,?)", (pid, gid, d.date(), round(p,2)))
            except Exception:
                pass
            pid += 1

    # ── sellers ────────────────────────────────────────
    seller_data = [
        (1, 1, "Amazon",          34.99, True,  "Free Ship"),
        (2, 1, "Miniature Market", 39.99, False, "-$10 ship"),
        (3, 1, "BoardGameBliss",  42.50, True,  "Free Ship"),
        (4, 1, "CoolStuffInc",    38.00, True,  "$4.99 ship"),
        (5, 2, "Amazon",          54.99, True,  "Free Ship"),
        (6, 2, "Miniature Market", 57.00, True,  "Free Ship"),
        (7, 3, "Noble Knight",    68.00, True,  "$5 ship"),
        (8, 4, "Amazon",          80.00, True,  "Free Ship"),
        (9, 5, "Amazon",          27.99, True,  "Free Ship"),
        (10,6, "Amazon",          49.99, True,  "Free Ship"),
    ]
    for s in seller_data:
        try:
            con.execute("INSERT INTO sellers VALUES (?,?,?,?,?,?)", s)
        except Exception:
            pass

    # ── expansions ────────────────────────────────────
    exp_data = [
        (1, 1, "The Riverfolk Expansion",  32.00, "🦦", "IN STOCK"),
        (2, 1, "The Underworld Expansion", 34.95, "🌑", "IN STOCK"),
        (3, 1, "The Marauder Expansion",   39.99, "⚔️", "LOW STOCK"),
        (4, 1, "The Landmarks Pack",       19.99, "🗺️", "IN STOCK"),
        (5, 2, "Spirecrest Expansion",     45.00, "🏔️", "IN STOCK"),
        (6, 2, "Pearlbrook Expansion",     40.00, "🦀", "OUT OF STOCK"),
        (7, 6, "European Expansion",       30.00, "🦢", "IN STOCK"),
        (8, 6, "Oceania Expansion",        30.00, "🦜", "IN STOCK"),
    ]
    for e in exp_data:
        try:
            con.execute("INSERT INTO expansions VALUES (?,?,?,?,?,?)", e)
        except Exception:
            pass


# ─────────────────────────────────────────────
# DATA HELPERS
# ─────────────────────────────────────────────
def get_game(con, game_id):
    return con.execute("SELECT * FROM games WHERE id=?", [game_id]).fetchdf()

def get_all_games(con):
    return con.execute("SELECT * FROM games").fetchdf()

def get_price_history(con, game_id, months=12):
    cutoff = (datetime.now() - timedelta(days=months*30)).date()
    return con.execute(
        "SELECT date, price FROM prices WHERE game_id=? AND date>=? ORDER BY date",
        [game_id, cutoff]
    ).fetchdf()

def get_market_snapshot(con, game_id):
    return con.execute("""
        SELECT
            MAX(price) as high,
            MIN(price) as low,
            ROUND(AVG(price),2) as avg
        FROM prices WHERE game_id=?
    """, [game_id]).fetchone()

def get_sellers(con, game_id):
    return con.execute(
        "SELECT * FROM sellers WHERE game_id=? ORDER BY price",
        [game_id]
    ).fetchdf()

def get_expansions(con, game_id):
    return con.execute(
        "SELECT * FROM expansions WHERE base_game_id=?",
        [game_id]
    ).fetchdf()

def get_similar_games(con, game_id, category, limit=4):
    return con.execute(
        "SELECT * FROM games WHERE id!=? AND (category=? OR publisher IN (SELECT publisher FROM games WHERE id=?)) LIMIT ?",
        [game_id, category, game_id, limit]
    ).fetchdf()

def get_deals(con):
    return con.execute("""
        SELECT s.*, g.name as game_name, g.image_url
        FROM sellers s
        JOIN games g ON g.id = s.game_id
        WHERE s.in_stock = true
        ORDER BY s.price ASC
        LIMIT 20
    """).fetchdf()

def get_watchlist(con):
    return con.execute("""
        SELECT g.*, w.added_date,
               (SELECT MIN(price) FROM sellers WHERE game_id=g.id AND in_stock=true) as current_price
        FROM watchlist w
        JOIN games g ON g.id = w.game_id
    """).fetchdf()


# ─────────────────────────────────────────────
# UI COMPONENTS
# ─────────────────────────────────────────────
def render_header(page):
    pages = ["CATALOG", "DEALS", "WATCHLIST", "LIBRARY"]
    links = " ".join([
        f'<a class="{"active" if p==page else ""}">{p}</a>'
        for p in pages
    ])
    st.markdown(f"""
    <div class="tgl-header">
      <div class="tgl-logo">The Grand Library</div>
      <nav class="tgl-nav">{links}</nav>
      <div style="font-size:18px;color:#888">🔔 &nbsp; 👤</div>
    </div>
    """, unsafe_allow_html=True)


def render_price_chart(df, current_price):
    if df.empty:
        return
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=df["date"], y=df["price"],
        mode="lines",
        line=dict(color="#2d6a3a", width=2),
        fill="tozeroy",
        fillcolor="rgba(45,106,58,0.08)",
        hovertemplate="$%{y:.2f}<br>%{x|%b %d, %Y}<extra></extra>",
    ))
    # highlight current price
    last_x = df["date"].iloc[-1]
    fig.add_annotation(
        x=last_x, y=current_price,
        text=f"<b>${current_price:.2f} Now</b>",
        showarrow=True, arrowhead=2, arrowcolor="#2a1f1f",
        bgcolor="#2a1f1f", font=dict(color="white", size=11),
        borderpad=5, ax=-70, ay=-30,
    )
    fig.update_layout(
        height=220,
        margin=dict(l=10, r=10, t=10, b=10),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        xaxis=dict(showgrid=False, zeroline=False, tickfont=dict(size=11, color="#aaa"), tickformat="%b %y"),
        yaxis=dict(showgrid=True, gridcolor="#f0ede8", zeroline=False, tickprefix="$", tickfont=dict(size=11, color="#aaa")),
        showlegend=False,
    )
    st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})


def render_deal_rows(sellers_df):
    for _, row in sellers_df.iterrows():
        status_html = (
            '<span class="deal-status-green">● IN STOCK</span>'
            if row["in_stock"]
            else '<span class="deal-status-red">● OUT OF STOCK</span>'
        )
        btn = (
            '<button class="deal-btn-buy">🔗</button>'
            if row["in_stock"]
            else '<button class="deal-btn-oos">✕</button>'
        )
        st.markdown(f"""
        <div class="deal-row">
          <div>
            <div class="deal-seller">🏪 {row["seller_name"]}</div>
            <div>{status_html}</div>
          </div>
          <div style="text-align:right">
            <div class="deal-price">${row["price"]:.2f}</div>
            <div class="deal-ship">{row["shipping"]}</div>
          </div>
          {btn}
        </div>
        """, unsafe_allow_html=True)


def stock_badge(status):
    if status == "IN STOCK":
        return '<span class="badge-green">In Stock</span>'
    elif status == "OUT OF STOCK":
        return '<span class="badge-red">Out of Stock</span>'
    else:
        return '<span class="badge-orange">Low Stock</span>'


def render_expansion_cards(exps_df):
    cols = st.columns(min(len(exps_df), 4))
    for i, (_, row) in enumerate(exps_df.iterrows()):
        with cols[i % len(cols)]:
            stock_col = "#2d6a3a" if row["stock_status"]=="IN STOCK" else ("#b83232" if row["stock_status"]=="OUT OF STOCK" else "#c97a1c")
            st.markdown(f"""
            <div class="game-card">
              <div style="height:170px;background:linear-gradient(135deg,#2a1f1f,#3a3030);
                          display:flex;align-items:center;justify-content:center;font-size:64px">
                {row["image_url"]}
              </div>
              <div class="card-body">
                <div class="card-name">{row["name"]}</div>
                <div style="display:flex;justify-content:space-between;align-items:center;margin-top:6px">
                  <span class="card-price">${row["price"]:.2f}</span>
                  <span style="font-size:10px;font-weight:700;color:{stock_col}">{row["stock_status"]}</span>
                </div>
              </div>
            </div>
            """, unsafe_allow_html=True)


def render_game_cards(games_df, con):
    cols = st.columns(min(len(games_df), 4))
    for i, (_, row) in enumerate(games_df.iterrows()):
        with cols[i % len(cols)]:
            cur_price = con.execute(
                "SELECT MIN(price) FROM sellers WHERE game_id=? AND in_stock=true",
                [row["id"]]
            ).fetchone()[0] or 0
            if st.button(f"{row['image_url']} {row['name']}", key=f"game_{row['id']}_{i}",
                         use_container_width=True):
                st.session_state.selected_game = row["id"]
                st.session_state.page = "CATALOG"
                st.rerun()

            st.markdown(f"""
            <div class="game-card" style="margin-top:-8px">
              <div style="height:155px;background:linear-gradient(135deg,#1a2a3a,#2a3a4a);
                          display:flex;align-items:center;justify-content:center;font-size:56px">
                {row["image_url"]}
              </div>
              <div class="card-body">
                <div class="card-tag">{row["category"]}</div>
                <div class="card-name">{row["name"]}</div>
                <div style="font-size:14px;font-weight:700;margin-top:4px">${cur_price:.2f}</div>
              </div>
            </div>
            """, unsafe_allow_html=True)


# ─────────────────────────────────────────────
# PAGES
# ─────────────────────────────────────────────
def page_game_detail(con, game_id):
    gdf = get_game(con, game_id)
    if gdf.empty:
        st.error("Game not found.")
        return
    g = gdf.iloc[0]

    sellers = get_sellers(con, game_id)
    snap = get_market_snapshot(con, game_id)
    hist = get_price_history(con, game_id)
    exps = get_expansions(con, game_id)
    similar = get_similar_games(con, game_id, g["category"])

    best_price = sellers[sellers["in_stock"]]["price"].min() if not sellers[sellers["in_stock"]].empty else None
    avg_price  = g["avg_rating"]

    st.markdown(f"""
    <div class="breadcrumb">
      CATALOG <span>›</span> {g["category"].upper()} <span>›</span> {g["name"].split(":")[0].upper()}
    </div>""", unsafe_allow_html=True)

    # ── TOP SECTION ────────────────────────────────
    col_img, col_info, col_snap = st.columns([2.5, 3.5, 2.5])

    with col_img:
        st.markdown(f"""
        <div style="background:linear-gradient(135deg,#1a2a1a,#2a3a2a);
                    border-radius:10px;height:280px;
                    display:flex;align-items:center;justify-content:center;
                    font-size:110px;border:1px solid #e0ddd8;position:relative">
          {g["image_url"]}
          <div style="position:absolute;top:10px;left:10px">
            <span class="badge-green">Lowest Price</span>
          </div>
        </div>
        """, unsafe_allow_html=True)
        # Thumbnails
        t_cols = st.columns(4)
        emojis = ["🌲","🗺️","🃏","⚔️"]
        for tc, em in zip(t_cols, emojis):
            with tc:
                st.markdown(f"""
                <div style="background:#f0ede8;border:1px solid #ddd;border-radius:5px;
                            height:55px;display:flex;align-items:center;justify-content:center;
                            font-size:22px;cursor:pointer">{em}</div>
                """, unsafe_allow_html=True)

    with col_info:
        list_price = snap[0] if snap else 59.99
        current_p  = best_price if best_price else 34.99
        savings    = list_price - current_p
        pct        = int(savings / list_price * 100) if list_price else 0

        st.markdown(f"""
        <div class="game-publisher">{g["publisher"]} · {g["category"]}</div>
        <div class="game-title">{g["name"]}</div>
        <hr style="border:none;border-top:1px solid #eee;margin:12px 0">
        <div class="price-label">Current Price</div>
        <div style="display:flex;align-items:baseline;gap:14px;margin-top:4px">
          <span class="price-big">${current_p:.2f}</span>
          <span class="price-save">-${savings:.2f} ({pct}%)</span>
        </div>
        <div style="margin-top:16px;display:flex;gap:10px">
          <button class="btn-primary">🛒 Best Deal: Amazon</button>
          <button class="btn-secondary">🔔 Watch Price</button>
          <button class="btn-secondary">♡</button>
        </div>
        <hr style="border:none;border-top:1px solid #eee;margin:18px 0 10px 0">
        <div style="display:flex;gap:24px">
          <div>
            <div style="font-size:10px;color:#aaa;text-transform:uppercase;letter-spacing:.08em">Players</div>
            <div style="font-size:14px;font-weight:600">{g["min_players"]}–{g["max_players"]}</div>
          </div>
          <div>
            <div style="font-size:10px;color:#aaa;text-transform:uppercase;letter-spacing:.08em">Play Time</div>
            <div style="font-size:14px;font-weight:600">{g["play_time"]} min</div>
          </div>
          <div>
            <div style="font-size:10px;color:#aaa;text-transform:uppercase;letter-spacing:.08em">Complexity</div>
            <div style="font-size:14px;font-weight:600">{g["complexity"]}/5</div>
          </div>
          <div>
            <div style="font-size:10px;color:#aaa;text-transform:uppercase;letter-spacing:.08em">Rating</div>
            <div style="font-size:14px;font-weight:600">⭐ {g["avg_rating"]}</div>
          </div>
        </div>
        """, unsafe_allow_html=True)

    with col_snap:
        st.markdown(f"""
        <div class="snapshot-box">
          <div class="snapshot-title">Market Snapshot</div>
          <div class="snap-grid">
            <div>
              <div class="snap-cell-label">1Y High</div>
              <div class="snap-cell-val">${snap[0]:.2f}</div>
            </div>
            <div>
              <div class="snap-cell-label">1Y Low</div>
              <div class="snap-cell-val green">${snap[1]:.2f}</div>
            </div>
            <div>
              <div class="snap-cell-label">Avg Price</div>
              <div class="snap-cell-val">${snap[2]:.2f}</div>
            </div>
            <div>
              <div class="snap-cell-label">Status</div>
              <div class="snap-cell-val green" style="font-size:14px">In Stock</div>
            </div>
          </div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<div style='height:24px'></div>", unsafe_allow_html=True)

    # ── PRICE CHART + LIVE DEALS ────────────────────
    col_chart, col_deals = st.columns([1.4, 1])

    with col_chart:
        # Period toggle
        period_col = st.columns([1,1,1,6])
        period = "12M"
        with period_col[0]:
            if st.button("1Y", key="p1y", use_container_width=True): period = "12M"
        with period_col[1]:
            if st.button("6M", key="p6m", use_container_width=True): period = "6M"
        with period_col[2]:
            if st.button("ALL", key="pall", use_container_width=True): period = "12M"

        months = 6 if period == "6M" else 12
        hist = get_price_history(con, game_id, months)
        st.markdown('<div style="font-size:13px;font-weight:700;margin-bottom:6px">Price Ledger</div>', unsafe_allow_html=True)
        render_price_chart(hist, current_p)

    with col_deals:
        n_sellers = len(sellers)
        st.markdown(f"""
        <div class="deal-header">
          <span class="deal-title">Live Deals</span>
          <span class="sellers-tag">{n_sellers} Sellers</span>
        </div>""", unsafe_allow_html=True)
        render_deal_rows(sellers)

    # ── EXPANSIONS ──────────────────────────────────
    if not exps.empty:
        st.markdown("""
        <div class="section-header">
          <span class="section-heading">Expansions & Add-ons</span>
          <span class="section-link">VIEW ALL</span>
        </div>""", unsafe_allow_html=True)
        render_expansion_cards(exps)

    # ── SIMILAR GAMES ───────────────────────────────
    if not similar.empty:
        st.markdown("""
        <div class="section-header">
          <span class="section-heading">Similar Games</span>
          <span class="section-link">Themed Recommendations</span>
        </div>""", unsafe_allow_html=True)
        render_game_cards(similar, con)


def page_catalog(con):
    st.markdown("### 🗂️ Game Catalog", unsafe_allow_html=False)

    # Search + filters
    sc1, sc2 = st.columns([3,1])
    with sc1:
        search = st.text_input("", placeholder="🔍  Search games…", label_visibility="collapsed", key="cat_search")
    with sc2:
        sort = st.selectbox("Sort by", ["Price: Low→High","Price: High→Low","Rating","Name"], label_visibility="collapsed")

    cats = ["All", "Strategy", "Engine", "Cooperative", "Dungeon", "Asymmetric"]
    sel_cat = st.radio("Category", cats, horizontal=True, label_visibility="collapsed")

    # Query
    query = "SELECT * FROM games WHERE 1=1"
    params = []
    if search:
        query += " AND (lower(name) LIKE ? OR lower(publisher) LIKE ?)"
        params += [f"%{search.lower()}%", f"%{search.lower()}%"]
    if sel_cat != "All":
        query += " AND category = ?"
        params.append(sel_cat)
    order = {"Price: Low→High":"id","Price: High→Low":"id DESC","Rating":"avg_rating DESC","Name":"name"}
    query += f" ORDER BY {order[sort]}"

    games = con.execute(query, params).fetchdf()

    st.markdown(f"<div style='font-size:12px;color:#888;margin-bottom:16px'>{len(games)} games found</div>", unsafe_allow_html=True)

    # Grid
    n_cols = 4
    for row_start in range(0, len(games), n_cols):
        chunk = games.iloc[row_start:row_start+n_cols]
        cols  = st.columns(n_cols)
        for col, (_, g) in zip(cols, chunk.iterrows()):
            with col:
                cur_price = con.execute(
                    "SELECT MIN(price) FROM sellers WHERE game_id=? AND in_stock=true",
                    [g["id"]]
                ).fetchone()[0] or 0
                if st.button(g["name"], key=f"cat_{g['id']}_{row_start}", use_container_width=True):
                    st.session_state.selected_game = g["id"]
                    st.rerun()
                st.markdown(f"""
                <div class="game-card" style="margin-top:-6px">
                  <div style="height:150px;background:linear-gradient(135deg,#1a2a3a,#2a3a4a);
                              display:flex;align-items:center;justify-content:center;font-size:52px">
                    {g["image_url"]}
                  </div>
                  <div class="card-body">
                    <div class="card-tag">{g["category"]} · {g["publisher"]}</div>
                    <div class="card-name">{g["name"]}</div>
                    <div style="display:flex;justify-content:space-between;align-items:center;margin-top:6px">
                      <span style="font-size:15px;font-weight:700">${cur_price:.2f}</span>
                      <span style="font-size:11px;color:#888">⭐ {g["avg_rating"]}</span>
                    </div>
                  </div>
                </div>
                """, unsafe_allow_html=True)


def page_deals(con):
    st.markdown("### 🏷️ Today's Best Deals", unsafe_allow_html=False)
    deals = get_deals(con)

    st.markdown(f"<div style='font-size:12px;color:#888;margin-bottom:16px'>{len(deals)} live listings across all sellers</div>", unsafe_allow_html=True)

    # Summary stats
    c1,c2,c3,c4 = st.columns(4)
    with c1:
        st.metric("Lowest Price", f"${deals['price'].min():.2f}")
    with c2:
        st.metric("Avg Deal Price", f"${deals['price'].mean():.2f}")
    with c3:
        st.metric("Active Sellers", deals['seller_name'].nunique())
    with c4:
        st.metric("In-Stock Games", deals[deals['in_stock']]['game_id'].nunique())

    st.markdown("<hr style='border:none;border-top:1px solid #eee;margin:18px 0'>", unsafe_allow_html=True)

    for _, row in deals.iterrows():
        col_a, col_b, col_c, col_d = st.columns([3,1.5,1.5,1])
        with col_a:
            st.markdown(f"**{row['game_name']}**  \n🏪 {row['seller_name']}")
        with col_b:
            st.markdown(f"**${row['price']:.2f}**")
        with col_c:
            st.markdown(f"🚚 {row['shipping']}")
        with col_d:
            if st.button("View →", key=f"deal_{row['id']}"):
                st.session_state.selected_game = row["game_id"]
                st.session_state.page = "CATALOG"
                st.rerun()
        st.divider()


def page_watchlist(con):
    st.markdown("### 🔔 Your Watchlist", unsafe_allow_html=False)
    wl = get_watchlist(con)
    if wl.empty:
        st.info("No games in your watchlist yet. Browse the catalog and click ♡ to add!")
        st.markdown("#### Suggested Games")
        games = con.execute("SELECT * FROM games LIMIT 4").fetchdf()
        render_game_cards(games, con)
    else:
        for _, g in wl.iterrows():
            c1,c2,c3 = st.columns([4,2,1])
            with c1:
                st.markdown(f"{g['image_url']} **{g['name']}**")
            with c2:
                st.markdown(f"${g['current_price']:.2f}" if g['current_price'] else "–")
            with c3:
                if st.button("View", key=f"wl_{g['id']}"):
                    st.session_state.selected_game = g["id"]
                    st.session_state.page = "CATALOG"
                    st.rerun()


def page_library(con):
    st.markdown("### 📚 Game Library", unsafe_allow_html=False)

    # Stats
    total = con.execute("SELECT COUNT(*) FROM games").fetchone()[0]
    total_sellers = con.execute("SELECT COUNT(DISTINCT seller_name) FROM sellers").fetchone()[0]
    best = con.execute("SELECT name, avg_rating FROM games ORDER BY avg_rating DESC LIMIT 1").fetchone()
    cheapest = con.execute("""
        SELECT g.name, MIN(s.price) as p FROM sellers s JOIN games g ON g.id=s.game_id
        WHERE s.in_stock=true GROUP BY g.name ORDER BY p LIMIT 1
    """).fetchone()

    c1,c2,c3,c4 = st.columns(4)
    with c1: st.metric("Total Games", total)
    with c2: st.metric("Active Sellers", total_sellers)
    with c3: st.metric("Top Rated", f"⭐ {best[1]}" if best else "–", best[0] if best else "")
    with c4: st.metric("Best Value", f"${cheapest[1]:.2f}" if cheapest else "–", cheapest[0] if cheapest else "")

    st.markdown("<hr style='border:none;border-top:1px solid #eee;margin:18px 0'>", unsafe_allow_html=True)

    # Full table from DuckDB
    df = con.execute("""
        SELECT g.name as "Game", g.publisher as "Publisher", g.category as "Category",
               g.avg_rating as "Rating", g.min_players || '–' || g.max_players as "Players",
               g.play_time as "Time (min)", g.complexity as "Complexity",
               COALESCE(MIN(CASE WHEN s.in_stock THEN s.price END), NULL) as "Best Price"
        FROM games g
        LEFT JOIN sellers s ON s.game_id = g.id
        GROUP BY g.name, g.publisher, g.category, g.avg_rating, g.min_players, g.max_players, g.play_time, g.complexity
        ORDER BY g.avg_rating DESC
    """).fetchdf()
    st.dataframe(df, use_container_width=True, hide_index=True)


# ─────────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────────
def main():
    con = get_db()

    if "page" not in st.session_state:
        st.session_state.page = "CATALOG"
    if "selected_game" not in st.session_state:
        st.session_state.selected_game = 1

    render_header(st.session_state.page)

    # ── NAV ────────────────────────────────────────
    nav_cols = st.columns([1,1,1,1,8])
    nav_labels = [("CATALOG","📚"),("DEALS","🏷️"),("WATCHLIST","🔔"),("LIBRARY","📖")]
    for i,(pg, icon) in enumerate(nav_labels):
        with nav_cols[i]:
            if st.button(f"{icon} {pg}", key=f"nav_{pg}", use_container_width=True,
                         type="primary" if st.session_state.page==pg else "secondary"):
                st.session_state.page = pg
                st.rerun()

    st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)

    # ── ROUTE ──────────────────────────────────────
    if st.session_state.page == "CATALOG":
        if st.session_state.selected_game:
            # Back button
            if st.button("← Back to Catalog"):
                st.session_state.selected_game = None
                st.rerun()
            page_game_detail(con, st.session_state.selected_game)
        else:
            page_catalog(con)
    elif st.session_state.page == "DEALS":
        page_deals(con)
    elif st.session_state.page == "WATCHLIST":
        page_watchlist(con)
    elif st.session_state.page == "LIBRARY":
        page_library(con)

    # ── FOOTER ─────────────────────────────────────
    st.markdown("""
    <div class="tgl-footer">
      <div>
        <div class="tgl-footer-logo">The Grand Library</div>
        <div class="tgl-footer-copy">© 2026 · Tabletop Price Index</div>
      </div>
      <div class="tgl-footer-links">
        <a>Partners</a><a>Terms</a><a>Privacy</a><a>API</a>
      </div>
    </div>
    """, unsafe_allow_html=True)


if __name__ == "__main__":
    main()