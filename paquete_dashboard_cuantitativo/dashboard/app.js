/**
 * TradeStation Analytics - 30M Candles & Volume Profile Controller
 */

let candleChart = null;
let candleSeries = null;
let volumeSeries = null;
let pocPriceLine = null;
let vahPriceLine = null;
let valPriceLine = null;

let currentSymbol = "TSLA";
let currentDays = 15;
let currentMode = "global";

let cachedCandles = [];
let cachedProfileData = null;

// Inicialización
document.addEventListener("DOMContentLoaded", () => {
    initLightweightChart();
    loadInstruments();
    setupEventListeners();
});

function setupEventListeners() {
    const symbolSelect = document.getElementById("symbol-select");
    const rangeSelect = document.getElementById("range-select");
    const modeSelect = document.getElementById("vp-view-mode");
    const btnRefresh = document.getElementById("btn-refresh");

    symbolSelect.addEventListener("change", (e) => {
        currentSymbol = e.target.value;
        loadData();
    });

    rangeSelect.addEventListener("change", (e) => {
        currentDays = parseInt(e.target.value, 10);
        loadData();
    });

    modeSelect.addEventListener("change", (e) => {
        currentMode = e.target.value;
        renderPlotlyProfile();
    });

    btnRefresh.addEventListener("click", () => {
        loadData();
    });

    window.addEventListener("resize", () => {
        const container = document.getElementById("chart-candles");
        if (candleChart && container) {
            candleChart.applyOptions({
                width: container.clientWidth,
                height: container.clientHeight
            });
        }
        const profileBox = document.getElementById("chart-profile");
        if (profileBox && window.Plotly) {
            Plotly.Plots.resize(profileBox);
        }
    });
}

// Inicializar Lightweight Charts
function initLightweightChart() {
    const container = document.getElementById("chart-candles");
    if (!container) return;

    candleChart = LightweightCharts.createChart(container, {
        width: container.clientWidth,
        height: container.clientHeight,
        layout: {
            background: { color: "#121820" },
            textColor: "#8b949e",
            fontSize: 11,
            fontFamily: "'Roboto Mono', monospace"
        },
        grid: {
            vertLines: { color: "#1b2430" },
            horzLines: { color: "#1b2430" }
        },
        crosshair: {
            mode: LightweightCharts.CrosshairMode.Normal,
            vertLine: {
                color: "#58a6ff",
                width: 1,
                style: LightweightCharts.LineStyle.Dotted
            },
            horzLine: {
                color: "#58a6ff",
                width: 1,
                style: LightweightCharts.LineStyle.Dotted
            }
        },
        rightPriceScale: {
            borderColor: "#232f3e",
            scaleMargins: {
                top: 0.1,
                bottom: 0.2
            }
        },
        timeScale: {
            borderColor: "#232f3e",
            timeVisible: true,
            secondsVisible: false
        }
    });

    // Serie de Velas
    candleSeries = candleChart.addCandlestickSeries({
        upColor: "#089981",
        downColor: "#f23645",
        borderVisible: false,
        wickUpColor: "#089981",
        wickDownColor: "#f23645"
    });

    // Serie de Volumen (Sub-panel inferior)
    volumeSeries = candleChart.addHistogramSeries({
        color: "#26a69a",
        priceFormat: {
            type: "volume"
        },
        priceScaleId: "",
        scaleMargins: {
            top: 0.8,
            bottom: 0
        }
    });
}

// Cargar lista de instrumentos desde la API
async function loadInstruments() {
    try {
        const res = await fetch("/api/instruments");
        const json = await res.json();
        if (json.status === "success" && json.data.length > 0) {
            const select = document.getElementById("symbol-select");
            select.innerHTML = "";
            
            json.data.forEach((item) => {
                const opt = document.createElement("option");
                opt.value = item.symbol;
                opt.textContent = `${item.symbol} - ${item.name} (${item.type})`;
                if (item.symbol === currentSymbol) opt.selected = true;
                select.appendChild(opt);
            });

            document.getElementById("data-coverage-info").textContent = 
                `${json.data.length} instrumentos con histórico local disponible`;

            loadData();
        }
    } catch (err) {
        console.error("Error al cargar instrumentos:", err);
    }
}

