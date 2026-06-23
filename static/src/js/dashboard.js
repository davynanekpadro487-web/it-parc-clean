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
                            '#1a73e8', // Google Blue
                            '#34a853', // Google Green
                            '#fbbc05', // Google Yellow
                            '#ea4335', // Google Red
                            '#8ab4f8', // Light Google Blue
                            '#a8dab5'  // Light Google Green
                        ],
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        legend: { 
                            position: 'right',
                            labels: {
                                font: {
                                    family: 'Inter, -apple-system, sans-serif',
                                    size: 11
                                }
                            }
                        },
                        title: {
                            display: true,
                            text: 'Équipements par catégorie',
                            font: {
                                family: 'Inter, -apple-system, sans-serif',
                                size: 14,
                                weight: 'bold'
                            },
                            color: '#333333'
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
                        backgroundColor: '#1a73e8',
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        legend: { display: false },
                        title: {
                            display: true,
                            text: 'Interventions par mois',
                            font: {
                                family: 'Inter, -apple-system, sans-serif',
                                size: 14,
                                weight: 'bold'
                            },
                            color: '#333333'
                        }
                    },
                    scales: {
                        x: {
                            grid: { display: false },
                            ticks: {
                                font: {
                                    family: 'Inter, -apple-system, sans-serif',
                                    size: 11
                                }
                            }
                        },
                        y: {
                            grid: { color: '#e5e7eb' },
                            ticks: {
                                font: {
                                    family: 'Inter, -apple-system, sans-serif',
                                    size: 11
                                }
                            }
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

    goToEquipementsAffectes() {
        this.action.doAction({
            type: 'ir.actions.act_window',
            name: 'Équipements (Affectés)',
            res_model: 'it.equipement',
            view_mode: 'list,form',
            views: [[false, 'list'], [false, 'form']],
            domain: [['state', '=', 'affecte']],
        });
    }

    goToEquipementsMaintenance() {
        this.action.doAction({
            type: 'ir.actions.act_window',
            name: 'Équipements (En maintenance)',
            res_model: 'it.equipement',
            view_mode: 'list,form',
            views: [[false, 'list'], [false, 'form']],
            domain: [['state', '=', 'maintenance']],
        });
    }

    goToEquipementsGarantiesCritiques() {
        this.action.doAction({
            type: 'ir.actions.act_window',
            name: 'Équipements (Garantie < 30j)',
            res_model: 'it.equipement',
            view_mode: 'list,form',
            views: [[false, 'list'], [false, 'form']],
            domain: [['jours_garantie_restants', '<', 30]],
        });
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
}

registry.category("actions").add(
    "it_parc_dashboard", ItParcDashboard
);
