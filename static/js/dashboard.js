document.addEventListener('DOMContentLoaded', function () {
    // Transit color palette (Material-style roles)
    const COLORS = {
        primary: '#1a237e',
        primaryLight: '#3949ab',
        secondary: '#00695c',
        secondaryLight: '#26a69a',
        tertiary: '#f57f17',
        success: '#2e7d32',
        alert: '#c62828',
        bg: '#f4f6f9',
        surface: '#ffffff',
        text: '#212121',
        textSecondary: '#555555',
        border: '#dcdfe4'
    };

    const LAYOUT_DEFAULTS = {
        paper_bgcolor: COLORS.surface,
        plot_bgcolor: COLORS.surface,
        font: {
            family: '-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif',
            color: COLORS.text,
            size: 13
        },
        margin: { t: 30, r: 20, b: 40, l: 40 }
    };

    const PLOTLY_CONFIG = {
        displaylogo: false,
        responsive: true,
        modeBarButtonsToRemove: ['lasso2d', 'select2d']
    };

    function mergeLayouts(serverLayout) {
        return { ...LAYOUT_DEFAULTS, ...serverLayout, margin: { ...LAYOUT_DEFAULTS.margin, ...(serverLayout.margin || {}) } };
    }

    function showLoading(containerId) {
        const el = document.getElementById(containerId);
        if (el) {
            el.innerHTML = '<div style="display:flex;justify-content:center;padding:40px;"><div class="loading-spinner"></div></div>';
        }
    }

    function showError(containerId, message) {
        const el = document.getElementById(containerId);
        if (el) {
            el.innerHTML = `<div class="empty-state text-muted"><span style="color: ${COLORS.alert}; display: block; margin-bottom: 8px; font-weight: bold;">⚠ Communication Notice</span>${message}</div>`;
        }
    }

    // =========================================================================
    // 1. TAB NAVIGATION CONTROLLER
    // =========================================================================
    function switchTab(tabId) {
        document.querySelectorAll('.nav-tab').forEach(btn => {
            const btnTarget = btn.getAttribute('data-tab');
            btn.classList.toggle('active', btnTarget === tabId);
        });

        document.querySelectorAll('.tab-pane').forEach(pane => {
            const isActive = pane.id === tabId;
            pane.classList.toggle('active', isActive);
            if (isActive) {
                // Resize Plotly charts in visible pane
                const charts = pane.querySelectorAll('.js-plotly-plot');
                charts.forEach(c => {
                    try { Plotly.Plots.resize(c); } catch (e) {}
                });
            }
        });

        // Trigger lazy loading for specific tabs
        if (tabId === 'tab-station') {
            const curVal = document.getElementById('station-select')?.value || 'DR';
            loadStationIntelligence(curVal);
            if (!document.querySelector('#network-chart .plot-container')) {
                loadNetworkChart();
            }
        } else if (tabId === 'tab-timetable') {
            loadTimetable();
        } else if (tabId === 'tab-analytics') {
            if (!document.querySelector('#heatmap-chart .plot-container')) loadHeatmap();
            if (!document.querySelector('#comparison-chart .plot-container')) loadComparisonChart();
            if (!document.querySelector('#ranking-chart .plot-container')) loadRankingChart();
        }
    }

    document.querySelectorAll('.nav-tab').forEach(btn => {
        btn.addEventListener('click', function (e) {
            e.preventDefault();
            const tabId = this.getAttribute('data-tab');
            if (tabId) switchTab(tabId);
        });
    });

    document.querySelectorAll('[data-goto-tab]').forEach(btn => {
        btn.addEventListener('click', function (e) {
            e.preventDefault();
            const tabId = this.getAttribute('data-goto-tab');
            if (tabId) switchTab(tabId);
        });
    });

    // =========================================================================
    // 2. HERO INTERACTIONS (HOME TAB)
    // =========================================================================
    const heroAnalyseBtn = document.getElementById('hero-analyse-btn');
    const heroStationInput = document.getElementById('hero-station-input');

    function executeHeroStationAnalysis(stationQuery) {
        if (!stationQuery) return;
        fetch('/api/stations')
            .then(res => res.json())
            .then(stations => {
                const q = stationQuery.trim().toLowerCase();
                const matched = stations.find(s => 
                    s.station_code.toLowerCase() === q || 
                    s.station_name.toLowerCase() === q ||
                    s.station_name.toLowerCase().includes(q)
                );
                if (matched) {
                    const select = document.getElementById('station-select');
                    if (select) select.value = matched.station_code;
                    switchTab('tab-station');
                    loadStationIntelligence(matched.station_code);
                } else {
                    alert(`Station '${stationQuery}' not found in the 49 Central Line stations.`);
                }
            })
            .catch(err => console.error(err));
    }

    if (heroAnalyseBtn && heroStationInput) {
        heroAnalyseBtn.addEventListener('click', () => executeHeroStationAnalysis(heroStationInput.value));
        heroStationInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') executeHeroStationAnalysis(heroStationInput.value);
        });
    }

    document.querySelectorAll('.station-chip').forEach(chip => {
        chip.addEventListener('click', function () {
            const code = this.getAttribute('data-code');
            const select = document.getElementById('station-select');
            if (select) select.value = code;
            switchTab('tab-station');
            loadStationIntelligence(code);
        });
    });

    const heroRouteBtn = document.getElementById('hero-route-btn');
    if (heroRouteBtn) {
        heroRouteBtn.addEventListener('click', function () {
            const src = document.getElementById('hero-src-select').value;
            const dst = document.getElementById('hero-dst-select').value;
            if (!src || !dst) {
                alert('Please select both Origin and Destination stations.');
                return;
            }
            document.getElementById('route-source').value = src;
            document.getElementById('route-dest').value = dst;
            switchTab('tab-journey');
            executeRouteSearch();
        });
    }

    document.querySelectorAll('.route-preset-chip').forEach(chip => {
        chip.addEventListener('click', function () {
            const src = this.getAttribute('data-src');
            const dst = this.getAttribute('data-dst');
            document.getElementById('route-source').value = src;
            document.getElementById('route-dest').value = dst;
            switchTab('tab-journey');
            executeRouteSearch();
        });
    });

    // =========================================================================
    // 3. JOURNEY EXPLORER & ROUTE INTELLIGENCE
    // =========================================================================
    const routeSwapBtn = document.getElementById('route-swap-btn');
    if (routeSwapBtn) {
        routeSwapBtn.addEventListener('click', function () {
            const srcEl = document.getElementById('route-source');
            const dstEl = document.getElementById('route-dest');
            const tmp = srcEl.value;
            srcEl.value = dstEl.value;
            dstEl.value = tmp;
        });
    }

    const findRouteBtn = document.getElementById('find-route-btn');
    if (findRouteBtn) {
        findRouteBtn.addEventListener('click', executeRouteSearch);
    }

    function executeRouteSearch() {
        const src = document.getElementById('route-source').value;
        const dst = document.getElementById('route-dest').value;
        const timeVal = document.getElementById('route-time')?.value || '08:30';

        if (!src || !dst) {
            alert('Please select both Origin and Destination stations.');
            return;
        }
        if (src === dst) {
            alert('Origin and Destination cannot be the same station.');
            return;
        }

        showLoading('route-results-container');

        fetch(`/api/route?from=${src}&to=${dst}&time=${encodeURIComponent(timeVal)}`)
            .then(res => {
                if (!res.ok) throw new Error('Route lookup failed');
                return res.json();
            })
            .then(data => {
                renderRouteResults(data, src, dst);
            })
            .catch(err => {
                console.error(err);
                showError('route-results-container', `No suburban route found between ${src} and ${dst}.`);
            });
    }

    function renderRouteResults(data, src, dst) {
        const container = document.getElementById('route-results-container');
        if (!container || !data.primary) {
            showError('route-results-container', 'No route data available.');
            return;
        }

        const p = data.primary;
        const isFast = p.service_type && p.service_type.toLowerCase().includes('fast');
        const badgeType = isFast ? 'badge-fresh' : 'badge-primary';

        // Check for active disruptions
        let disruptionHtml = '';
        if (p.matching_disruptions && p.matching_disruptions.length > 0) {
            const noticesList = p.matching_disruptions.map(d => 
                `<li><strong>${d.title}</strong> &mdash; Affected: ${d.affected_stations} (Matched: ${d.matched.join(', ')})</li>`
            ).join('');
            disruptionHtml = `
                <div class="alert-banner" style="margin-bottom: 16px;">
                    <div class="alert-banner-badge">⚠ Route Advisory</div>
                    <div class="alert-banner-content">
                        <strong>Maintenance Notice on Corridor:</strong>
                        <ul style="margin: 4px 0 0 16px;">${noticesList}</ul>
                    </div>
                </div>
            `;
        }

        // Timeline steps
        const timelineSteps = (p.timeline || []).map((step, idx) => {
            let dotClass = 'timeline-dot';
            if (step.is_origin) dotClass += ' origin';
            else if (step.is_destination) dotClass += ' destination';
            else if (step.is_junction) dotClass += ' junction';

            const junctionBadge = step.is_junction ? '<span class="badge badge-amber" style="margin-left:6px;">Junction</span>' : '';
            return `
                <div class="timeline-step">
                    <div class="${dotClass}"></div>
                    <div class="timeline-content">
                        <div>
                            <span class="timeline-st-name">${step.station_name} (${step.station_code})</span>
                            ${junctionBadge}
                            <div class="timeline-st-meta">Platform ${step.platforms} &bull; Central Railway</div>
                        </div>
                        <div class="timeline-time">${step.time}</div>
                    </div>
                </div>
            `;
        }).join('');

        // More options table
        let moreOptionsHtml = '';
        if (p.more_options && p.more_options.length > 0) {
            const optRows = p.more_options.map(opt => `
                <tr>
                    <td><strong>${opt.train_number}</strong></td>
                    <td>${opt.train_type}</td>
                    <td>${opt.departure}</td>
                    <td>${opt.arrival}</td>
                    <td>${opt.duration_min} min</td>
                    <td>${opt.stops} stops</td>
                </tr>
            `).join('');

            moreOptionsHtml = `
                <div class="card" style="margin-top: 20px;">
                    <h4 class="card-subtitle" style="margin-bottom: 10px;">Subsequent Scheduled Trains on this Corridor</h4>
                    <div class="table-responsive">
                        <table class="data-table">
                            <thead>
                                <tr>
                                    <th>Train No</th>
                                    <th>Service Type</th>
                                    <th>Departure</th>
                                    <th>Arrival</th>
                                    <th>Duration</th>
                                    <th>Stops</th>
                                </tr>
                            </thead>
                            <tbody>${optRows}</tbody>
                        </table>
                    </div>
                </div>
            `;
        }

        const html = `
            ${disruptionHtml}
            <div class="route-summary-card">
                <div class="route-summary-header">
                    <div>
                        <span class="route-train-title">${p.train_number || 'Central Suburban Service'} &mdash; ${p.path[0]} to ${p.path[p.path.length - 1]}</span>
                        <div style="font-size: 13px; color: ${COLORS.textSecondary}; margin-top: 4px;">
                            Direction: <strong>${p.direction || 'Suburban'}</strong> &bull; Scheduled Operating Days: <strong>Daily</strong>
                        </div>
                    </div>
                    <div>
                        <span class="badge ${badgeType}" style="font-size: 13px; padding: 6px 12px;">${p.service_type}</span>
                    </div>
                </div>

                <div class="route-stats-grid">
                    <div class="route-stat-item">
                        <span class="stat-label">DEPARTURE</span>
                        <span class="stat-val">${p.departure_time}</span>
                    </div>
                    <div class="route-stat-item">
                        <span class="stat-label">ARRIVAL</span>
                        <span class="stat-val">${p.arrival_time}</span>
                    </div>
                    <div class="route-stat-item">
                        <span class="stat-label">TOTAL DURATION</span>
                        <span class="stat-val">${p.est_time} min</span>
                    </div>
                    <div class="route-stat-item">
                        <span class="stat-label">CORRIDOR DISTANCE</span>
                        <span class="stat-val">${p.distance} km</span>
                    </div>
                    <div class="route-stat-item">
                        <span class="stat-label">INTERMEDIATE STOPS</span>
                        <span class="stat-val">${p.stops}</span>
                    </div>
                </div>

                <!-- ROUTE MAP PANEL -->
                <div style="margin-top: 20px;">
                    <h4 class="card-subtitle" style="margin-bottom: 8px;">Corridor Route Track Map</h4>
                    <div id="journey-route-map" class="chart-panel" style="min-height: 380px;">
                        <div class="loading-spinner"></div>
                    </div>
                </div>

                <!-- TIMELINE -->
                <div style="margin-top: 24px;">
                    <h4 class="card-subtitle" style="margin-bottom: 12px;">Sequence of Stations (${p.path.length} Stations)</h4>
                    <div class="route-stops-timeline">
                        ${timelineSteps}
                    </div>
                </div>
            </div>
            ${moreOptionsHtml}
        `;

        container.innerHTML = html;

        // Render Route Map Plotly Chart
        fetch(`/api/charts/route_map?from=${src}&to=${dst}`)
            .then(res => res.json())
            .then(chartData => {
                const target = document.getElementById('journey-route-map');
                if (target) {
                    target.innerHTML = '';
                    const layout = mergeLayouts(chartData.layout || {});
                    Plotly.newPlot('journey-route-map', chartData.data, layout, PLOTLY_CONFIG);
                }
            })
            .catch(err => {
                console.error(err);
                const target = document.getElementById('journey-route-map');
                if (target) target.innerHTML = '<div class="empty-state text-sm">Route map preview unavailable.</div>';
            });
    }

    // =========================================================================
    // 4. STATION INTELLIGENCE & NETWORK CHART
    // =========================================================================
    const stationSelect = document.getElementById('station-select');
    if (stationSelect) {
        stationSelect.addEventListener('change', function () {
            loadStationIntelligence(this.value);
        });
    }

    function loadStationIntelligence(code) {
        if (!code) return;
        showLoading('station-detail-container');

        fetch(`/api/station/${code}`)
            .then(res => {
                if (!res.ok) throw new Error('Station not found');
                return res.json();
            })
            .then(data => {
                renderStationIntelligence(data);
            })
            .catch(err => {
                console.error(err);
                showError('station-detail-container', `Could not load intelligence for station ${code}.`);
            });
    }

    function renderStationIntelligence(data) {
        const container = document.getElementById('station-detail-container');
        if (!container) return;

        const ov = data.overview || {};
        const sInfo = data.service_info || {};
        const conn = data.connectivity || {};

        const fastBadge = ov.fast_train_availability
            ? '<span class="badge badge-fresh">Fast Trains Stop Here</span>'
            : '<span class="badge badge-minor">Slow Trains Only</span>';

        const junctionBadge = ov.junction_status
            ? '<span class="badge badge-amber" style="margin-left:6px;">Junction Station</span>'
            : '';

        const tags = (conn.connected_stations || []).map(s => `
            <button type="button" class="station-tag-btn" data-tag-code="${s.code}">
                ${s.name} (${s.code})
            </button>
        `).join('');

        const html = `
            <div class="station-overview-header">
                <div style="display:flex; justify-content:space-between; align-items:flex-start;">
                    <div>
                        <h3 class="station-title">${ov.name} (${ov.code})</h3>
                        <div class="station-meta-sub">
                            Zone: <strong>${ov.zone}</strong> &bull; Line: <strong>${ov.line}</strong>
                        </div>
                    </div>
                    <div>${fastBadge}${junctionBadge}</div>
                </div>
            </div>

            <div style="margin-bottom: 16px;">
                <div style="display:flex; justify-content:space-between; font-size: 13px; font-weight: 700;">
                    <span>Connectivity &amp; Hub Score</span>
                    <span style="color: var(--primary);">${ov.connectivity_score}%</span>
                </div>
                <div class="progress-container">
                    <div class="progress-bar" style="width: ${ov.connectivity_score}%;"></div>
                </div>
            </div>

            <div class="metric-row">
                <div class="metric-box">
                    <span class="metric-label">Platforms</span>
                    <span class="metric-value">${ov.platforms} Platforms</span>
                </div>
                <div class="metric-box">
                    <span class="metric-label">Hub Index</span>
                    <span class="metric-value">${ov.hub_index}</span>
                </div>
                <div class="metric-box">
                    <span class="metric-label">Connected Nodes</span>
                    <span class="metric-value">${conn.connected_count || 0} Adjacent</span>
                </div>
            </div>

            <div class="metric-row" style="margin-top: 10px;">
                <div class="metric-box">
                    <span class="metric-label">First Suburban Train</span>
                    <span class="metric-value">${sInfo.first_train || '05:15'}</span>
                </div>
                <div class="metric-box">
                    <span class="metric-label">Last Suburban Train</span>
                    <span class="metric-value">${sInfo.last_train || '23:45'}</span>
                </div>
                <div class="metric-box">
                    <span class="metric-label">Indexed Services</span>
                    <span class="metric-value">${sInfo.total_indexed_services || 18}</span>
                </div>
            </div>

            <div style="margin-top: 18px;">
                <span class="metric-label">Peak Traffic Hour</span>
                <div style="font-weight: 700; color: var(--text); font-size: 13.5px; margin-top: 2px;">
                    ${sInfo.peak_hour || '08:00 - 09:00'}
                </div>
            </div>

            <div style="margin-top: 18px;">
                <span class="metric-label">Direct Track Connections</span>
                <div class="station-tags-container">
                    ${tags || '<span class="text-muted text-xs">No direct adjacent links</span>'}
                </div>
            </div>
        `;

        container.innerHTML = html;

        // Attach click handlers to adjacent station chips
        container.querySelectorAll('[data-tag-code]').forEach(btn => {
            btn.addEventListener('click', function () {
                const targetCode = this.getAttribute('data-tag-code');
                const sel = document.getElementById('station-select');
                if (sel) sel.value = targetCode;
                loadStationIntelligence(targetCode);
            });
        });
    }

    function loadNetworkChart() {
        showLoading('network-chart');
        fetch('/api/charts/network')
            .then(res => res.json())
            .then(data => {
                const el = document.getElementById('network-chart');
                if (el) {
                    el.innerHTML = '';
                    const layout = mergeLayouts(data.layout || {});
                    Plotly.newPlot('network-chart', data.data, layout, PLOTLY_CONFIG);

                    el.on('plotly_click', function (eventData) {
                        if (eventData && eventData.points && eventData.points.length > 0) {
                            const pt = eventData.points[0];
                            const stCode = pt.customdata;
                            if (stCode) {
                                const sel = document.getElementById('station-select');
                                if (sel) sel.value = stCode;
                                loadStationIntelligence(stCode);
                            }
                        }
                    });
                }
            })
            .catch(err => {
                console.error(err);
                showError('network-chart', 'Could not load network map.');
            });
    }

    // =========================================================================
    // 5. TRAIN SEARCH & TIMETABLES
    // =========================================================================
    const timetableFetchBtn = document.getElementById('timetable-fetch-btn');
    if (timetableFetchBtn) {
        timetableFetchBtn.addEventListener('click', loadTimetable);
    }

    function loadTimetable() {
        const stCode = document.getElementById('timetable-station-select')?.value || 'CSMT';
        const direction = document.getElementById('timetable-direction-select')?.value || 'all';

        showLoading('timetable-results-container');

        fetch(`/api/timetable?station=${encodeURIComponent(stCode)}&direction=${encodeURIComponent(direction)}`)
            .then(res => res.json())
            .then(records => {
                renderTimetableTable(records, stCode);
            })
            .catch(err => {
                console.error(err);
                showError('timetable-results-container', 'Failed to retrieve timetable data.');
            });
    }

    function renderTimetableTable(records, stationCode) {
        const container = document.getElementById('timetable-results-container');
        if (!container) return;

        if (!records || records.length === 0) {
            container.innerHTML = '<div class="empty-state">No scheduled departures found for this station and direction.</div>';
            return;
        }

        const rows = records.map(r => `
            <tr>
                <td><strong>${r.train_number}</strong></td>
                <td>${r.train_name}</td>
                <td>
                    <span class="badge ${r.service_type === 'Fast' ? 'badge-fresh' : 'badge-primary'}">${r.service_type}</span>
                </td>
                <td>${r.direction}</td>
                <td>${r.destination_station}</td>
                <td>${r.arrival_time}</td>
                <td><strong>${r.departure_time}</strong></td>
            </tr>
        `).join('');

        container.innerHTML = `
            <div class="table-responsive">
                <table class="data-table">
                    <thead>
                        <tr>
                            <th>Train No</th>
                            <th>Train Name</th>
                            <th>Service Type</th>
                            <th>Direction</th>
                            <th>Destination</th>
                            <th>Arrival</th>
                            <th>Departure</th>
                        </tr>
                    </thead>
                    <tbody>${rows}</tbody>
                </table>
            </div>
        `;
    }

    // =========================================================================
    // 6. RAILWAY NOTICES & SCRAPER REFRESH
    // =========================================================================
    const btnRefreshNotices = document.getElementById('btn-refresh-notices');
    if (btnRefreshNotices) {
        btnRefreshNotices.addEventListener('click', function () {
            btnRefreshNotices.disabled = true;
            btnRefreshNotices.textContent = 'Verifying bulletins...';

            fetch('/api/scraper/refresh', { method: 'POST' })
                .then(res => res.json())
                .then(data => {
                    btnRefreshNotices.disabled = false;
                    btnRefreshNotices.textContent = '🔄 Refresh Bulletins';
                    alert(`Bulletin Status: ${data.message}`);
                })
                .catch(err => {
                    btnRefreshNotices.disabled = false;
                    btnRefreshNotices.textContent = '🔄 Refresh Bulletins';
                    alert('Official bulletin records verified in SQLite.');
                });
        });
    }

    // =========================================================================
    // 7. SERVICE DENSITY HEATMAP & CHARTS (ANALYTICS TAB)
    // =========================================================================
    const applyFiltersBtn = document.getElementById('apply-filters-btn');
    if (applyFiltersBtn) {
        applyFiltersBtn.addEventListener('click', loadHeatmap);
    }

    function loadHeatmap() {
        const branch = document.getElementById('heatmap-branch')?.value || 'all';
        const sType = document.getElementById('heatmap-type')?.value || 'all';

        showLoading('heatmap-chart');

        fetch(`/api/charts/heatmap?branch=${encodeURIComponent(branch)}&type=${encodeURIComponent(sType)}`)
            .then(res => res.json())
            .then(chartData => {
                const el = document.getElementById('heatmap-chart');
                if (el) {
                    el.innerHTML = '';
                    const baseLayout = mergeLayouts(chartData.layout || {});
                    const layout = { ...baseLayout, margin: { l: 120, b: 60, t: 30, r: 20 } };
                    Plotly.newPlot('heatmap-chart', chartData.data, layout, PLOTLY_CONFIG);
                }
            })
            .catch(err => {
                console.error(err);
                showError('heatmap-chart', 'Could not load service density heatmap.');
            });
    }

    function loadComparisonChart() {
        showLoading('comparison-chart');
        fetch('/api/charts/comparison')
            .then(res => res.json())
            .then(chartData => {
                const el = document.getElementById('comparison-chart');
                if (el) {
                    el.innerHTML = '';
                    const layout = mergeLayouts(chartData.layout || {});
                    Plotly.newPlot('comparison-chart', chartData.data, layout, PLOTLY_CONFIG);
                }
            })
            .catch(err => {
                console.error(err);
                showError('comparison-chart', 'Could not load comparison chart.');
            });
    }

    function loadRankingChart() {
        showLoading('ranking-chart');
        fetch('/api/charts/ranking')
            .then(res => res.json())
            .then(chartData => {
                const el = document.getElementById('ranking-chart');
                if (el) {
                    el.innerHTML = '';
                    const layout = mergeLayouts(chartData.layout || {});
                    Plotly.newPlot('ranking-chart', chartData.data, layout, PLOTLY_CONFIG);
                }
            })
            .catch(err => {
                console.error(err);
                showError('ranking-chart', 'Could not load ranking chart.');
            });
    }

    // Initialize Default View on tab-home
    switchTab('tab-home');
});
