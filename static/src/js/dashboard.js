/** @odoo-module **/

import { Component, onWillStart, useState, useRef, useEffect } from "@odoo/owl";
import { registry } from "@web/core/registry";
import { useService } from "@web/core/utils/hooks";
import { rpc } from "@web/core/network/rpc";
import { loadBundle } from "@web/core/assets";

class ItParcDashboard extends Component {
    static template = "it_parc.Dashboard";
    static props = {};

    setup() {
        this.action = useService("action");
        this.chartCategoriesRef = useRef("chartCategories");
        this.chartInterventionsRef = useRef("chartInterventions");

        this.state = useState({
            loaded: false,
            kpis: {},
            graphiques: {},
            error: null,
        });

        onWillStart(async () => {
            await this._loadData();
            await loadBundle("web.chartjs_lib");
        });

        useEffect(() => {
            if (this.state.loaded && !this.state.error) {
                this._renderCharts();
            }
            return () => {
                this._destroyCharts();
            };
        });
    }

    async _loadData() {
        try {
            const data = await rpc("/it_parc/dashboard/data");
            this.state.kpis = data.kpis;
            this.state.graphiques = data.graphiques;
            this.state.loaded = true;
        } catch (e) {
            this.state.error = e.message || e.toString();
            this.state.loaded = true;
        }
    }

    get formattedCoutTotalMaintenance() {
        const cout = this.state.kpis?.cout_total_maintenance || 0;
        return Math.round(cout).toLocaleString();
    }

    _renderCharts() {
        // Graphique catégories
        const ctxCat = this.chartCategoriesRef.el;
        if (ctxCat && window.Chart) {
            if (this.chartCat) {
                this.chartCat.destroy();
            }
            this.chartCat = new window.Chart(ctxCat, {
                type: 'doughnut',
                data: {
                    labels: this.state.graphiques.categories?.labels || [],
                    datasets: [{
                        data: this.state.graphiques.categories?.data || [],
                        backgroundColor: [
                            '#1a3c5e', '#2e6da4',
                            '#c9a84c', '#4caf50',
                            '#f44336', '#9e9e9e'
                        ],
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        legend: { position: 'right' },
                        title: {
                            display: true,
                            text: 'Équipements par catégorie'
                        }
                    }
                }
            });
        }

        // Graphique interventions
        const ctxInter = this.chartInterventionsRef.el;
        if (ctxInter && window.Chart) {
            if (this.chartInter) {
                this.chartInter.destroy();
            }
            this.chartInter = new window.Chart(ctxInter, {
                type: 'bar',
                data: {
                    labels: this.state.graphiques.interventions?.labels || [],
                    datasets: [{
                        label: 'Interventions',
                        data: this.state.graphiques.interventions?.data || [],
                        backgroundColor: '#1a3c5e',
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        title: {
                            display: true,
                            text: 'Interventions par mois'
                        }
                    }
                }
            });
        }
    }

    _destroyCharts() {
        if (this.chartCat) {
            this.chartCat.destroy();
            this.chartCat = null;
        }
        if (this.chartInter) {
            this.chartInter.destroy();
            this.chartInter = null;
        }
    }

    goToEquipements() {
        this.action.doAction('it_parc.action_it_equipement');
    }

    goToAlertes() {
        this.action.doAction('it_parc.action_it_alerte');
    }

    goToContrats() {
        this.action.doAction('it_parc.action_it_contrat');
    }

    goToInterventions() {
        this.action.doAction('it_parc.action_it_intervention');
    }

    scrollToTop() {
        const container = document.querySelector('.o_it_parc_dashboard');
        if (container) {
            container.scrollTo({ top: 0, behavior: 'smooth' });
        }
    }

    scrollToBottom() {
        const container = document.querySelector('.o_it_parc_dashboard');
        if (container) {
            container.scrollTo({ top: container.scrollHeight, behavior: 'smooth' });
        }
    }
}

registry.category("actions").add(
    "it_parc_dashboard", ItParcDashboard
);
