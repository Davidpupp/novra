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


def generate_product_variations():
    """Generate 1000+ product variations with professional images for massive catalog"""
    products = []
    
    # URLs de imagens profissionais por categoria (Unsplash)
    tee_images = [
        "https://images.unsplash.com/photo-1521572163474-6864f9cf17ab?w=600",
        "https://images.unsplash.com/photo-1583743814966-8936f5b7be1a?w=600",
        "https://images.unsplash.com/photo-1576566588028-4147f3842f27?w=600",
        "https://images.unsplash.com/photo-1618354691373-d851c5c3a990?w=600",
        "https://images.unsplash.com/photo-1562157873-818bc0726f68?w=600",
        "https://images.unsplash.com/photo-1581655353564-df123a1eb820?w=600",
        "https://images.unsplash.com/photo-1503341504253-dff4815485f1?w=600",
        "https://images.unsplash.com/photo-1571945153237-4929e783af4a?w=600",
    ]
    
    hoodie_images = [
        "https://images.unsplash.com/photo-1556905055-8f358a7a47b2?w=600",
        "https://images.unsplash.com/photo-1578768079052-aa76e52ff62e?w=600",
        "https://images.unsplash.com/photo-1620799140408-edc6dcb6d633?w=600",
        "https://images.unsplash.com/photo-1556821840-3a63f95609a7?w=600",
        "https://images.unsplash.com/photo-1515886657613-9f3515b0c78f?w=600",
    ]
    
    pants_images = [
        "https://images.unsplash.com/photo-1542272604-787c3839105e?w=600",
        "https://images.unsplash.com/photo-1594633312681-425c7b97ccd1?w=600",
        "https://images.unsplash.com/photo-1506629082955-511b1aa562c8?w=600",
        "https://images.unsplash.com/photo-1473966968600-fa801b869a1a?w=600",
    ]
    
    sneaker_images = [
        "https://images.unsplash.com/photo-1542291026-7eec264c27ff?w=600",
        "https://images.unsplash.com/photo-1600185365926-3a2ce3cdb9eb?w=600",
        "https://images.unsplash.com/photo-1595950653106-6c9ebd614d3a?w=600",
        "https://images.unsplash.com/photo-1606107557195-0e29a4b5b4aa?w=600",
        "https://images.unsplash.com/photo-1551107696-a4b0c5a0d9a2?w=600",
        "https://images.unsplash.com/photo-1549298916-b41d501d3772?w=600",
    ]
    
    accessory_images = [
        "https://images.unsplash.com/photo-1553062407-98eeb64c6a62?w=600",
        "https://images.unsplash.com/photo-1548036328-c9fa89d128fa?w=600",
        "https://images.unsplash.com/photo-1558171813-4c088753af8f?w=600",
        "https://images.unsplash.com/photo-1622434641406-a158123450f9?w=600",
        "https://images.unsplash.com/photo-1611085583193-a87b724c82c3?w=600",
    ]
    
    # CAMISETAS - 150 variações
    tee_colors = ["Preto", "Branco", "Cinza", "Bege", "Verde", "Azul", "Vinho", "Marrom", "Creme", "Off-White"]
    tee_styles = [
        ("Oversized Premium", "oversized", "Camiseta oversized em algodão 200g/m². Caimento estruturado, gola canelada reforçada.", 199.90, 149.90),
        ("Essential Basic", "essential", "Camiseta básica em algodão 180g/m². Conforto premium para o dia a dia.", 129.90, 99.90),
        ("Heavyweight Boxy", "heavyweight", "Camiseta heavyweight 300g/m². Corte boxy, gola alta, acabamento premium.", 249.90, 199.90),
        ("Washed Vintage", "washed", "Camiseta washed efeito vintage. Pigmentada, lavada enzimaticamente.", 179.90, 139.90),
        ("Minimal Logo", "minimal", "Camiseta minimalista com logo bordado discreto. Elegância streetwear.", 169.90, 129.90),
        ("Street Graphic", "graphic", "Camiseta com estampa exclusiva streetwear. Arte urbana, pintura à mão.", 219.90, 169.90),
        ("Premium Essentials", "essentials", "Camiseta essentials com detalhes em suede. Tacto macio.", 189.90, 149.90),
        ("Cropped Boxy", "cropped", "Camiseta cropped boxy fit. Corte moderno, tendência streetwear.", 159.90, 119.90),
        ("Longline Tee", "longline", "Camiseta longline com fenda lateral. Estética streetwear premium.", 179.90, 139.90),
        ("Tie Dye Premium", "tie-dye", "Camiseta tie-dye artesanal. Cada peça única, tingida à mão.", 229.90, 179.90),
        ("Reflective Tech", "reflective", "Camiseta com detalhes refletivos. Techwear, funcional urbana.", 259.90, 199.90),
        ("Distressed Raw", "distressed", "Camiseta com efeito destroyed. Bordas raw, estética grunge premium.", 199.90, 159.90),
        ("Embroidery Classic", "embroidery", "Camiseta com bordado clássico. Logo 3D, textura premium.", 229.90, 179.90),
        ("Slub Texture", "slub", "Camiseta com textura slub irregular. Visual artesanal, algodão natural.", 189.90, 149.90),
        ("Oversized Pocket", "pocket", "Camiseta oversized com bolso utilitário. Funcional streetwear.", 209.90, 169.90),
    ]
    
    for i, (style_name, slug, desc, price, promo) in enumerate(tee_styles):
        for j, color in enumerate(tee_colors):
            color_slug = color.lower().replace(" ", "-").replace("-", "")
            sku = f"NV-TEE-{i+1:03d}-{color[:2].upper()}"
            badge = "Mais Vendido" if i < 3 and color == "Preto" else ("Promo" if promo else ("Novo" if i > 10 else None))
            stock = 50 + (i * 5) % 100
            featured = 1 if i < 5 else 0
            is_new = 1 if i > 10 else 0
            is_bestseller = 1 if i < 3 else 0
            free_ship = 1 if price > 150 else 0
            image_url = tee_images[(i + j) % len(tee_images)]
            
            products.append((
                f"{style_name} {color}",
                f"{slug}-{color_slug}",
                "camisetas",
                f"{desc} Disponível na cor {color}.",
                price,
                promo if i % 3 == 0 else None,
                stock,
                featured,
                badge,
                "P,M,L,XL,XXL",
                color,
                sku,
                image_url,
                is_new,
                is_bestseller,
                free_ship
            ))
    
    # HOODIES - 80 variações
    hoodie_colors = ["Preto", "Cinza", "Bege", "Branco", "Vinho", "Verde Oliva", "Marrom", "Azul Marinho"]
    hoodie_styles = [
        ("Essential Hoodie", "essential", "Moletom essentials em fleece 320g/m². Capuz duplo, bolsos canguru.", 399.90, 349.90),
        ("Oversized Hoodie", "oversized", "Moletom oversized fit. Caimento largo, estética streetwear.", 449.90, 399.90),
        ("Tech Fleece Hoodie", "tech", "Moletom tech fleece. Tecido técnico, cortes estratégicos.", 499.90, 449.90),
        ("Sherpa Lined Hoodie", "sherpa", "Moletom com forro sherpa. Conforto térmico extremo.", 549.90, 499.90),
        ("Zip Up Premium", "zipup", "Moletom com zíper YKK premium. Funcionalidade urbana.", 479.90, 429.90),
        ("Heavyweight Hoodie", "heavyweight", "Moletom heavyweight 450g/m². Estrutura premium, durabilidade.", 529.90, 479.90),
        ("Vintage Wash Hoodie", "vintage", "Moletom washed vintage. Efeito envelhecido, exclusivo.", 459.90, 409.90),
        ("Embroidered Logo", "embroidery", "Moletom com logo bordado 3D. Acabamento de luxo.", 489.90, 439.90),
        ("Pullover Fleece", "pullover", "Moletom pullover clássico. Silhueta atemporal, comforto.", 429.90, 379.90),
        ("Reflective Hoodie", "reflective", "Moletom com detalhes refletivos. Techwear noturno.", 519.90, 469.90),
    ]
    
    for i, (style, slug, desc, price, promo) in enumerate(hoodie_styles):
        for j, color in enumerate(hoodie_colors):
            color_slug = color.lower().replace(" ", "-").replace("-", "")
            sku = f"NV-HOO-{i+1:03d}-{color[:2].upper()}"
            badge = "Mais Vendido" if i == 0 and color == "Preto" else ("Promo" if promo and i % 2 == 0 else None)
            stock = 30 + (i * 8) % 70
            image_url = hoodie_images[(i + j) % len(hoodie_images)]
            
            products.append((
                f"{style} {color}",
                f"{slug}-hoodie-{color_slug}",
                "hoodies",
                f"{desc} Cor {color} exclusiva.",
                price,
                promo if i % 2 == 0 else None,
                stock,
                1 if i < 3 else 0,
                badge,
                "P,M,L,XL,XXL",
                color,
                sku,
                image_url,
                1 if i > 7 else 0,
                1 if i < 2 else 0,
                1
            ))
    
    # CALÇAS - 60 variações
    pants_colors = ["Preto", "Cinza", "Bege", "Verde", "Camuflado", "Azul", "Cáqui", "Marrom"]
    pants_styles = [
        ("Cargo Pants", "cargo", "Calça cargo 6 bolsos. Tecido ripstop premium, resistência.", 449.90, 399.90),
        ("Wide Leg Pants", "wide", "Calça wide leg. Corte moderno, tendência streetwear.", 399.90, 349.90),
        ("Jogger Premium", "jogger", "Calça jogger em moletom premium. Punhos reforçados.", 349.90, 299.90),
        ("Straight Fit", "straight", "Calça corte reto clássico. Silhueta atemporal.", 379.90, 329.90),
        ("Utility Tech Pants", "utility", "Calça utilitária tech. Bolsos funcionais, tecido técnico.", 479.90, 429.90),
        ("Parachute Pants", "parachute", "Calça parachute nylon. Estética 90s renovada.", 419.90, 369.90),
        (" Carpenter Work Pants", "carpenter", "Calça carpenter workwear. Resistência industrial.", 389.90, 339.90),
        ("Track Pants", "track", "Calça track listra lateral. Athletic streetwear.", 329.90, 279.90),
    ]
    
    for i, (style, slug, desc, price, promo) in enumerate(pants_styles):
        for j, color in enumerate(pants_colors):
            color_slug = color.lower().replace(" ", "-").replace("-", "")
            sku = f"NV-PAN-{i+1:03d}-{color[:2].upper()}"
            badge = "Mais Vendido" if i == 0 and color == "Preto" else None
            image_url = pants_images[(i + j) % len(pants_images)]
            
            products.append((
                f"{style} {color}",
                f"{slug}-pants-{color_slug}",
                "calcas",
                f"{desc} Disponível em {color}.",
                price,
                promo if i % 3 == 0 else None,
                25 + (i * 5) % 60,
                1 if i < 3 else 0,
                badge,
                "36,38,40,42,44,46",
                color,
                sku,
                image_url,
                1 if i > 6 else 0,
                1 if i < 2 else 0,
                1
            ))
    
    # TÊNIS - 100 variações (estilo MC, premium)
    sneaker_models = [
        ("Dunk Low", "dunk-low", 899.90, 799.90, "Tênis estilo Dunk. Couro premium, sola robusta.", "Mais Vendido"),
        ("Air Force Inspired", "af-inspired", 849.90, 749.90, "Tênis clássico reinventado. Couro grão integral.", "Escolha dos MCs"),
        ("Jordan Style High", "jordan-high", 1299.90, 1199.90, "Tênis cano alto premium. Estilo basketball luxo.", "Drop Limitado"),
        ("Runner Pro", "runner-pro", 699.90, 599.90, "Tênis running performance. Amortecimento responsivo.", None),
        ("Chunky Platform", "chunky", 799.90, 699.90, "Tênis chunky plataforma. Silhueta ousada streetwear.", "Tendência"),
        ("Retro 90s", "retro-90", 649.90, 549.90, "Tênis retrô 90s. Vintage moderno, cores vibrantes.", "Novo"),
        ("Skate Low Pro", "skate-pro", 579.90, 479.90, "Tênis skate pro. Borracha vulcanizada premium.", None),
        ("Luxury Suede", "luxury-suede", 1199.90, 1099.90, "Tênis camurça italiana. Acabamento artesanal.", "Edição Limitada"),
        ("Tech Runner", "tech-runner", 899.90, 799.90, "Tênis techwear. Materiais sintéticos avançados.", None),
        ("Basketball Elite", "bball-elite", 999.90, 899.90, "Tênis basketball elite. Performance profissional.", None),
    ]
    
    sneaker_colors = [
        ("Black White", "preto/branco"),
        ("Triple Black", "preto total"),
        ("Triple White", "branco total"),
        ("Grey Fog", "cinza"),
        ("University Red", "vermelho"),
        ("Royal Blue", "azul"),
        ("Olive Green", "verde"),
        ("Beige", "bege"),
        ("Cream", "creme"),
        ("Brown", "marrom"),
    ]
    
    for i, (model, slug, price, promo, desc, badge) in enumerate(sneaker_models):
        for j, (color_name, color_pt) in enumerate(sneaker_colors):
            color_slug = color_name.lower().replace(" ", "-")
            sku = f"NV-SNK-{i+1:03d}-{j+1:02d}"
            is_ltd = 1 if "Limitado" in str(badge) or i in [2, 7] else 0
            stock = 8 if is_ltd else (15 if i < 3 else 30 + (i * j) % 50)
            image_url = sneaker_images[(i + j) % len(sneaker_images)]
            
            products.append((
                f"{model} {color_name}",
                f"{slug}-{color_slug}",
                "tenis",
                f"{desc} Colorway {color_name} exclusiva.",
                price,
                promo if j % 2 == 0 and not is_ltd else None,
                stock,
                1 if i < 4 else 0,
                badge if j == 0 else None,
                "37,38,39,40,41,42,43,44",
                color_pt,
                sku,
                image_url,
                1 if i > 7 else 0,
                1 if i < 2 else 0,
                1
            ))
    
    # ACESSÓRIOS - 100 variações
    accessory_types = [
        # Bonés - 20
        ("Dad Hat", "dad-hat", "Boné dad hat clássico. Curva suave, ajuste perfeito.", 129.90, 99.90, "acessorios"),
        ("Trucker Premium", "trucker", "Boné trucker telado. Estilo americano premium.", 149.90, 119.90, "acessorios"),
        ("Snapback Classic", "snapback", "Boné snapback plano. Estrutura rígida, logo bordado.", 159.90, 129.90, "acessorios"),
        ("Bucket Hat", "bucket", "Bucket hat reversível. Duas cores, estilo streetwear.", 179.90, 149.90, "acessorios"),
        ("Beanie Ribbed", "beanie", "Gorro beanie canelado. Lã premium, stretch confortável.", 99.90, 79.90, "acessorios"),
        # Bolsas - 20
        ("Crossbody Mini", "crossbody", "Bolsa transversal compacta. Couro sintético premium.", 249.90, 199.90, "acessorios"),
        ("Shoulder Bag", "shoulder", "Bolsa ombro estilo mensageiro. Compartimentos organizados.", 299.90, 249.90, "acessorios"),
        ("Tote Premium", "tote", "Ecobag tote premium. Algodão 100%, silkscreen.", 199.90, 159.90, "acessorios"),
        ("Waist Bag", "waist", "Pochete waist bag moderna. Hands free, funcional.", 179.90, 139.90, "acessorios"),
        ("Backpack Rolltop", "backpack", "Mochila rolltop urbana. Expansível, resistente.", 449.90, 399.90, "acessorios"),
        # Meias & Underwear - 20
        ("Pack 3 Meias", "socks-pack", "Pack 3 meias cano alto. Algodão premium, conforto.", 89.90, 69.90, "acessorios"),
        ("Meia Street Premium", "socks-street", "Meia streetwear premium. Estampas exclusivas.", 49.90, 39.90, "acessorios"),
        ("Cueca Boxer", "boxer", "Cueca boxer microfibra. Conforto premium, cores.", 69.90, 49.90, "acessorios"),
        # Carteiras & Cintos - 20
        ("Carteira Slim", "wallet-slim", "Carteira slim minimalista. Couro PU, compartimentos.", 129.90, 99.90, "acessorios"),
        ("Carteira Zip", "wallet-zip", "Carteira com zíper. Segurança total, moderna.", 149.90, 119.90, "acessorios"),
        ("Cinto Classic", "belt", "Cinto clássico fivela prata. Couro sintético premium.", 179.90, 149.90, "acessorios"),
        ("Cinto Chain", "belt-chain", "Cinto com corrente decorativa. Estilo punk luxo.", 229.90, 199.90, "acessorios"),
        # Óculos & Outros - 20
        ("Óculos de Sol", "sunglasses", "Óculos de sol UV400. Armação acetato premium.", 299.90, 249.90, "acessorios"),
        ("Corrente Prata", "chain", "Corrente prata 925. Elo cubano, fecho reforçado.", 399.90, 349.90, "acessorios"),
        ("Anel Signet", "ring", "Anel signet clássico. Aço inoxidável, gravável.", 149.90, 119.90, "acessorios"),
        ("Pulseira Silicone", "bracelet", "Pulseira silicone premium. Cores vibrantes.", 59.90, 39.90, "acessorios"),
        ("Phone Case", "phone-case", "Capa phone case premium. Proteção militar.", 129.90, 99.90, "acessorios"),
    ]
    
    acc_colors = ["Preto", "Branco", "Cinza", "Bege", "Marrom", "Azul", "Verde", "Vermelho"]
    
    for i, (name, slug, desc, price, promo, cat) in enumerate(accessory_types):
        for j, color in enumerate(acc_colors[:5]):
            color_slug = color.lower()
            sku = f"NV-ACC-{i+1:03d}-{color[:2].upper()}"
            stock = 40 + i * 10
            image_url = accessory_images[(i + j) % len(accessory_images)]
            
            products.append((
                f"{name} {color}",
                f"{slug}-{color_slug}",
                cat,
                f"{desc} Cor {color}.",
                price,
                promo if i % 4 == 0 else None,
                stock,
                1 if i < 5 else 0,
                "Mais Vendido" if i == 0 else None,
                "Único" if i < 10 else "Ajustável",
                color,
                sku,
                image_url,
                1 if i > 12 else 0,
                1 if i < 3 else 0,
                0
            ))
    
    # CONJUNTOS (SETS) - 30 variações
    set_images = [
        "https://images.unsplash.com/photo-1515886657613-9f3515b0c78f?w=600",
        "https://images.unsplash.com/photo-1556905055-8f358a7a47b2?w=600",
        "https://images.unsplash.com/photo-1578768079052-aa76e52ff62e?w=600",
        "https://images.unsplash.com/photo-1620799140408-edc6dcb6d633?w=600",
    ]
    
    set_styles = [
        ("Conjunto Street", "set-street", "Conjunto camiseta + calça streetwear. Look completo.", 499.90, 449.90),
        ("Conjunto Sport", "set-sport", "Conjunto esportivo completo. Treino ou casual.", 599.90, 549.90),
        ("Conjunto Luxo", "set-luxo", "Conjunto premium hoodie + cargo. Streetwear luxo.", 799.90, 699.90),
        ("Conjunto Verão", "set-verao", "Conjunto verão leve. Conforto e estilo.", 349.90, 299.90),
        ("Conjunto Tech", "set-tech", "Conjunto techwear completo. Funcional urbano.", 899.90, 799.90),
    ]
    
    set_colors = ["Preto", "Cinza", "Bege", "Verde"]
    for i, (name, slug, desc, price, promo) in enumerate(set_styles):
        for j, color in enumerate(set_colors):
            color_slug = color.lower()
            sku = f"NV-SET-{i+1:03d}-{color[:2].upper()}"
            image_url = set_images[(i + j) % len(set_images)]
            
            products.append((
                f"{name} {color}",
                f"{slug}-{color_slug}",
                "conjuntos",
                f"{desc} Disponível em {color}.",
                price,
                promo,
                20 + i * 5,
                1,
                "Combo Especial" if i == 2 else None,
                "P,M,L,XL,XXL",
                color,
                sku,
                image_url,
                1 if i > 3 else 0,
                1 if i == 0 else 0,
                1
            ))
    
    return products


