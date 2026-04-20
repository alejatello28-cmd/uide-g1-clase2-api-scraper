"""
╔══════════════════════════════════════════════════════════════╗
║     CRYPTO SCRAPER — CoinMarketCap Top 100 Cryptocurrencies  ║
║     Extrae: precio, market cap, volumen, cambios, supply     ║
╚══════════════════════════════════════════════════════════════╝

Fuente: https://coinmarketcap.com
Librerías: requests, BeautifulSoup4, pandas
"""

import requests
import pandas as pd
import json
import time
import sys
from bs4 import BeautifulSoup
from datetime import datetime
from pathlib import Path

# ──────────────────────────────────────────────
# CONFIGURACIÓN
# ──────────────────────────────────────────────

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    ),
    "Accept-Language": "en-US,en;q=0.9",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
}

OUTPUT_DIR = Path(__file__).parent / "data"
OUTPUT_DIR.mkdir(exist_ok=True)


# ──────────────────────────────────────────────
# SCRAPER PRINCIPAL (CoinGecko tabla pública)
# ──────────────────────────────────────────────

def scrape_coingecko() -> list[dict]:
    """
    Scraping de CoinGecko /en/coins para obtener top 100 criptomonedas.
    Estrategia: scraping HTML + parsing de columnas de la tabla.
    """
    print("🔍 Iniciando scraping de CoinGecko...")
    url = "https://www.coingecko.com/en/coins"
    records = []

    try:
        response = requests.get(url, headers=HEADERS, timeout=20)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")

        # Buscar todas las filas de la tabla
        rows = soup.select("table tbody tr")
        print(f"   → Filas encontradas en tabla: {len(rows)}")

        for row in rows[:100]:
            cols = row.find_all("td")
            if len(cols) < 5:
                continue
            try:
                # Extrae texto limpio de cada columna
                rank_text = cols[0].get_text(strip=True)
                name_cell = cols[1]
                name = name_cell.select_one("a span") or name_cell
                symbol_span = name_cell.select_one(".tw-hidden") or name_cell
                price_text = cols[2].get_text(strip=True)
                change_1h = cols[3].get_text(strip=True)
                change_24h = cols[4].get_text(strip=True)
                change_7d = cols[5].get_text(strip=True) if len(cols) > 5 else ""
                volume_text = cols[6].get_text(strip=True) if len(cols) > 6 else ""
                mcap_text = cols[7].get_text(strip=True) if len(cols) > 7 else ""

                records.append({
                    "rank": clean_number(rank_text),
                    "name": name.get_text(strip=True) if hasattr(name, 'get_text') else str(name),
                    "price_usd": clean_price(price_text),
                    "change_1h_pct": clean_pct(change_1h),
                    "change_24h_pct": clean_pct(change_24h),
                    "change_7d_pct": clean_pct(change_7d),
                    "volume_24h_usd": clean_price(volume_text),
                    "market_cap_usd": clean_price(mcap_text),
                })
            except Exception:
                continue

    except Exception as e:
        print(f"   ⚠️  Error con CoinGecko HTML: {e}")

    return records


def scrape_coinmarketcap_api() -> list[dict]:
    """
    Scraping de CoinMarketCap usando su endpoint JSON interno
    (sin API key, usando endpoint de la web pública).
    """
    print("🔍 Usando CoinMarketCap data endpoint...")

    url = "https://api.coingecko.com/api/v3/coins/markets"
    params = {
        "vs_currency": "usd",
        "order": "market_cap_desc",
        "per_page": 100,
        "page": 1,
        "sparkline": False,
        "price_change_percentage": "1h,24h,7d,30d",
    }

    try:
        response = requests.get(url, params=params, headers=HEADERS, timeout=20)
        response.raise_for_status()
        data = response.json()
        print(f"   → Monedas obtenidas: {len(data)}")

        records = []
        for i, coin in enumerate(data, 1):
            records.append({
                "rank": i,
                "id": coin.get("id", ""),
                "symbol": coin.get("symbol", "").upper(),
                "name": coin.get("name", ""),
                "price_usd": coin.get("current_price"),
                "market_cap_usd": coin.get("market_cap"),
                "market_cap_rank": coin.get("market_cap_rank"),
                "fully_diluted_valuation": coin.get("fully_diluted_valuation"),
                "total_volume_24h_usd": coin.get("total_volume"),
                "high_24h_usd": coin.get("high_24h"),
                "low_24h_usd": coin.get("low_24h"),
                "price_change_24h_usd": coin.get("price_change_24h"),
                "change_1h_pct": coin.get("price_change_percentage_1h_in_currency"),
                "change_24h_pct": coin.get("price_change_percentage_24h"),
                "change_7d_pct": coin.get("price_change_percentage_7d_in_currency"),
                "change_30d_pct": coin.get("price_change_percentage_30d_in_currency"),
                "circulating_supply": coin.get("circulating_supply"),
                "total_supply": coin.get("total_supply"),
                "max_supply": coin.get("max_supply"),
                "ath_usd": coin.get("ath"),
                "ath_date": coin.get("ath_date"),
                "ath_change_pct": coin.get("ath_change_percentage"),
                "atl_usd": coin.get("atl"),
                "atl_date": coin.get("atl_date"),
                "last_updated": coin.get("last_updated"),
            })
        return records

    except Exception as e:
        print(f"   ❌ Error: {e}")
        return []