// Cargar velas y perfil de volumen del activo seleccionado
async function loadData() {
    document.getElementById("candles-symbol-badge").textContent = currentSymbol;
    
    try {
        // 1. Fetch Velas 30M
        const candlesRes = await fetch(`/api/data/${currentSymbol}/candles?days=${currentDays}&year=2026`);
        const candlesJson = await candlesRes.json();
        
        if (candlesJson.status === "success") {
            cachedCandles = candlesJson.candles;
            renderCandles(cachedCandles);
        }

        // 2. Fetch Perfil de Volumen
        const profileRes = await fetch(`/api/data/${currentSymbol}/volume_profile?days=${currentDays}&year=2026&bins=60`);
        const profileJson = await profileRes.json();

        if (profileJson.status === "success") {
            cachedProfileData = profileJson.data;
            renderPlotlyProfile();
            updateKPIs();
        }
    } catch (err) {
        console.error("Error cargando datos:", err);
    }
}

// Renderizar Velas 30M y Líneas de Niveles Clave (POC, VAH, VAL)
function renderCandles(candles) {
    if (!candles || candles.length === 0) return;

    const candleData = candles.map((c) => ({
        time: c.time,
        open: c.open,
        high: c.high,
        low: c.low,
        close: c.close
    }));

    const volData = candles.map((c) => ({
        time: c.time,
        value: c.volume,
        color: c.close >= c.open ? "rgba(8, 153, 129, 0.4)" : "rgba(242, 54, 69, 0.4)"
    }));

    candleSeries.setData(candleData);
    volumeSeries.setData(volData);

    candleChart.timeScale().fitContent();

    // Rango de fechas
    const firstDate = candles[0].date;
    const lastDate = candles[candles.length - 1].date;
    document.getElementById("candles-date-badge").textContent = `${firstDate} -> ${lastDate}`;
}

