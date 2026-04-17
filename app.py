import os
import secrets
import sqlite3
import time
import json
import hashlib
import hmac
from datetime import datetime, timedelta
from functools import wraps

import requests
from flask import Flask, abort, flash, g, jsonify, redirect, render_template, request, send_from_directory, session, url_for
from werkzeug.security import check_password_hash, generate_password_hash


# Database configuration - use /tmp for Railway's ephemeral filesystem
if os.getenv("RAILWAY_ENVIRONMENT"):
    DB_PATH = "/tmp/store.db"
else:
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    DB_PATH = os.path.join(BASE_DIR, "store.db")

app = Flask(__name__)
app.config["SECRET_KEY"] = os.getenv("SECRET_KEY", "change-me-in-production")
app.config["ADMIN_PATH"] = os.getenv("ADMIN_PATH", "painel-interno-velocity-2026")
app.config["SILLIENT_PAY_ENABLED"] = os.getenv("SILLIENT_PAY_ENABLED", "false").lower() == "true"
app.config["SILLIENT_PAY_BASE_URL"] = os.getenv("SILLIENT_PAY_BASE_URL", "https://sandbox.sillientpay.example")
app.config["SILLIENT_PAY_API_KEY"] = os.getenv("SILLIENT_PAY_API_KEY", "")
app.config["SILLIENT_PAY_WEBHOOK_SECRET"] = os.getenv("SILLIENT_PAY_WEBHOOK_SECRET", "")
app.config["PRODUCTS_PER_PAGE"] = 12
app.config["PERMANENT_SESSION_LIFETIME"] = timedelta(hours=12)
app.config["SESSION_COOKIE_HTTPONLY"] = True
app.config["SESSION_COOKIE_SAMESITE"] = "Lax"
app.config["SESSION_COOKIE_SECURE"] = os.getenv("SESSION_COOKIE_SECURE", "false").lower() == "true"


def get_db():
    if "db" not in g:
        g.db = sqlite3.connect(DB_PATH)
        g.db.row_factory = sqlite3.Row
    return g.db


@app.teardown_appcontext
def close_db(_error):
    db = g.pop("db", None)
    if db is not None:
        db.close()


def ensure_column(db, table_name, column_name, column_def):
    columns = [row["name"] for row in db.execute(f"PRAGMA table_info({table_name})").fetchall()]
    if column_name not in columns:
        db.execute(f"ALTER TABLE {table_name} ADD COLUMN {column_name} {column_def}")