# ──────────────────────────────────────────────
# LIMPIEZA Y PROCESAMIENTO
# ──────────────────────────────────────────────

def clean_number(text: str) -> float | None:
    """Limpia texto y convierte a número."""
    try:
        cleaned = text.replace(",", "").replace(" ", "").strip()
        return float(cleaned)
    except Exception:
        return None


def clean_price(text: str) -> float | None:
    """Limpia texto de precio (maneja $, M, B, K)."""
    try:
        t = text.replace("$", "").replace(",", "").replace(" ", "").strip()
        if t.endswith("B"):
            return float(t[:-1]) * 1_000_000_000
        if t.endswith("M"):
            return float(t[:-1]) * 1_000_000
        if t.endswith("K"):
            return float(t[:-1]) * 1_000
        return float(t) if t else None
    except Exception:
        return None


def clean_pct(text: str) -> float | None:
    """Limpia texto de porcentaje."""
    try:
        return float(text.replace("%", "").replace("+", "").replace(" ", "").strip())
    except Exception:
        return None


def clean_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    """Aplica limpieza y enriquecimiento al DataFrame."""
    print("\n🧹 Limpiando y procesando datos...")

    original_rows = len(df)

    # Eliminar duplicados
    df = df.drop_duplicates(subset=["id"] if "id" in df.columns else ["name"])

    # Eliminar filas sin precio
    df = df.dropna(subset=["price_usd"])

    # Redondear columnas numéricas
    numeric_cols = [c for c in df.columns if any(
        x in c for x in ["price", "cap", "volume", "supply", "change", "pct", "high", "low"]
    )]
    for col in numeric_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")

    # Columnas derivadas
    if "market_cap_usd" in df.columns and "price_usd" in df.columns:
        df["market_cap_billions"] = (df["market_cap_usd"] / 1e9).round(3)

    if "ath_usd" in df.columns and "price_usd" in df.columns:
        df["pct_below_ath"] = (
            ((df["price_usd"] - df["ath_usd"]) / df["ath_usd"]) * 100
        ).round(2)

    if "circulating_supply" in df.columns and "max_supply" in df.columns:
        df["supply_pct_circulating"] = (
            (df["circulating_supply"] / df["max_supply"]) * 100
        ).round(2)

    # Columna de categoría por market cap
    def categorize(mc):
        if pd.isna(mc):
            return "Unknown"
        if mc >= 100e9:
            return "Mega Cap (>$100B)"
        if mc >= 10e9:
            return "Large Cap ($10B-$100B)"
        if mc >= 1e9:
            return "Mid Cap ($1B-$10B)"
        return "Small Cap (<$1B)"

    if "market_cap_usd" in df.columns:
        df["market_cap_category"] = df["market_cap_usd"].apply(categorize)

    # Columna de señal de tendencia 24h
    if "change_24h_pct" in df.columns:
        df["trend_24h"] = df["change_24h_pct"].apply(
            lambda x: "📈 Bullish" if x and x > 2 else (
                "📉 Bearish" if x and x < -2 else "➡️ Neutral"
            )
        )

    # Timestamp
    df["scraped_at"] = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")

    print(f"   ✅ Filas originales: {original_rows} → Filas limpias: {len(df)}")
    return df


# ──────────────────────────────────────────────
# GUARDAR CSV
# ──────────────────────────────────────────────

def save_csv(df: pd.DataFrame, filename: str = None) -> str:
    """Guarda el DataFrame en CSV con timestamp."""
    if filename is None:
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"crypto_top100_{ts}.csv"

    path = OUTPUT_DIR / filename
    df.to_csv(path, index=False, encoding="utf-8-sig")
    print(f"\n💾 CSV guardado en: {path}")
    print(f"   → Filas: {len(df)} | Columnas: {len(df.columns)}")
    return str(path)