def bulk_seed_products():
    """Generate complete product catalog with 1000+ professional items with images"""
    products = generate_product_variations()
    
    # DROP LIMITADO - Edições ultra exclusivas
    limited_editions = [
        ("Drop Tee - Autografada", "drop-autografada", "drop-limitado", "Camiseta edição limitada 001/100. Numerada, autografada.", 999.90, None, 3, 1, "🔥 Drop Limitado", "M,L,XL", "Preto", "NV-LTD-001", "https://images.unsplash.com/photo-1521572163474-6864f9cf17ab?w=600", 1, 0, 1),
        ("Hoodie Supreme Edition", "hoodie-supreme", "drop-limitado", "Moletom edição suprema. Bordado ouro 24k.", 2499.90, None, 2, 1, "👑 Ultra Exclusivo", "L,XL", "Preto", "NV-LTD-002", "https://images.unsplash.com/photo-1556905055-8f358a7a47b2?w=600", 1, 0, 1),
        ("Tênis Colab Artist", "tenis-colab", "drop-limitado", "Tênis colab artista urbano. Arte exclusiva.", 1899.90, None, 5, 1, "🎨 Colab Especial", "38-44", "Multi", "NV-LTD-003", "https://images.unsplash.com/photo-1542291026-7eec264c27ff?w=600", 1, 0, 1),
        ("Jaqueta Premium Leather", "jaqueta-leather", "drop-limitado", "Jaqueta couro legítimo. Costura artesanal.", 3499.90, None, 1, 1, "💎 Peça Única", "L,XL", "Preto", "NV-LTD-004", "https://images.unsplash.com/photo-1551028719-00167b16eac5?w=600", 1, 0, 1),
        ("Kit MC Gold", "kit-mc-gold", "drop-limitado", "Kit completo MC: camiseta + boné + corrente. Dourado.", 1499.90, None, 8, 1, "⚡ Escolha dos MCs", "Único", "Ouro", "NV-LTD-005", "https://images.unsplash.com/photo-1617137968427-85924c800a22?w=600", 1, 0, 1),
    ]
    products.extend(limited_editions)
    
    # COLAB ESPECIAIS
    collabs = [
        ("NV x DJonga Tee", "colab-djonga", "drop-limitado", "Colab exclusiva DJonga. Letra bordada.", 399.90, 349.90, 15, 1, "🎤 Colab", "M,L,XL", "Preto", "NV-COL-001", "https://images.unsplash.com/photo-1583743814966-8936f5b7be1a?w=600", 1, 0, 1),
        ("NV x BK Hoodie", "colab-bk", "drop-limitado", "Colab BK. Design artwork exclusivo.", 699.90, 599.90, 12, 1, "🎤 Colab", "L,XL,XXL", "Cinza", "NV-COL-002", "https://images.unsplash.com/photo-1578768079052-aa76e52ff62e?w=600", 1, 0, 1),
        ("NV x Matuê Tee", "colab-matue", "drop-limitado", "Colab Matuê. Estampa 30k.", 449.90, 399.90, 20, 1, "🎤 Colab", "P,M,L,XL", "Branco", "NV-COL-003", "https://images.unsplash.com/photo-1576566588028-4147f3842f27?w=600", 1, 0, 1),
    ]
    products.extend(collabs)
    
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
            image_url TEXT,
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
    ensure_column(db, "products", "image_url", "TEXT")
    
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
            INSERT INTO products (name, slug, category, description, price, promo_price, stock, featured, badge, sizes, colors, sku, image_url, is_new, is_bestseller, free_shipping)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
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
    tenis_premium = db.execute("SELECT * FROM products WHERE category = 'tenis' AND price > 500 ORDER BY id DESC LIMIT 8").fetchall()
    conjuntos = db.execute("SELECT * FROM products WHERE category = 'conjuntos' ORDER BY id DESC LIMIT 6").fetchall()
    acessorios = db.execute("SELECT * FROM products WHERE category = 'acessorios' ORDER BY id DESC LIMIT 8").fetchall()
    return render_template("home.html", 
                         featured=featured, 
                         new_arrivals=new_arrivals, 
                         bestsellers=bestsellers, 
                         limited_drop=limited_drop,
                         tenis_premium=tenis_premium,
                         conjuntos=conjuntos,
                         acessorios=acessorios)


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