def bulk_seed_products():
    products = []
    
    # CAMISETAS
    camisetas = [
        ("Oversized Premium Black", "oversized-premium-black", "camisetas", "Camiseta oversized em algodão premium de alta gramatura. Corte moderno, caimento estruturado e estética minimalista.", 199.90, None, 80, 1, "Mais Vendido", "P,M,L,XL,XXL", "Preto", "NV-TEE-001-BK", 1, 0, 1),
        ("Oversized Premium White", "oversized-premium-white", "camisetas", "Camiseta oversized branca em algodão premium. Visual clean, caimento perfeito e versatilidade absoluta.", 199.90, 179.90, 75, 0, "Promo", "P,M,L,XL,XXL", "Branco", "NV-TEE-002-WH", 0, 1, 1),
        ("Washed Street Tee", "washed-street-tee", "camisetas", "Camiseta com efeito envelhecido premium. Textura única, visual usado autêntico e conforto incomparável.", 179.90, None, 60, 1, "Novo", "M,L,XL,XXL", "Cinza", "NV-TEE-003-GY", 1, 0, 0),
        ("Minimal Logo Tee", "minimal-logo-tee", "camisetas", "Camiseta minimalista com logo discreto. Elegância na simplicidade, qualidade na costura.", 159.90, None, 90, 1, None, "P,M,L,XL", "Preto", "NV-TEE-004-BK", 0, 0, 1),
        ("Heavy Cotton Tee", "heavy-cotton-tee", "camisetas", "Camiseta em algodão heavy weight. Estrutura premium, durabilidade excepcional e caimento sofisticado.", 219.90, None, 55, 1, "Novo", "M,L,XL,XXL", "Branco", "NV-TEE-005-WH", 1, 0, 0),
    ]
    products.extend(camisetas)
    
    # HOODIES / MOLETONS
    hoodies = [
        ("Essential Hoodie Black", "essential-hoodie-black", "hoodies", "Moletom preto essencial em fleece premium. Conforto térmico, capuz estruturado e acabamento premium.", 399.90, None, 70, 1, "Mais Vendido", "P,M,L,XL,XXL", "Preto", "NV-HOO-001-BK", 1, 1, 1),
        ("Essential Hoodie Grey", "essential-hoodie-grey", "hoodies", "Moletom cinza essencial em fleece premium. Versatilidade absoluta, conforto para todas as estações.", 399.90, 349.90, 65, 0, "Promo", "P,M,L,XL,XXL", "Cinza", "NV-HOO-002-GY", 0, 1, 1),
        ("Washed Hoodie", "washed-hoodie", "hoodies", "Moletom com efeito envelhecido premium. Visual único, textura sofisticada e autenticidade urbana.", 449.90, None, 45, 1, "Novo", "M,L,XL,XXL", "Bege", "NV-HOO-003-GR", 1, 0, 0),
        ("Premium Zip Hoodie", "premium-zip-hoodie", "hoodies", "Moletom com zíper premium em fleece de alta qualidade. Funcionalidade e estilo em perfeita harmonia.", 479.90, None, 50, 1, None, "M,L,XL,XXL", "Preto", "NV-HOO-004-BK", 1, 0, 1),
        ("Limited Drop Hoodie", "limited-drop-hoodie", "hoodies", "Moletom edição limitada. Design exclusivo, número seriado e exclusividade garantida.", 549.90, None, 25, 1, "Drop Limitado", "L,XL,XXL", "Preto", "NV-HOO-005-BK", 1, 0, 1),
    ]
    products.extend(hoodies)
    
    # CALÇAS
    calcas = [
        ("Cargo Pants Black", "cargo-pants-black", "calcas", "Calça cargo preta em tecido premium. Múltiplos bolsos funcionais, corte moderno e durabilidade superior.", 429.90, None, 60, 1, "Mais Vendido", "32,34,36,38,40", "Preto", "NV-PAN-001-BK", 1, 1, 1),
        ("Cargo Pants Grey", "cargo-pants-grey", "calcas", "Calça cargo cinza em tecido premium. Estilo utilitário refinado, conforto e funcionalidade.", 429.90, 389.90, 55, 0, "Promo", "32,34,36,38,40", "Cinza", "NV-PAN-002-GY", 0, 1, 1),
        ("Straight Fit Pants", "straight-fit-pants", "calcas", "Calça corte reto em algodão premium. Silhueta clássica, caimento perfeito e versatilidade urbana.", 379.90, None, 50, 1, "Novo", "30,32,34,36,38,40", "Preto", "NV-PAN-003-BK", 1, 0, 0),
        ("Wide Pants Street", "wide-pants-street", "calcas", "Calça wide leg premium. Corte contemporâneo, volume equilibrado e estética streetwear.", 449.90, None, 45, 1, None, "30,32,34,36,38,40", "Cinza", "NV-PAN-004-GY", 1, 0, 1),
        ("Utility Pants", "utility-pants", "calcas", "Calça utilitária premium em tecido técnico. Resistência, conforto e múltiplos bolsos funcionais.", 399.90, None, 40, 1, "Novo", "30,32,34,36,38,40", "Verde", "NV-PAN-005-GR", 1, 0, 0),
    ]
    products.extend(calcas)
    
    # TÊNIS
    tenis = [
        ("Low Street White", "low-street-white", "tenis", "Tênis low street branco. Design minimalista, conforto premium e versatilidade absoluta.", 549.90, None, 80, 1, "Mais Vendido", "38,39,40,41,42,43,44", "Branco", "NV-SNK-001-WH", 1, 1, 1),
        ("Low Street Black", "low-street-black", "tenis", "Tênis low street preto. Visual impactante, conforto superior e estética sofisticada.", 549.90, 499.90, 75, 0, "Promo", "38,39,40,41,42,43,44", "Preto", "NV-SNK-002-BK", 0, 1, 1),
        ("Urban Runner", "urban-runner", "tenis", "Tênis runner urbano. Amortecimento responsivo, design contemporâneo e performance diária.", 649.90, None, 55, 1, "Novo", "38,39,40,41,42,43,44", "Cinza", "NV-SNK-003-GY", 1, 0, 0),
        ("Premium Chunky", "premium-chunky", "tenis", "Tênis chunky premium. Silhueta ousada, conforto máximo e presença visual inegável.", 699.90, None, 45, 1, None, "38,39,40,41,42,43,44", "Preto", "NV-SNK-004-BK", 1, 0, 1),
        ("Luxury Inspired Sneaker", "luxury-inspired-sneaker", "tenis", "Tênis inspirado em luxury. Acabamento premium, materiais nobres e exclusividade.", 799.90, None, 20, 1, "Drop Limitado", "38,39,40,41,42,43,44", "Branco", "NV-SNK-005-WH", 1, 0, 1),
    ]
    products.extend(tenis)
    
    # BONÉS / HEADWEAR
    bones = [
        ("Clean Cap Black", "clean-cap-black", "acessorios", "Boné clean preto. Design minimalista, ajuste perfeito e estética premium.", 99.90, None, 100, 1, "Mais Vendido", "Único", "Preto", "NV-CAP-001-BK", 1, 1, 1),
        ("Clean Cap White", "clean-cap-white", "acessorios", "Boné clean branco. Visual clean, versatilidade absoluta e acabamento premium.", 99.90, 89.90, 90, 0, "Promo", "Único", "Branco", "NV-CAP-002-WH", 0, 1, 1),
        ("Trucker Street Cap", "trucker-street-cap", "acessorios", "Boné trucker street. Malha respirável, visual autêntico e estilo urbano.", 89.90, None, 80, 1, "Novo", "Único", "Preto", "NV-CAP-003-BK", 1, 0, 0),
        ("Beanie Premium", "beanie-premium", "acessorios", "Gorro premium em tricot. Conforto térmico, caimento perfeito e versatilidade.", 79.90, None, 120, 1, None, "Único", "Preto", "NV-BEA-001-BK", 1, 0, 1),
    ]
    products.extend(bones)
    
    # BOLSAS / ACESSÓRIOS
    bolsas = [
        ("Crossbody Bag Black", "crossbody-bag-black", "acessorios", "Bolsa transversal preta premium. Couro sintético de alta qualidade, design funcional e estética sofisticada.", 299.90, None, 60, 1, "Mais Vendido", "Único", "Preto", "NV-BAG-001-BK", 1, 1, 1),
        ("Shoulder Bag Utility", "shoulder-bag-utility", "acessorios", "Bolsa ombro utilitária premium. Múltiplos bolsos, design inteligente e funcionalidade urbana.", 349.90, 319.90, 55, 0, "Promo", "Único", "Cinza", "NV-BAG-002-GY", 0, 1, 1),
        ("Minimal Wallet", "minimal-wallet", "acessorios", "Carteira minimalista premium. Couro sintético, design compacto e acabamento sofisticado.", 149.90, None, 80, 1, "Novo", "Único", "Preto", "NV-WAL-001-BK", 1, 0, 0),
        ("Urban Backpack", "urban-backpack", "acessorios", "Mochila urbana premium. Compartimento notebook, múltiplos bolsos e design ergonômico.", 449.90, None, 40, 1, None, "Único", "Preto", "NV-BAC-001-BK", 1, 0, 1),
    ]
    products.extend(bolsas)
    
    # DROP LIMITADO
    drop_limitado = [
        ("Limited Tee 01", "limited-tee-01", "drop-limitado", "Camiseta edição limitada 01. Design exclusivo, número seriado e colecionável.", 249.90, None, 15, 1, "Drop Limitado", "M,L,XL", "Preto", "NV-LTD-TEE-001", 1, 0, 1),
        ("Limited Hoodie 01", "limited-hoodie-01", "drop-limitado", "Moletom edição limitada 01. Exclusividade absoluta, design único e edição restrita.", 599.90, None, 10, 1, "Drop Limitado", "L,XL,XXL", "Preto", "NV-LTD-HOO-001", 1, 0, 1),
        ("Limited Sneaker 01", "limited-sneaker-01", "drop-limitado", "Tênis edição limitada 01. Design exclusivo, número seriado e colecionável.", 899.90, None, 8, 1, "Drop Limitado", "40,41,42,43,44", "Branco", "NV-LTD-SNK-001", 1, 0, 1),
        ("Exclusive Capsule Item", "exclusive-capsule-item", "drop-limitado", "Peça exclusiva cápsula. Edição ultra limitada, design premium e raridade garantida.", 999.90, None, 5, 1, "Drop Limitado", "L,XL", "Preto", "NV-LTD-CAP-001", 1, 0, 1),
    ]
    products.extend(drop_limitado)
    
    return products