// Renderizar Perfil de Volumen en Plotly.js
function renderPlotlyProfile() {
    const profileBox = document.getElementById("chart-profile");
    if (!profileBox || !cachedProfileData) return;

    const gp = cachedProfileData.global_profile;
    if (!gp || !gp.prices) return;

    // Actualizar líneas de referencia en el gráfico de velas
    updateChartPriceLines(gp.poc, gp.vah, gp.val);

    if (currentMode === "global") {
        // Vista 1: Perfil Global Consolidado
        const traceBuy = {
            x: gp.buy_volumes,
            y: gp.prices,
            name: "Volumen Comprador",
            type: "bar",
            orientation: "h",
            marker: {
                color: "#089981",
                opacity: 0.85
            }
        };

        const traceSell = {
            x: gp.sell_volumes,
            y: gp.prices,
            name: "Volumen Vendedor",
            type: "bar",
            orientation: "h",
            marker: {
                color: "#f23645",
                opacity: 0.85
            }
        };

        const layout = {
            barmode: "stack",
            paper_bgcolor: "#121820",
            plot_bgcolor: "#121820",
            margin: { l: 60, r: 20, t: 30, b: 40 },
            showlegend: true,
            legend: {
                font: { color: "#8b949e", size: 10, family: "Inter" },
                orientation: "h",
                x: 0,
                y: 1.08
            },
            xaxis: {
                title: "Volumen Acumulado",
                titlefont: { size: 11, color: "#8b949e" },
                tickfont: { size: 10, color: "#8b949e" },
                gridcolor: "#1b2430",
                zerolinecolor: "#232f3e"
            },
            yaxis: {
                title: "Precio",
                titlefont: { size: 11, color: "#8b949e" },
                tickfont: { size: 10, color: "#8b949e" },
                gridcolor: "#1b2430",
                side: "right"
            },
            shapes: [
                // Línea POC
                {
                    type: "line",
                    x0: 0,
                    x1: Math.max(...gp.volumes) * 1.1,
                    y0: gp.poc,
                    y1: gp.poc,
                    line: {
                        color: "#ffd700",
                        width: 2,
                        dash: "dash"
                    }
                },
                // Línea VAH
                {
                    type: "line",
                    x0: 0,
                    x1: Math.max(...gp.volumes) * 0.9,
                    y0: gp.vah,
                    y1: gp.vah,
                    line: {
                        color: "#00e676",
                        width: 1.5,
                        dash: "dot"
                    }
                },
                // Línea VAL
                {
                    type: "line",
                    x0: 0,
                    x1: Math.max(...gp.volumes) * 0.9,
                    y0: gp.val,
                    y1: gp.val,
                    line: {
                        color: "#2979ff",
                        width: 1.5,
                        dash: "dot"
                    }
                }
            ],
            annotations: [
                {
                    x: Math.max(...gp.volumes) * 0.8,
                    y: gp.poc,
                    text: `POC: ${gp.poc}`,
                    showarrow: false,
                    font: { color: "#ffd700", size: 10, family: "Roboto Mono" },
                    bgcolor: "rgba(255, 215, 0, 0.15)",
                    bordercolor: "#ffd700",
                    borderwidth: 1
                },
                {
                    x: Math.max(...gp.volumes) * 0.8,
                    y: gp.vah,
                    text: `VAH: ${gp.vah}`,
                    showarrow: false,
                    font: { color: "#00e676", size: 10, family: "Roboto Mono" },
                    bgcolor: "rgba(0, 230, 118, 0.15)",
                    bordercolor: "#00e676",
                    borderwidth: 1
                },
                {
                    x: Math.max(...gp.volumes) * 0.8,
                    y: gp.val,
                    text: `VAL: ${gp.val}`,
                    showarrow: false,
                    font: { color: "#2979ff", size: 10, family: "Roboto Mono" },
                    bgcolor: "rgba(41, 121, 255, 0.15)",
                    bordercolor: "#2979ff",
                    borderwidth: 1
                }
            ]
        };

        Plotly.newPlot(profileBox, [traceBuy, traceSell], layout, {
            responsive: true,
            displayModeBar: false
        });

    } else {
        // Vista 2: Sesiones Diarias Multi-Perfil
        const sessions = cachedProfileData.sessions || [];
        const traces = [];
        const shapes = [];

        sessions.forEach((s, idx) => {
            traces.push({
                x: s.volumes,
                y: s.prices,
                name: s.date,
                type: "bar",
                orientation: "h",
                opacity: 0.75
            });

            // Línea POC de cada sesión
            shapes.push({
                type: "line",
                x0: 0,
                x1: Math.max(...s.volumes) * 1.1,
                y0: s.poc,
                y1: s.poc,
                line: {
                    color: "#ffd700",
                    width: 1.5,
                    dash: "dot"
                }
            });
        });

        const layout = {
            barmode: "overlay",
            paper_bgcolor: "#121820",
            plot_bgcolor: "#121820",
            margin: { l: 60, r: 20, t: 30, b: 40 },
            showlegend: true,
            legend: {
                font: { color: "#8b949e", size: 9, family: "Inter" },
                orientation: "h",
                x: 0,
                y: 1.1
            },
            xaxis: {
                title: "Volumen por Sesión",
                titlefont: { size: 11, color: "#8b949e" },
                tickfont: { size: 10, color: "#8b949e" },
                gridcolor: "#1b2430"
            },
            yaxis: {
                title: "Precio",
                titlefont: { size: 11, color: "#8b949e" },
                tickfont: { size: 10, color: "#8b949e" },
                gridcolor: "#1b2430",
                side: "right"
            },
            shapes: shapes
        };

        Plotly.newPlot(profileBox, traces, layout, {
            responsive: true,
            displayModeBar: false
        });
    }
}

