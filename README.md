<img width="1291" height="717" alt="image" src="https://github.com/user-attachments/assets/81881859-b55f-4d75-84bb-b0bb02749a5a" /><img width="1285" height="728" alt="image" src="https://github.com/user-attachments/assets/50764f64-d1be-4385-be83-be98ead1109e" /># 🪙 Crypto Scraper — Top 100 Criptomonedas

[![Python](https://img.shields.io/badge/Python-3.11+-3776AB?style=flat&logo=python&logoColor=white)](https://python.org)
[![Pandas](https://img.shields.io/badge/Pandas-2.2-150458?style=flat&logo=pandas)](https://pandas.pydata.org)
[![BeautifulSoup](https://img.shields.io/badge/BeautifulSoup-4.12-green?style=flat)](https://www.crummy.com/software/BeautifulSoup/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](./LICENSE)

Scraper de datos financieros que extrae información de las **Top 100 criptomonedas** usando la API pública de CoinGecko. Incluye limpieza de datos, enriquecimiento con columnas derivadas y exportación a CSV.

---

## 📋 Tabla de Contenidos

- [¿Qué extrae?](#-qué-extrae)
- [Proceso completo](#-proceso-completo)
- [Instalación](#-instalación)
- [Uso](#-uso)
- [Datos de salida](#-datos-de-salida)
- [Screenshots](#-screenshots)
- [Estructura del proyecto](#-estructura-del-proyecto)

---

## 📊 ¿Qué extrae?

El scraper obtiene **31 campos** por cada criptomoneda:

### Datos crudos (scrapeados)
| Campo | Descripción |
|-------|-------------|
| `rank` | Posición en el ranking |
| `id` | Identificador único (ej: `bitcoin`) |
| `symbol` | Símbolo del ticker (ej: `BTC`) |
| `name` | Nombre completo |
| `price_usd` | Precio actual en USD |
| `market_cap_usd` | Capitalización de mercado |
| `total_volume_24h_usd` | Volumen de trading en 24h |
| `high_24h_usd` | Precio máximo en 24h |
| `low_24h_usd` | Precio mínimo en 24h |
| `change_1h_pct` | Variación porcentual 1 hora |
| `change_24h_pct` | Variación porcentual 24 horas |
| `change_7d_pct` | Variación porcentual 7 días |
| `change_30d_pct` | Variación porcentual 30 días |
| `circulating_supply` | Suministro circulante |
| `total_supply` | Suministro total |
| `max_supply` | Suministro máximo |
| `ath_usd` | All-Time High en USD |
| `ath_date` | Fecha del ATH |
| `atl_usd` | All-Time Low en USD |
| `last_updated` | Última actualización |

### Columnas derivadas (procesadas)
| Campo | Descripción | Cómo se calcula |
|-------|-------------|-----------------|
| `market_cap_billions` | Market cap en miles de millones | `market_cap_usd / 1e9` |
| `pct_below_ath` | % que está por debajo del ATH | `(price - ath) / ath * 100` |
| `supply_pct_circulating` | % del supply en circulación | `circulating / max_supply * 100` |
| `market_cap_category` | Categoría por tamaño | Mega/Large/Mid/Small Cap |
| `trend_24h` | Señal de tendencia del día | Bullish/Bearish/Neutral |
| `scraped_at` | Timestamp del scraping | `datetime.utcnow()` |

---

## 🔄 Proceso completo

```
┌─────────────────┐     ┌──────────────────┐     ┌─────────────────┐     ┌──────────────┐
│   1. SCRAPING   │────▶│  2. PARSING      │────▶│  3. LIMPIEZA    │────▶│  4. GUARDAR  │
│                 │     │                  │     │                 │     │              │
│ CoinGecko API   │     │ JSON → DataFrame │     │ • Deduplicar    │     │ CSV + resumen│
│ (endpoint       │     │ 100 registros    │     │ • Dropna        │     │ por categoría│
│  público)       │     │ 24 columnas      │     │ • Columnas      │     │              │
│                 │     │                  │     │   derivadas     │     │              │
└─────────────────┘     └──────────────────┘     └─────────────────┘     └──────────────┘
```

---

## 🚀 Instalación

```bash
# 1. Clonar el repositorio
git clone https://github.com/alejatello28-cmd/uide-g1-clase2-api-scraper.git
cd uide-g1-clase2-api-scraper

# 2. Crear entorno virtual
python -m venv venv
source venv/bin/activate     # Linux/Mac
venv\Scripts\activate        # Windows

# 3. Instalar dependencias
pip install -r requirements.txt
```

---

## ▶️ Uso

```bash
# Ejecutar el scraper
python scraper.py
```

### Salida esperada en consola

```
╔══════════════════════════════════════════╗
║   🪙  CRYPTO SCRAPER  v1.0              ║
║   Fuente: CoinGecko API pública         ║
╚══════════════════════════════════════════╝

🔍 Usando CoinMarketCap data endpoint...
   → Monedas obtenidas: 100

🧹 Limpiando y procesando datos...
   ✅ Filas originales: 100 → Filas limpias: 100

💾 CSV guardado en: data/crypto_top100_20250418_120000.csv
   → Filas: 100 | Columnas: 31
   → Resumen por categoría guardado

============================================================
📊 ANÁLISIS DE DATOS — TOP 100 CRIPTOMONEDAS
============================================================

📈 ESTADÍSTICAS GENERALES:
   Total de monedas: 100
   Market cap total: $3.21T

💵 PRECIOS:
   Más caro:  Bitcoin ($95,243.18)
   Más barat: Shiba Inu ($0.00001120)

📉 VARIACIONES 24H:
   Mejor: Chainlink (+6.21%)
   Peor:  Avalanche (-8.42%)
   Promedio: -1.23%
   En verde: 38/100 (38%)

🏷️ POR CATEGORÍA:
   Mega Cap (>$100B): 4
   Large Cap ($10B-$100B): 14
   Mid Cap ($1B-$10B): 48
   Small Cap (<$1B): 34

🏆 ATH:
   Más cercano a su ATH: Bitcoin (-11.8% del ATH)

============================================================

✅ Completado en 2.3s
📁 Archivos en: data/

📌 Vista previa (top 5):
 rank      name symbol  price_usd  change_24h_pct  market_cap_billions
    1   Bitcoin    BTC  95243.18            1.32              1884.000
    2  Ethereum    ETH   1812.44           -1.17               218.000
    3    Tether   USDT      1.00            0.01               144.000
    4       BNB    BNB    598.71            0.52                86.900
    5    Solana    SOL    131.22           -2.09                67.600
```

---

## 📁 Datos de salida

El scraper genera archivos en la carpeta `data/`:

```
data/
├── crypto_top100_20250418_120000.csv      ← Dataset principal (100 filas, 31 cols)
└── crypto_by_category_20250418_120000.csv ← Resumen por categoría de market cap
```

### Vista del CSV principal

```csv
rank,id,symbol,name,price_usd,market_cap_usd,change_24h_pct,market_cap_billions,trend_24h,...
1,bitcoin,BTC,Bitcoin,95243.18,1884000000000,1.32,1884.0,➡️ Neutral,...
2,ethereum,ETH,Ethereum,1812.44,218000000000,-1.17,218.0,➡️ Neutral,...
3,tether,USDT,Tether,1.0,144000000000,0.01,144.0,➡️ Neutral,...
```

### Vista del resumen por categoría

```csv
market_cap_category,count,avg_price,avg_change_24h,total_market_cap
Mega Cap (>$100B),4,23765.55,-0.21,2369000000000
Large Cap ($10B-$100B),14,89.34,-1.84,631000000000
Mid Cap ($1B-$10B),48,12.45,-2.31,148000000000
Small Cap (<$1B),34,0.89,-3.12,14000000000
```

---

## 📸 Screenshots
<img width="886" height="421" alt="image" src="https://github.com/user-attachments/assets/60c05887-5940-4101-a709-11ec11b74c17" />
<img width="886" height="600" alt="image" src="https://github.com/user-attachments/assets/831178e7-388f-49f9-99e4-3f4d7718a399" />
<img width="886" height="236" alt="image" src="https://github.com/user-attachments/assets/0885b160-5632-44c5-b279-30b11d8c2416" />


## Datos para análisis

<img width="886" height="316" alt="image" src="https://github.com/user-attachments/assets/da523748-d1aa-47a0-842a-68914e24d5ce" />
<img width="886" height="316" alt="image" src="https://github.com/user-attachments/assets/fe020d63-6b28-4e0e-b1b7-3e21182ebba7" />


### Ejecución del scraper

```
$ python scraper.py

🔍 Usando CoinMarketCap data endpoint...
   → Monedas obtenidas: 100
🧹 Limpiando y procesando datos...
   ✅ Filas originales: 100 → Filas limpias: 100
💾 CSV guardado en: data/crypto_top100_20250418_120000.csv
```

### CSV abierto en Excel / LibreOffice

| rank | name | symbol | price_usd | change_24h_pct | market_cap_billions | trend_24h |
|------|------|--------|-----------|---------------|---------------------|-----------|
| 1 | Bitcoin | BTC | 95,243.18 | +1.32% | 1,884.0 | ➡️ Neutral |
| 2 | Ethereum | ETH | 1,812.44 | -1.17% | 218.0 | ➡️ Neutral |
| 3 | Tether | USDT | 1.00 | +0.01% | 144.0 | ➡️ Neutral |
| 4 | BNB | BNB | 598.71 | +0.52% | 86.9 | ➡️ Neutral |
| 5 | Solana | SOL | 131.22 | -2.09% | 67.6 | 📉 Bearish |

---

## 📂 Estructura del proyecto

```
crypto-scraper/
├── scraper.py          # Script principal
├── requirements.txt    # Dependencias
├── README.md           # Documentación
└── data/               # CSVs generados (creado al ejecutar)
    ├── crypto_top100_*.csv
    └── crypto_by_category_*.csv
```

---

## 🛠 Tecnologías

| Librería | Versión | Uso |
|----------|---------|-----|
| [requests](https://requests.readthedocs.io) | 2.32 | HTTP requests |
| [BeautifulSoup4](https://www.crummy.com/software/BeautifulSoup/) | 4.12 | Parsing HTML |
| [pandas](https://pandas.pydata.org) | 2.2 | Procesamiento de datos |
| [lxml](https://lxml.de) | 5.3 | Parser XML/HTML rápido |

**Fuente de datos:** [CoinGecko API](https://www.coingecko.com/en/api) — Endpoint público gratuito, sin API key requerida.

---

## ⚠️ Notas

- El scraper respeta los rate limits de la API pública de CoinGecko.
- Los datos se actualizan cada ~60 segundos en la fuente.
- Para uso intensivo se recomienda obtener una [API key gratuita de CoinGecko](https://www.coingecko.com/en/api/pricing).

---

## 📄 Licencia

MIT © 2025 — Crypto Scraper