def init_db():
    db = get_db()
    db.executescript(
        """
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT NOT NULL UNIQUE,
            password_hash TEXT NOT NULL,
            is_admin INTEGER NOT NULL DEFAULT 0,
            full_name TEXT,
            reset_token TEXT,
            reset_expires_at TEXT,
            created_at TEXT
        );

        CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            slug TEXT NOT NULL UNIQUE,
            category TEXT NOT NULL,
            description TEXT NOT NULL,
            price REAL NOT NULL,
            promo_price REAL,
            stock INTEGER NOT NULL DEFAULT 0,
            featured INTEGER NOT NULL DEFAULT 0,
            badge TEXT,
            sizes TEXT,
            colors TEXT,
            sku TEXT,
            is_new INTEGER NOT NULL DEFAULT 0,
            is_bestseller INTEGER NOT NULL DEFAULT 0,
            free_shipping INTEGER NOT NULL DEFAULT 0
        );

        CREATE TABLE IF NOT EXISTS orders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            customer_name TEXT NOT NULL,
            customer_email TEXT NOT NULL,
            address TEXT NOT NULL,
            cep TEXT NOT NULL,
            payment_method TEXT NOT NULL,
            subtotal REAL NOT NULL,
            freight REAL NOT NULL,
            total REAL NOT NULL,
            status TEXT NOT NULL DEFAULT 'pending',
            created_at TEXT NOT NULL,
            FOREIGN KEY(user_id) REFERENCES users(id)
        );

        CREATE TABLE IF NOT EXISTS order_items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            order_id INTEGER NOT NULL,
            product_id INTEGER NOT NULL,
            product_name TEXT NOT NULL,
            quantity INTEGER NOT NULL,
            unit_price REAL NOT NULL,
            FOREIGN KEY(order_id) REFERENCES orders(id),
            FOREIGN KEY(product_id) REFERENCES products(id)
        );
        """
    )

    ensure_column(db, "users", "full_name", "TEXT")
    ensure_column(db, "users", "reset_token", "TEXT")
    ensure_column(db, "users", "reset_expires_at", "TEXT")
    ensure_column(db, "users", "created_at", "TEXT")
    ensure_column(db, "orders", "user_id", "INTEGER")
    ensure_column(db, "orders", "payment_provider", "TEXT DEFAULT 'manual'")
    ensure_column(db, "orders", "payment_reference", "TEXT")
    ensure_column(db, "orders", "payment_checkout_url", "TEXT")
    
    # Product columns for catalog expansion
    ensure_column(db, "products", "promo_price", "REAL")
    ensure_column(db, "products", "badge", "TEXT")
    ensure_column(db, "products", "sizes", "TEXT")
    ensure_column(db, "products", "colors", "TEXT")
    ensure_column(db, "products", "sku", "TEXT")
    ensure_column(db, "products", "is_new", "INTEGER DEFAULT 0")
    ensure_column(db, "products", "is_bestseller", "INTEGER DEFAULT 0")
    ensure_column(db, "products", "free_shipping", "INTEGER DEFAULT 0")
    
    db.commit()

    admin_email = os.getenv("ADMIN_EMAIL", "admin@velocity.local")
    admin_password = os.getenv("ADMIN_PASSWORD", "admin123")
    existing_admin = db.execute("SELECT id FROM users WHERE email = ?", (admin_email,)).fetchone()
    if not existing_admin:
        db.execute(
            "INSERT INTO users (email, password_hash, is_admin, created_at) VALUES (?, ?, 1, ?)",
            (admin_email, generate_password_hash(admin_password), datetime.utcnow().isoformat()),
        )
        db.commit()

    existing_slugs = {row["slug"] for row in db.execute("SELECT slug FROM products").fetchall()}
    new_products = [p for p in bulk_seed_products() if p[1] not in existing_slugs]
    if new_products:
        db.executemany(
            """
            INSERT INTO products (name, slug, category, description, price, promo_price, stock, featured, badge, sizes, colors, sku, is_new, is_bestseller, free_shipping)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            new_products,
        )
        db.commit()


def login_required(view):
    @wraps(view)
    def wrapped(*args, **kwargs):
        if "user_id" not in session:
            return redirect(url_for("admin_login"))
        return view(*args, **kwargs)

    return wrapped


def admin_required(view):
    @wraps(view)
    def wrapped(*args, **kwargs):
        if not session.get("is_admin"):
            return redirect(url_for("admin_login"))
        return view(*args, **kwargs)

    return wrapped


def customer_required(view):
    @wraps(view)
    def wrapped(*args, **kwargs):
        if "customer_user_id" not in session:
            flash("Faça login para acessar sua conta.", "warning")
            return redirect(url_for("customer_login", next=request.path))
        return view(*args, **kwargs)

    return wrapped


def get_current_customer():
    user_id = session.get("customer_user_id")
    if not user_id:
        return None
    return get_db().execute("SELECT * FROM users WHERE id = ?", (user_id,)).fetchone()


def list_products(category=None, search_query=None, filter_type=None):
    db = get_db()
    sql = "SELECT * FROM products WHERE 1=1"
    params = []

    if category and category != "todos":
        sql += " AND category = ?"
        params.append(category)

    if search_query:
        sql += " AND (name LIKE ? OR description LIKE ?)"
        like = f"%{search_query}%"
        params.extend([like, like])

    if filter_type == "bestsellers":
        sql += " AND is_bestseller = 1"
    elif filter_type == "new":
        sql += " AND is_new = 1"
    elif filter_type == "promo":
        sql += " AND promo_price IS NOT NULL"

    sql += " ORDER BY id DESC"
    return db.execute(sql, tuple(params)).fetchall()


def parse_positive_int(raw_value, default_value):
    try:
        parsed = int(raw_value)
        return parsed if parsed > 0 else default_value
    except (TypeError, ValueError):
        return default_value


def get_cart():
    return session.get("cart", {})


def save_cart(cart):
    session["cart"] = cart
    session.modified = True


def cart_details():
    cart = get_cart()
    db = get_db()
    items = []
    subtotal = 0.0
    for product_id, qty in cart.items():
        product = db.execute("SELECT * FROM products WHERE id = ?", (product_id,)).fetchone()
        if not product:
            continue
        line_total = product["price"] * qty
        subtotal += line_total
        items.append({"product": product, "quantity": qty, "line_total": line_total})

    freight = 0.0 if subtotal >= 399 or subtotal == 0 else 29.9
    total = subtotal + freight
    return {"items": items, "subtotal": subtotal, "freight": freight, "total": total}


def create_sillient_checkout(order_id, total_value):
    if not app.config["SILLIENT_PAY_ENABLED"]:
        return {
            "provider": "sillient_pay",
            "reference": f"SILLIENT-TEST-{order_id}",
            "checkout_url": url_for("payment_preview", order_id=order_id, _external=True),
            "status": "pending",
        }

    try:
        # Real SillientPay API call
        api_url = f"{app.config['SILLIENT_PAY_BASE_URL']}/v1/checkout"
        headers = {
            "Authorization": f"Bearer {app.config['SILLIENT_PAY_API_KEY']}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "order_id": str(order_id),
            "amount": float(total_value),
            "currency": "BRL",
            "callback_url": url_for("payment_callback", _external=True),
            "cancel_url": url_for("cart", _external=True),
            "success_url": url_for("checkout_success", order_id=order_id, _external=True),
            "metadata": {
                "order_id": order_id,
                "timestamp": datetime.utcnow().isoformat()
            }
        }
        
        response = requests.post(api_url, json=payload, headers=headers, timeout=30)
        response.raise_for_status()
        
        data = response.json()
        
        return {
            "provider": "sillient_pay",
            "reference": data.get("reference", f"SILLIENT-LIVE-{order_id}"),
            "checkout_url": data.get("checkout_url", url_for("payment_preview", order_id=order_id, _external=True)),
            "status": "pending",
            "checkout_id": data.get("id")
        }
        
    except requests.exceptions.RequestException as e:
        # Fallback to test mode if API fails
        return {
            "provider": "sillient_pay",
            "reference": f"SILLIENT-TEST-{order_id}",
            "checkout_url": url_for("payment_preview", order_id=order_id, _external=True),
            "status": "pending",
            "error": str(e)
        }


def verify_webhook_signature(payload, signature, secret):
    """Verify SillientPay webhook signature for security"""
    if not secret:
        return False
    
    expected_signature = hmac.new(
        secret.encode('utf-8'),
        payload.encode('utf-8'),
        hashlib.sha256
    ).hexdigest()
    
    return hmac.compare_digest(expected_signature, signature)


def ai_reply(message):
    text = (message or "").strip().lower()
    if not text:
        return "Posso te ajudar com tamanhos, estilos, preço e recomendações para looks urbanos e esportivos.", []

    category = None
    if any(k in text for k in ["corrida", "correr", "maratona"]):
        category = "corrida"
    elif any(k in text for k in ["treino", "academia", "musculacao", "musculação"]):
        category = "treino"
    elif any(k in text for k in ["lifestyle", "casual", "dia a dia"]):
        category = "lifestyle"

    db = get_db()
    if category:
        recs = db.execute("SELECT name, slug, price FROM products WHERE category = ? ORDER BY featured DESC, id DESC LIMIT 4", (category,)).fetchall()
        answer = f"Para {category}, eu recomendo estes produtos com melhor custo-benefício e alta procura."
    else:
        recs = db.execute("SELECT name, slug, price FROM products ORDER BY featured DESC, id DESC LIMIT 4").fetchall()
        answer = "Perfeito. Com base no seu estilo, selecionei peças populares para começar."

    products = [{"name": r["name"], "slug": r["slug"], "price": r["price"]} for r in recs]
    return answer, products


def hit_rate_limit(key, max_requests, window_seconds):
    now = time.time()
    bucket = session.get(key, [])
    bucket = [ts for ts in bucket if now - ts < window_seconds]
    allowed = len(bucket) < max_requests
    if allowed:
        bucket.append(now)
    session[key] = bucket
    session.modified = True
    return not allowed


@app.context_processor
def inject_globals():
    cart_count = sum(get_cart().values()) if session.get("cart") else 0
    customer = get_current_customer()
    return {
        "admin_login_path": f"/{app.config['ADMIN_PATH']}/login",
        "cart_count": cart_count,
        "current_customer": customer,
        "store_name": "N\u00d8VRA",
    }


@app.template_filter("brl")
def brl(value):
    return f"R$ {value:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")


@app.route("/")
def home():
    db = get_db()
    featured = db.execute("SELECT * FROM products WHERE featured = 1 ORDER BY id DESC LIMIT 8").fetchall()
    new_arrivals = db.execute("SELECT * FROM products WHERE is_new = 1 ORDER BY id DESC LIMIT 8").fetchall()
    bestsellers = db.execute("SELECT * FROM products WHERE is_bestseller = 1 ORDER BY id DESC LIMIT 8").fetchall()
    limited_drop = db.execute("SELECT * FROM products WHERE category = 'drop-limitado' ORDER BY id DESC LIMIT 4").fetchall()
    return render_template("home.html", featured=featured, new_arrivals=new_arrivals, bestsellers=bestsellers, limited_drop=limited_drop)


@app.route("/catalogo")
def catalog():
    category = request.args.get("categoria", "todos")
    query = request.args.get("q", "").strip()
    filter_type = request.args.get("filtro", None)
    page = parse_positive_int(request.args.get("page"), 1)
    products = list_products(category, query, filter_type)
    per_page = app.config["PRODUCTS_PER_PAGE"]
    total = len(products)
    pages = max(1, (total + per_page - 1) // per_page)
    if page > pages:
        page = pages
    start = (page - 1) * per_page
    end = start + per_page
    paginated = products[start:end]

    return render_template(
        "catalog.html",
        products=paginated,
        current_category=category,
        search_query=query,
        current_filter=filter_type,
        page=page,
        pages=pages,
        total=total,
    )


@app.route("/camisetas")
def category_camisetas():
    return redirect(url_for("catalog", categoria="camisetas"))


@app.route("/hoodies")
def category_hoodies():
    return redirect(url_for("catalog", categoria="hoodies"))


@app.route("/calcas")
def category_calcas():
    return redirect(url_for("catalog", categoria="calcas"))


@app.route("/tenis")
def category_tenis():
    return redirect(url_for("catalog", categoria="tenis"))


@app.route("/acessorios")
def category_acessorios():
    return redirect(url_for("catalog", categoria="acessorios"))


@app.route("/drop-limitado")
def category_drop_limitado():
    return redirect(url_for("catalog", categoria="drop-limitado"))


@app.route("/produto/<slug>")
def product_detail(slug):
    product = get_db().execute("SELECT * FROM products WHERE slug = ?", (slug,)).fetchone()
    if not product:
        return redirect(url_for("catalog"))
    return render_template("product.html", product=product)


@app.post("/carrinho/adicionar/<int:product_id>")
def add_to_cart(product_id):
    qty = max(1, int(request.form.get("quantity", 1)))
    cart = get_cart()
    key = str(product_id)
    cart[key] = cart.get(key, 0) + qty
    save_cart(cart)
    flash("Produto adicionado ao carrinho.", "success")
    return redirect(request.referrer or url_for("catalog"))


@app.post("/carrinho/remover/<int:product_id>")
def remove_from_cart(product_id):
    cart = get_cart()
    cart.pop(str(product_id), None)
    save_cart(cart)
    flash("Produto removido do carrinho.", "info")
    return redirect(url_for("cart"))


@app.get("/carrinho")
def cart():
    details = cart_details()
    return render_template("cart.html", **details)


@app.route("/checkout", methods=["GET", "POST"])
def checkout():
    details = cart_details()
    customer = get_current_customer()
    if not details["items"]:
        flash("Seu carrinho está vazio.", "warning")
        return redirect(url_for("catalog"))

    if request.method == "POST":
        form = request.form
        payment_method = form["pagamento"]
        payment_provider = "sillient_pay" if payment_method == "Sillient Pay" else "manual"

        db = get_db()
        created_at = datetime.utcnow().isoformat()
        cursor = db.execute(
            """
            INSERT INTO orders (
                customer_name, customer_email, address, cep, payment_method,
                subtotal, freight, total, status, created_at, payment_provider, user_id
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                form["nome"],
                form["email"],
                form["endereco"],
                form["cep"],
                payment_method,
                details["subtotal"],
                details["freight"],
                details["total"],
                "awaiting_payment" if payment_provider == "sillient_pay" else "pending",
                created_at,
                payment_provider,
                customer["id"] if customer else None,
            ),
        )
        order_id = cursor.lastrowid
        for item in details["items"]:
            db.execute(
                """
                INSERT INTO order_items (order_id, product_id, product_name, quantity, unit_price)
                VALUES (?, ?, ?, ?, ?)
                """,
                (
                    order_id,
                    item["product"]["id"],
                    item["product"]["name"],
                    item["quantity"],
                    item["product"]["price"],
                ),
            )

        if payment_provider == "sillient_pay":
            payment = create_sillient_checkout(order_id, details["total"])
            db.execute(
                "UPDATE orders SET payment_reference = ?, payment_checkout_url = ? WHERE id = ?",
                (payment["reference"], payment["checkout_url"], order_id),
            )
            db.commit()
            save_cart({})
            return redirect(url_for("start_payment", order_id=order_id))

        db.commit()
        save_cart({})
        return redirect(url_for("checkout_success", order_id=order_id))

    prefill = {
        "nome": customer["full_name"] if customer and customer["full_name"] else "",
        "email": customer["email"] if customer else "",
    }
    return render_template("checkout.html", **details, sillient_enabled=app.config["SILLIENT_PAY_ENABLED"], prefill=prefill)


