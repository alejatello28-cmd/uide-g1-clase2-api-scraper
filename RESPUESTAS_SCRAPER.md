# Trabajo Final — Módulo de Tratamiento de Datos
## Repositorio: uide-g1-clase2-api-scraper (Crypto Scraper)

---

## Pregunta 2: Qué desventajas en cuanto a tipo de información pueden preveer en cuanto a su scrapper?

### Contexto del proyecto

El scraper `scraper.py` extrae información de las **Top 100 criptomonedas** usando el endpoint público de CoinGecko, procesa los datos con **Pandas** y los exporta a CSV con 31 campos por criptomoneda. Si bien el sistema funciona correctamente para su propósito actual, el tipo de información que puede obtener presenta limitaciones estructurales importantes.

---
INTEGRANTE: Alejandra Tello
### Desventajas identificadas por tipo de información

#### 1. Datos de mercado limitados a un instante en el tiempo (snapshot)

El scraper captura los datos en el momento exacto en que se ejecuta (`scraped_at = datetime.utcnow()`), generando un **snapshot estático**. Los mercados de criptomonedas son extremadamente volátiles: Bitcoin puede variar un 5% en minutos.

**Consecuencia concreta en este proyecto:**

```
rank | name    | price_usd | scraped_at
  1  | Bitcoin | 95,243.18 | 2025-04-18 12:00:00  ← precio de ese momento exacto
  1  | Bitcoin | 94,100.00 | 2025-04-18 12:05:00  ← ya cambió
```

El CSV generado (`crypto_top100_20250418_120000.csv`) es inmediatamente obsoleto en un mercado que actualiza precios **cada 60 segundos**. No hay forma de saber qué ocurrió entre ejecuciones del scraper.

#### 2. Ausencia de datos de profundidad de mercado (Order Book)

El scraper obtiene el precio actual y volumen de 24h, pero **no puede capturar** la profundidad real del mercado, que es información crítica para entender si un precio es sostenible:

| Dato ausente | Por qué importa |
|---|---|
| Órdenes de compra (bids) | Indica el soporte real del precio |
| Órdenes de venta (asks) | Indica la resistencia real del precio |
| Spread bid-ask | Mide la liquidez real del mercado |
| Volumen por exchange | El volumen agregado puede ser engañoso |

El campo `total_volume_24h_usd` que extrae el scraper es un **agregado** de todos los exchanges. Un volumen alto puede ser artificial si está concentrado en un solo exchange con baja liquidez real.

#### 3. Columnas derivadas basadas en fórmulas simples que pueden ser engañosas

El scraper calcula columnas derivadas como:

```python
market_cap_billions = market_cap_usd / 1e9
pct_below_ath       = (price - ath) / ath * 100
supply_pct_circulating = circulating_supply / max_supply * 100
trend_24h           = "Bullish" / "Bearish" / "Neutral"
```

El campo `trend_24h` clasifica la tendencia basándose únicamente en el `change_24h_pct`, lo cual es una **simplificación excesiva**:

- Una moneda puede tener `change_24h_pct = +2%` (clasificada como "Bullish") pero estar en caída libre en los últimos 30 minutos.
- Una moneda puede tener `change_24h_pct = -0.5%` (clasificada como "Bearish") pero haber subido un 15% en la última hora.

**El campo `trend_24h` no refleja tendencia real, sino solo la variación diaria puntual.**

#### 4. Datos de suministro potencialmente incorrectos o incompletos

El scraper extrae `circulating_supply`, `total_supply` y `max_supply`. Sin embargo:

- **`max_supply` puede ser `null`** para monedas como Ethereum, que no tiene un límite máximo definido. Esto hace que `supply_pct_circulating` sea incalculable o genere división por cero.
- **`total_supply` vs `circulating_supply`** no siempre refleja la realidad: tokens bloqueados en contratos inteligentes aparecen como "circulantes" pero no están disponibles en el mercado.
- El scraper no captura el **cronograma de desbloqueo de tokens** (vesting schedules), que es determinante para predecir presión de venta futura.

#### 5. Categorización por market cap demasiado rígida

El scraper clasifica las monedas en categorías usando umbrales fijos:

```python
# Lógica aproximada del scraper
if market_cap > 10_000_000_000:   → "Mega Cap"
elif market_cap > 1_000_000_000:  → "Large Cap"
elif market_cap > 100_000_000:    → "Mid Cap"
else:                             → "Small Cap"
```

**Problema:** Estos umbrales son estáticos. En un mercado bajista, una moneda que era "Large Cap" puede pasar a "Mid Cap" simplemente por la caída del mercado general, no por un problema propio. El resumen por categoría (`crypto_by_category_*.csv`) puede llevar a conclusiones incorrectas si se comparan CSVs de diferentes fechas sin considerar el contexto del mercado.

#### 6. Dependencia total de un único endpoint público de CoinGecko

El scraper usa el endpoint `/coins/markets` de CoinGecko **sin API key**, lo que implica:

- **Solo devuelve las Top 100 por capitalización de mercado**: no hay acceso a monedas emergentes, tokens DeFi pequeños ni proyectos nuevos que podrían ser relevantes.
- **Los datos son los que CoinGecko decide mostrar**: si CoinGecko tiene datos incorrectos o desactualizados para una moneda, el scraper los replica sin validación cruzada.
- **Sin datos de exchanges específicos**: el precio es un promedio ponderado calculado por CoinGecko, no el precio real en ningún exchange en particular. Para trading real, este precio puede diferir significativamente del precio ejecutable.

#### 7. El campo `ath_date` pierde contexto temporal

El scraper extrae la fecha del All-Time High (`ath_date`) y el porcentaje por debajo del ATH (`pct_below_ath`), pero:

- No extrae **cuándo** ocurrió el ATH en relación al ciclo de mercado actual.
- Un ATH de hace 4 años (como el de Bitcoin en 2021) tiene implicaciones muy diferentes a un ATH de hace 3 meses.
- Sin este contexto, el campo `pct_below_ath` puede llevar a interpretaciones erróneas sobre el "potencial de recuperación" de una moneda.

#### 8. Ausencia de datos cualitativos y fundamentales

El scraper captura exclusivamente **datos cuantitativos de mercado**. No tiene acceso a información cualitativa que es determinante para evaluar una criptomoneda:

| Dato ausente | Relevancia |
|---|---|
| Estado del desarrollo (commits GitHub) | Indica si el proyecto está activo |
| Sentimiento en redes sociales | Influye directamente en el precio a corto plazo |
| Noticias y eventos recientes | Hacks, regulaciones, partnerships |
| Actividad on-chain (transacciones reales) | Distingue uso real de especulación |
| Equipo y transparencia del proyecto | Factor crítico de riesgo |


### Resumen de desventajas

| Categoría | Desventaja | Impacto |
|---|---|---|
| **Temporalidad** | Snapshot estático en mercado de alta volatilidad | Alto — datos obsoletos en minutos |
| **Profundidad** | Sin order book ni liquidez real por exchange | Alto — precio puede no ser ejecutable |
| **Derivadas** | `trend_24h` basado solo en variación diaria | Medio — clasificación simplista y engañosa |
| **Suministro** | `max_supply` nulo rompe columnas derivadas | Medio — errores en cálculos de supply |
| **Categorización** | Umbrales fijos no se adaptan al ciclo de mercado | Medio — comparaciones entre fechas inconsistentes |
| **Fuente única** | Solo Top 100 de CoinGecko sin validación cruzada | Alto — dependencia y sesgo de una sola fuente |
| **Contexto ATH** | Fecha del ATH sin contexto de ciclo de mercado | Bajo — interpretaciones erróneas |
| **Cualitativos** | Sin datos de desarrollo, sentimiento ni on-chain | Alto — visión incompleta del activo |

### Conclusión

El scraper es una herramienta válida para obtener una **fotografía general del mercado en un momento dado**, pero las desventajas en el tipo de información lo limitan a uso exploratorio y descriptivo. Para análisis financiero serio o toma de decisiones de inversión, sería necesario complementarlo con: datos históricos en series de tiempo, información on-chain, fuentes de datos de múltiples exchanges y análisis de sentimiento.
