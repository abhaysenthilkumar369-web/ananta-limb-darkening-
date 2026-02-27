import React, { useMemo } from 'react';
import Plotly from 'plotly.js-basic-dist';
import createPlotlyComponent from 'react-plotly.js/factory';

const Plot = createPlotlyComponent(Plotly);

export const ResultsGraphs = ({ analysisData, selectedModel }) => {
    // Extract parsed data from backend
    const { mu_array, i_norm_array, results } = analysisData;

    // 1. Distance vs Gray Value Plot (Reconstruct the symmetric Dome)
    const driftScanData = useMemo(() => {
        // r_norm = sqrt(1 - mu^2)
        const r_norm = mu_array.map(mu => Math.sqrt(1 - mu * mu));

        // Symmetric array from -1 to 1
        const r_full = [...[...r_norm].reverse().map(r => -r), ...r_norm];
        const i_full = [...[...i_norm_array].reverse(), ...i_norm_array];

        return [
            {
                x: r_full,
                y: i_full,
                type: 'scatter',
                mode: 'markers',
                marker: { color: 'rgba(255, 255, 255, 0.4)', size: 4 },
                name: 'Observed Profile',
                hoverinfo: 'x+y'
            }
        ];
    }, [mu_array, i_norm_array]);

    // 2. Solar Limb Darkening Plot
    const limbDarkeningData = useMemo(() => {
        const traces = [
            {
                x: mu_array,
                y: i_norm_array,
                type: 'scatter',
                mode: 'markers',
                marker: { color: 'rgba(255, 255, 255, 0.6)', size: 4 },
                name: 'Observational Data',
            }
        ];

        results.forEach((res, i) => {
            // Teal accent for the fitted line
            const color = results.length === 1 ? '#00D4FF' : `hsl(${i * 60 + 180}, 100%, 50%)`;

            traces.push({
                x: mu_array,
                y: res.fitted_curve_y,
                type: 'scatter',
                mode: 'lines',
                line: { color: color, width: 3 },
                name: `Fit: ${res.model_type.charAt(0).toUpperCase() + res.model_type.slice(1)}`,
            });
        });

        return traces;
    }, [mu_array, i_norm_array, results]);

    // 3. Residuals Plot
    const residualsData = useMemo(() => {
        if (results.length !== 1) return null;
        const res = results[0];
        return [
            {
                x: mu_array,
                y: res.residuals,
                type: 'scatter',
                mode: 'markers',
                marker: { color: '#ff4d4d', size: 4 },
                name: 'Residuals'
            },
            {
                x: [0, 1],
                y: [0, 0],
                type: 'scatter',
                mode: 'lines',
                line: { color: 'white', dash: 'dash', width: 1 },
                showlegend: false
            }
        ];
    }, [mu_array, results]);

    const layoutBase = {
        paper_bgcolor: 'rgba(0,0,0,0)',
        plot_bgcolor: 'rgba(0,0,0,0)',
        font: { color: '#ffffff', family: '"Inter", sans-serif' },
        margin: { t: 40, r: 20, l: 50, b: 40 },
        xaxis: { showgrid: true, gridcolor: 'rgba(255,255,255,0.1)', zeroline: false },
        yaxis: { showgrid: true, gridcolor: 'rgba(255,255,255,0.1)', zeroline: false },
        legend: { x: 0.95, xanchor: 'right', y: 0.95, yanchor: 'top', bgcolor: 'rgba(10,37,64,0.7)', bordercolor: 'rgba(255,255,255,0.2)', borderwidth: 1 },
        hovermode: 'closest'
    };

    return (
        <div className="flex flex-col gap-6 mt-8">
            {/* Plot 1: Drift Scan */}
            <div className="glass-panel p-4 pb-8 overflow-hidden relative">
                <h3 className="text-xl font-semibold mb-2 text-center">Distance vs Gray Value</h3>
                <div className="flex justify-between text-xs text-white/50 px-10 absolute top-12 w-full z-10 pointer-events-none">
                    <span className="bg-space-dark/80 px-2 py-1 rounded">Preceding Limb</span>
                    <span className="bg-space-dark/80 px-2 py-1 rounded">Following Limb</span>
                </div>
                <Plot
                    data={driftScanData}
                    layout={{
                        ...layoutBase,
                        xaxis: { ...layoutBase.xaxis, title: 'Distance (pixels)' },
                        yaxis: { ...layoutBase.yaxis, title: 'Gray Value (I / I_max)' },
                        height: 400
                    }}
                    useResizeHandler={true}
                    className="w-full"
                    config={{ displayModeBar: false }}
                />
            </div>

            {/* Plot 2: Limb Darkening Profile & Residuals */}
            <div className="glass-panel p-4 overflow-hidden">
                <h3 className="text-xl font-semibold mb-2 text-center">Solar Limb Darkening</h3>
                <Plot
                    data={limbDarkeningData}
                    layout={{
                        ...layoutBase,
                        xaxis: { showgrid: true, gridcolor: 'rgba(255,255,255,0.1)', title: 'μ = cos(θ)', autorange: 'reversed' },
                        yaxis: { showgrid: true, gridcolor: 'rgba(255,255,255,0.1)', title: 'Normalized Intensity' },
                        height: 400
                    }}
                    useResizeHandler={true}
                    className="w-full"
                    config={{ displayModeBar: false }}
                />
            </div>

            {/* Plot 3: Residuals (only show if single model selected) */}
            {residualsData && (
                <div className="glass-panel p-4 overflow-hidden mt-[-10px]">
                    <h3 className="text-sm font-semibold mb-1 text-center text-white/70">Residuals</h3>
                    <Plot
                        data={residualsData}
                        layout={{
                            ...layoutBase,
                            xaxis: { showgrid: true, gridcolor: 'rgba(255,255,255,0.1)', title: 'μ = cos(θ)', autorange: 'reversed' },
                            yaxis: { showgrid: true, gridcolor: 'rgba(255,255,255,0.1)', title: 'Observed - Fitted' },
                            height: 200,
                            margin: { t: 10, r: 20, l: 50, b: 40 },
                            legend: { orientation: "h", y: -0.3 }
                        }}
                        useResizeHandler={true}
                        className="w-full"
                        config={{ displayModeBar: false }}
                    />
                </div>
            )}
        </div>
    );
};