@app.get("/pagamento/iniciar/<int:order_id>")
def start_payment(order_id):
    order = get_db().execute("SELECT * FROM orders WHERE id = ?", (order_id,)).fetchone()
    if not order:
        return redirect(url_for("home"))
    if order["payment_provider"] != "sillient_pay":
        return redirect(url_for("checkout_success", order_id=order_id))
    return redirect(order["payment_checkout_url"] or url_for("payment_preview", order_id=order_id))


@app.get("/pagamento/sillient/preview/<int:order_id>")
def payment_preview(order_id):
    order = get_db().execute("SELECT * FROM orders WHERE id = ?", (order_id,)).fetchone()
    if not order:
        return redirect(url_for("home"))
    return render_template("payment_preview.html", order=order)


@app.post("/pagamento/sillient/aprovar/<int:order_id>")
def payment_approve(order_id):
    db = get_db()
    db.execute("UPDATE orders SET status = 'paid' WHERE id = ?", (order_id,))
    db.commit()
    return redirect(url_for("checkout_success", order_id=order_id))


@app.post("/pagamento/sillient/callback")
def payment_callback():
    payload = request.get_json(silent=True) or {}
    signature = request.headers.get("X-Sillient-Signature", "")
    
    # Verify webhook signature if secret is configured
    if app.config["SILLIENT_PAY_WEBHOOK_SECRET"]:
        payload_str = request.get_data(as_text=True)
        if not verify_webhook_signature(payload_str, signature, app.config["SILLIENT_PAY_WEBHOOK_SECRET"]):
            return jsonify({"ok": False, "error": "invalid signature"}), 401
    
    reference = payload.get("reference")
    status = payload.get("status", "awaiting_payment")
    if not reference:
        return jsonify({"ok": False, "error": "missing reference"}), 400

    db = get_db()
    order = db.execute("SELECT id FROM orders WHERE payment_reference = ?", (reference,)).fetchone()
    if not order:
        return jsonify({"ok": False, "error": "order not found"}), 404

    mapped = "paid" if status in {"approved", "paid", "confirmed"} else "awaiting_payment"
    db.execute("UPDATE orders SET status = ? WHERE id = ?", (mapped, order["id"]))
    db.commit()
    return jsonify({"ok": True})