// Sincronizar Líneas de Referencia en el Gráfico de Velas
function updateChartPriceLines(poc, vah, val) {
    if (!candleSeries) return;

    if (pocPriceLine) candleSeries.removePriceLine(pocPriceLine);
    if (vahPriceLine) candleSeries.removePriceLine(vahPriceLine);
    if (valPriceLine) candleSeries.removePriceLine(valPriceLine);

    if (poc) {
        pocPriceLine = candleSeries.createPriceLine({
            price: poc,
            color: "#ffd700",
            lineWidth: 2,
            lineStyle: LightweightCharts.LineStyle.Dashed,
            axisLabelVisible: true,
            title: "POC"
        });
    }

    if (vah) {
        vahPriceLine = candleSeries.createPriceLine({
            price: vah,
            color: "#00e676",
            lineWidth: 1,
            lineStyle: LightweightCharts.LineStyle.Dotted,
            axisLabelVisible: true,
            title: "VAH"
        });
    }

    if (val) {
        valPriceLine = candleSeries.createPriceLine({
            price: val,
            color: "#2979ff",
            lineWidth: 1,
            lineStyle: LightweightCharts.LineStyle.Dotted,
            axisLabelVisible: true,
            title: "VAL"
        });
    }
}

// Actualizar Tarjetas de KPIs Cuantitativos
function updateKPIs() {
    if (!cachedCandles || cachedCandles.length === 0 || !cachedProfileData) return;

    const lastCandle = cachedCandles[cachedCandles.length - 1];
    const firstCandle = cachedCandles[0];
    const gp = cachedProfileData.global_profile;

    const lastPrice = lastCandle.close;
    const priceChange = ((lastPrice - firstCandle.open) / firstCandle.open) * 100;

    document.getElementById("kpi-price").textContent = lastPrice.toFixed(2);
    const changeEl = document.getElementById("kpi-change");
    changeEl.textContent = `${priceChange >= 0 ? "+" : ""}${priceChange.toFixed(2)}% en el período`;
    changeEl.style.color = priceChange >= 0 ? "var(--color-bull)" : "var(--color-bear)";

    document.getElementById("kpi-poc").textContent = gp.poc ? gp.poc.toFixed(2) : "--";
    document.getElementById("kpi-vah").textContent = gp.vah ? gp.vah.toFixed(2) : "--";
    document.getElementById("kpi-val").textContent = gp.val ? gp.val.toFixed(2) : "--";

    const totalBuy = gp.buy_volumes.reduce((a, b) => a + b, 0);
    const totalSell = gp.sell_volumes.reduce((a, b) => a + b, 0);
    const totalVol = totalBuy + totalSell;
    const buyPct = totalVol > 0 ? ((totalBuy / totalVol) * 100).toFixed(1) : 50;
    const sellPct = totalVol > 0 ? ((totalSell / totalVol) * 100).toFixed(1) : 50;

    document.getElementById("kpi-total-vol").textContent = formatNumber(gp.total_volume);
    document.getElementById("kpi-delta").textContent = `Comp: ${buyPct}% | Vent: ${sellPct}%`;

    const rangeDiff = (gp.max_price - gp.min_price).toFixed(2);
    document.getElementById("kpi-range").textContent = `${gp.min_price} - ${gp.max_price} (Δ ${rangeDiff})`;
    document.getElementById("kpi-candles-count").textContent = `${cachedCandles.length} velas de 30M`;
}

function formatNumber(num) {
    if (!num) return "0";
    if (num >= 1e9) return (num / 1e9).toFixed(2) + "B";
    if (num >= 1e6) return (num / 1e6).toFixed(2) + "M";
    if (num >= 1e3) return (num / 1e3).toFixed(1) + "K";
    return num.toString();
}