def save_summary(df: pd.DataFrame) -> str:
    """Genera y guarda un resumen estadístico."""
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    path = OUTPUT_DIR / f"crypto_summary_{ts}.csv"

    summary_data = []

    if "market_cap_category" in df.columns:
        cat_summary = df.groupby("market_cap_category").agg(
            count=("name", "count"),
            avg_price=("price_usd", "mean"),
            avg_change_24h=("change_24h_pct", "mean"),
            total_market_cap=("market_cap_usd", "sum"),
        ).reset_index()
        cat_summary.to_csv(
            OUTPUT_DIR / f"crypto_by_category_{ts}.csv",
            index=False, encoding="utf-8-sig"
        )
        print(f"   → Resumen por categoría guardado")

    return str(path)


# ──────────────────────────────────────────────
# ANÁLISIS Y REPORTE
# ──────────────────────────────────────────────

def print_analysis(df: pd.DataFrame):
    """Imprime análisis de los datos scrapeados."""
    print("\n" + "="*60)
    print("📊 ANÁLISIS DE DATOS — TOP 100 CRIPTOMONEDAS")
    print("="*60)

    print(f"\n📈 ESTADÍSTICAS GENERALES:")
    print(f"   Total de monedas: {len(df)}")

    if "market_cap_usd" in df.columns:
        total_mc = df["market_cap_usd"].sum()
        print(f"   Market cap total: ${total_mc/1e12:.2f}T")

    if "price_usd" in df.columns:
        print(f"\n💵 PRECIOS:")
        print(f"   Más caro:  {df.loc[df['price_usd'].idxmax(), 'name']} (${df['price_usd'].max():,.2f})")
        print(f"   Más barat: {df.loc[df['price_usd'].idxmin(), 'name']} (${df['price_usd'].min():.8f})")

    if "change_24h_pct" in df.columns:
        df_ch = df.dropna(subset=["change_24h_pct"])
        if len(df_ch) > 0:
            print(f"\n📉 VARIACIONES 24H:")
            best = df_ch.loc[df_ch["change_24h_pct"].idxmax()]
            worst = df_ch.loc[df_ch["change_24h_pct"].idxmin()]
            avg = df_ch["change_24h_pct"].mean()
            bullish = (df_ch["change_24h_pct"] > 0).sum()
            print(f"   Mejor: {best['name']} (+{best['change_24h_pct']:.2f}%)")
            print(f"   Peor:  {worst['name']} ({worst['change_24h_pct']:.2f}%)")
            print(f"   Promedio: {avg:.2f}%")
            print(f"   En verde: {bullish}/{len(df_ch)} ({bullish/len(df_ch)*100:.0f}%)")

    if "market_cap_category" in df.columns:
        print(f"\n🏷️ POR CATEGORÍA:")
        for cat, count in df["market_cap_category"].value_counts().items():
            print(f"   {cat}: {count}")

    if "pct_below_ath" in df.columns:
        df_ath = df.dropna(subset=["pct_below_ath"])
        if len(df_ath) > 0:
            nearest = df_ath.loc[df_ath["pct_below_ath"].idxmax()]
            print(f"\n🏆 ATH:")
            print(f"   Más cercano a su ATH: {nearest['name']} ({nearest['pct_below_ath']:.1f}% del ATH)")

    print("\n" + "="*60)


# ──────────────────────────────────────────────
# MAIN
# ──────────────────────────────────────────────

def main():
    print("╔══════════════════════════════════════════╗")
    print("║   🪙  CRYPTO SCRAPER  v1.0              ║")
    print("║   Fuente: CoinGecko API pública         ║")
    print("╚══════════════════════════════════════════╝\n")

    start = time.time()

    # 1. Scraping
    records = scrape_coinmarketcap_api()

    if not records:
        print("❌ No se obtuvieron datos. Verifica tu conexión a internet.")
        sys.exit(1)

    # 2. Crear DataFrame
    df = pd.DataFrame(records)
    print(f"\n📋 DataFrame creado: {df.shape[0]} filas × {df.shape[1]} columnas")

    # 3. Limpiar y enriquecer
    df = clean_dataframe(df)

    # 4. Guardar CSV principal
    csv_path = save_csv(df)

    # 5. Guardar resúmenes
    save_summary(df)

    # 6. Análisis
    print_analysis(df)

    elapsed = time.time() - start
    print(f"\n✅ Completado en {elapsed:.1f}s")
    print(f"📁 Archivos en: {OUTPUT_DIR}/")
    print(f"\n📌 Vista previa (top 5):")
    cols_preview = ["rank", "name", "symbol", "price_usd", "change_24h_pct", "market_cap_billions"]
    available = [c for c in cols_preview if c in df.columns]
    print(df[available].head().to_string(index=False))

    return csv_path


if __name__ == "__main__":
    main()