@app.get("/checkout/sucesso/<int:order_id>")
def checkout_success(order_id):
    order = get_db().execute("SELECT * FROM orders WHERE id = ?", (order_id,)).fetchone()
    if not order:
        return redirect(url_for("home"))
    return render_template("success.html", order=order)


@app.route("/admin")
def legacy_admin_redirect():
    abort(404)


@app.route(f"/{app.config['ADMIN_PATH']}/login", methods=["GET", "POST"])
def admin_login():
    attempts = session.get("admin_login_attempts", 0)
    blocked_until = session.get("admin_blocked_until")
    if blocked_until and datetime.utcnow() < datetime.fromisoformat(blocked_until):
        flash("Muitas tentativas. Tente novamente em alguns minutos.", "warning")
        return render_template("admin_login.html")

    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]
        user = get_db().execute("SELECT * FROM users WHERE email = ?", (email,)).fetchone()
        if user and check_password_hash(user["password_hash"], password):
            session["user_id"] = user["id"]
            session["is_admin"] = bool(user["is_admin"])
            session["admin_login_attempts"] = 0
            session.pop("admin_blocked_until", None)
            return redirect(url_for("admin_dashboard"))

        attempts += 1
        session["admin_login_attempts"] = attempts
        if attempts >= 5:
            session["admin_blocked_until"] = (datetime.utcnow() + timedelta(minutes=5)).isoformat()
        flash("Credenciais inválidas.", "danger")

    return render_template("admin_login.html")


@app.get(f"/{app.config['ADMIN_PATH']}/logout")
def admin_logout():
    session.clear()
    return redirect(url_for("admin_login"))


@app.get(f"/{app.config['ADMIN_PATH']}")
@login_required
@admin_required
def admin_dashboard():
    db = get_db()
    products = db.execute("SELECT * FROM products ORDER BY id DESC").fetchall()
    orders = db.execute("SELECT * FROM orders ORDER BY id DESC LIMIT 25").fetchall()
    return render_template("admin_dashboard.html", products=products, orders=orders)


@app.post(f"/{app.config['ADMIN_PATH']}/produtos")
@login_required
@admin_required
def admin_create_product():
    form = request.form
    slug = form["slug"].strip().lower()
    db = get_db()
    existing = db.execute("SELECT id FROM products WHERE slug = ?", (slug,)).fetchone()
    if existing:
        flash("Slug já existe. Use um slug único.", "warning")
        return redirect(url_for("admin_dashboard"))

    db.execute(
        """
        INSERT INTO products (name, slug, category, description, price, stock, featured)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
        (
            form["name"],
            slug,
            form["category"],
            form["description"],
            float(form["price"]),
            int(form["stock"]),
            1 if form.get("featured") == "on" else 0,
        ),
    )
    db.commit()
    flash("Produto criado com sucesso.", "success")
    return redirect(url_for("admin_dashboard"))


@app.post(f"/{app.config['ADMIN_PATH']}/pedidos/<int:order_id>/status")
@login_required
@admin_required
def admin_update_order_status(order_id):
    status = request.form.get("status", "pending")
    if status not in {"pending", "paid", "shipped", "cancelled", "awaiting_payment"}:
        status = "pending"
    db = get_db()
    db.execute("UPDATE orders SET status = ? WHERE id = ?", (status, order_id))
    db.commit()
    flash("Status do pedido atualizado.", "success")
    return redirect(url_for("admin_dashboard"))


@app.post("/api/ai-assistant")
def ai_assistant():
    if hit_rate_limit("ai_rate_limit", max_requests=12, window_seconds=60):
        return jsonify({"answer": "Muitas mensagens em pouco tempo. Aguarde alguns segundos e tente novamente.", "products": []}), 429

    payload = request.get_json(silent=True) or {}
    message = payload.get("message", "")
    answer, products = ai_reply(message)
    return jsonify({"answer": answer, "products": products})


@app.route("/conta/cadastro", methods=["GET", "POST"])
def customer_register():
    if request.method == "POST":
        full_name = request.form["full_name"].strip()
        email = request.form["email"].strip().lower()
        password = request.form["password"]
        confirm_password = request.form["confirm_password"]

        if password != confirm_password:
            flash("As senhas não conferem.", "warning")
            return render_template("customer_register.html")

        if len(password) < 8:
            flash("Use uma senha com ao menos 8 caracteres.", "warning")
            return render_template("customer_register.html")

        db = get_db()
        exists = db.execute("SELECT id FROM users WHERE email = ?", (email,)).fetchone()
        if exists:
            flash("Este e-mail já possui cadastro.", "warning")
            return render_template("customer_register.html")

        db.execute(
            "INSERT INTO users (full_name, email, password_hash, is_admin, created_at) VALUES (?, ?, ?, 0, ?)",
            (full_name, email, generate_password_hash(password), datetime.utcnow().isoformat()),
        )
        db.commit()
        flash("Cadastro criado com sucesso. Faça login para continuar.", "success")
        return redirect(url_for("customer_login"))

    return render_template("customer_register.html")


@app.route("/conta/login", methods=["GET", "POST"])
def customer_login():
    if request.method == "POST":
        email = request.form["email"].strip().lower()
        password = request.form["password"]
        user = get_db().execute("SELECT * FROM users WHERE email = ?", (email,)).fetchone()

        if not user or not check_password_hash(user["password_hash"], password):
            flash("Credenciais inválidas.", "danger")
            return render_template("customer_login.html")

        session.clear()
        session["customer_user_id"] = user["id"]
        session["customer_email"] = user["email"]
        session.permanent = True
        next_path = request.args.get("next")
        if next_path and next_path.startswith("/"):
            return redirect(next_path)
        return redirect(url_for("customer_account"))

    return render_template("customer_login.html")


@app.get("/conta/logout")
def customer_logout():
    session.pop("customer_user_id", None)
    session.pop("customer_email", None)
    return redirect(url_for("home"))


@app.route("/conta/esqueci-senha", methods=["GET", "POST"])
def customer_forgot_password():
    if request.method == "POST":
        email = request.form["email"].strip().lower()
        db = get_db()
        user = db.execute("SELECT id FROM users WHERE email = ?", (email,)).fetchone()
        if user:
            token = secrets.token_urlsafe(24)
            expires = (datetime.utcnow() + timedelta(minutes=30)).isoformat()
            db.execute("UPDATE users SET reset_token = ?, reset_expires_at = ? WHERE id = ?", (token, expires, user["id"]))
            db.commit()
            reset_link = url_for("customer_reset_password", token=token, _external=True)
            flash(f"Link de redefinição (sandbox): {reset_link}", "info")
        else:
            flash("Se o e-mail existir, o link de redefinição foi gerado.", "info")
        return redirect(url_for("customer_login"))
    return render_template("customer_forgot_password.html")


@app.route("/conta/redefinir-senha/<token>", methods=["GET", "POST"])
def customer_reset_password(token):
    db = get_db()
    user = db.execute("SELECT * FROM users WHERE reset_token = ?", (token,)).fetchone()
    if not user or not user["reset_expires_at"] or datetime.utcnow() > datetime.fromisoformat(user["reset_expires_at"]):
        flash("Token inválido ou expirado.", "danger")
        return redirect(url_for("customer_forgot_password"))

    if request.method == "POST":
        password = request.form["password"]
        confirm_password = request.form["confirm_password"]
        if password != confirm_password or len(password) < 8:
            flash("Senha inválida ou diferente da confirmação.", "warning")
            return render_template("customer_reset_password.html", token=token)

        db.execute(
            "UPDATE users SET password_hash = ?, reset_token = NULL, reset_expires_at = NULL WHERE id = ?",
            (generate_password_hash(password), user["id"]),
        )
        db.commit()
        flash("Senha atualizada. Faça login.", "success")
        return redirect(url_for("customer_login"))

    return render_template("customer_reset_password.html", token=token)


@app.get("/conta")
@customer_required
def customer_account():
    customer = get_current_customer()
    orders = get_db().execute(
        "SELECT * FROM orders WHERE user_id = ? ORDER BY id DESC LIMIT 30",
        (customer["id"],),
    ).fetchall()
    return render_template("customer_account.html", customer=customer, orders=orders)


@app.get("/api/products")
def api_products():
    category = request.args.get("categoria", "todos")
    query = request.args.get("q", "").strip()
    page = parse_positive_int(request.args.get("page"), 1)
    per_page = min(50, parse_positive_int(request.args.get("per_page"), 12))
    products = list_products(category, query)
    total = len(products)
    pages = max(1, (total + per_page - 1) // per_page)
    if page > pages:
        page = pages
    start = (page - 1) * per_page
    end = start + per_page
    items = [
        {
            "id": p["id"],
            "name": p["name"],
            "slug": p["slug"],
            "category": p["category"],
            "description": p["description"],
            "price": p["price"],
            "stock": p["stock"],
            "featured": bool(p["featured"]),
        }
        for p in products[start:end]
    ]
    return jsonify({
        "items": items,
        "pagination": {"page": page, "per_page": per_page, "pages": pages, "total": total},
    })


@app.get("/api/health")
def health():
    return jsonify({
        "status": "ok",
        "service": "novra-store",
        "admin_path": app.config["ADMIN_PATH"],
        "sillient_pay_enabled": app.config["SILLIENT_PAY_ENABLED"],
    })


@app.get("/manifest.webmanifest")
def manifest():
    static_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "static")
    return send_from_directory(static_dir, "manifest.webmanifest")


@app.get("/sw.js")
def service_worker():
    static_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "static")
    response = send_from_directory(static_dir, "sw.js")
    response.headers["Cache-Control"] = "no-cache"
    return response


@app.after_request
def set_security_headers(response):
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "SAMEORIGIN"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    response.headers["Permissions-Policy"] = "geolocation=(), microphone=(), camera=()"
    response.headers["Content-Security-Policy"] = (
        "default-src 'self'; "
        "img-src 'self' data: https:; "
        "style-src 'self' 'unsafe-inline' https://fonts.googleapis.com; "
        "font-src 'self' https://fonts.gstatic.com; "
        "script-src 'self' 'unsafe-inline'; "
        "connect-src 'self'; "
        "frame-ancestors 'self';"
    )
    return response


@app.before_request
def set_session_policy():
    session.permanent = True


@app.route("/health")
def health_check():
    """Health check endpoint for Railway monitoring."""
    return jsonify({"status": "ok", "service": "novra"}), 200


def initialize_database():
    """Initialize database with error handling for production environments."""
    try:
        with app.app_context():
            init_db()
            print("✓ Database initialized successfully")
    except Exception as e:
        print(f"✗ Database initialization error: {e}")
        import traceback
        traceback.print_exc()

# Initialize database on startup
initialize_database()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
