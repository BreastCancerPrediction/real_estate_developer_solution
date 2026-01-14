/** @odoo-module **/
import { registry } from "@web/core/registry";
import { Component ,useState,onMounted } from "@odoo/owl";
import { useService } from "@web/core/utils/hooks";
const actionRegistry = registry.category("actions");
class DlpDashboard extends Component {
setup() {
        super.setup();
        this.orm = this.env.services.orm;
         // Chart instances
         this.currentFilter = null;
        this.pieChart = null;
        this.statusChart = null;
        this.priorityChart = null;
        this.resolutionChart = null;
        this._fetch_data();
        this._addArrowClickHandler();


    }

    async _fetch_data(filter_by = null) {
        this.currentFilter = filter_by;
        const args = [];
        const kwargs = filter_by ? { filter_by } : {};

        let result = await this.orm.call("helpdesk.ticket", "get_tiles_data", args, kwargs);

        document.getElementById('all_workorders').innerHTML = `<span>${result.all_workorder_count}</span>`;
        document.getElementById('service_appointments').innerHTML = `<span>${result.service_appointment_count}</span>`;
        document.getElementById('dlp_cases').innerHTML = `<span>${result.dlp_case_count}</span>`;

        this._renderPieChart(result);
        this._renderStatusChart({
            stage_labels: result.stage_labels,
            stage_counts: result.stage_counts
        });

//        const priorityData = await this.orm.call('helpdesk.ticket', 'read_group', [[], ['priority'], ['priority']]);
//        this._renderPriorityBarChart(priorityData);

        this._renderPriorityBarChart({
            labels: result.priority_labels,
            counts: result.priority_counts
        });


        this._renderResolutionLineChart({
            labels: result.typology_labels,
            counts: result.typology_counts
        });
    }
    onChangeFilter(ev) {
        const selected = ev.target.value;
        this._fetch_data(selected);
    }

_addArrowClickHandler() {
    setTimeout(() => {
        const arrows = document.querySelectorAll('.chart-arrow');
        arrows.forEach(arrow => {
            arrow.addEventListener('click', () => {
                this._onChartArrowClick(arrow.dataset.chart);
            });
        });
    }, 100);
}

_onChartArrowClick(chartType) {
    let domain = [];
    let name = "";

    if (chartType === "work_order_status") {
        name = "Work Orders by Status";
        const labels = this.statusChart.data.labels;  // existing chart labels
        console.log(labels,"<<<<<<<<<<<<<<<<<<<<<<<<<<")
        domain = [['stage_id.name', 'in', labels]];
    }
//    else if (chartType === "dlp_summary") {
//        name = "DLP Tickets Summary";
//
//        // Assuming you have this.dlpSummaryChart and its labels or data
//        const labels = this.dlpSummaryChart.data.labels;  // get labels from DLP summary chart
//        console.log(labels,"DLP Tickets Summary..........................")
//        // Example: filter tickets by 'dlp_stage' or a field related to DLP summary stages
//        // Replace 'dlp_stage' with the correct field on 'helpdesk.ticket' that matches labels
//        domain = [['dlp_stage', 'in', labels]];
//        console.log(domain,"====================================")
//    }

    // Date filtering logic (unchanged)
    const today = new Date();
    let startDate = null;
    let endDate = null;
    const filter = this.currentFilter;

    if (filter === 'this_week') {
        const day = today.getDay();
        const diffToMonday = (day === 0 ? -6 : 1 - day);
        startDate = new Date(today);
        startDate.setDate(today.getDate() + diffToMonday);
        endDate = new Date(startDate);
        endDate.setDate(startDate.getDate() + 6);
    }else if (filter === 'last_week') {
         const day = today.getDay();
         // Calculate last week's Monday
         const diffToLastMonday = (day === 0 ? -13 : 1 - day - 7);
         startDate = new Date(today);
         startDate.setDate(today.getDate() + diffToLastMonday);
         // Last week's Sunday
         endDate = new Date(startDate);
         endDate.setDate(startDate.getDate() + 6);
    }else if (filter === 'this_month') {
        startDate = new Date(today.getFullYear(), today.getMonth(), 1);
        endDate = new Date(today.getFullYear(), today.getMonth() + 1, 0);
    }

    if (startDate && endDate) {
        const toOdooDate = (d) => d.toISOString().split('T')[0];
        domain.push(['create_date', '>=', toOdooDate(startDate)]);
        domain.push(['create_date', '<=', toOdooDate(endDate)]);
    }

    this.env.services.action.doAction({
        type: 'ir.actions.act_window',
        name: name,
        res_model: 'helpdesk.ticket',
        view_mode: 'tree,form',
        views: [[false, 'list'], [false, 'form']],
        domain: domain,
        target: 'current',
    });
}

onTileClick(ev) {
    const tileType = ev.currentTarget.dataset.type;
    let domain = [];
    let resModel = '';
    let name = '';
    const filter = this.currentFilter;

    // Compute date domain based on filter
    const today = new Date();
    let startDate = null;
    let endDate = null;

    if (filter === 'this_week') {
        const day = today.getDay(); // 0=Sunday, 1=Monday...
        const diffToMonday = (day === 0 ? -6 : 1 - day);
        startDate = new Date(today);
        startDate.setDate(today.getDate() + diffToMonday);
        endDate = new Date(startDate);
        endDate.setDate(startDate.getDate() + 6);
    } else if (filter === 'last_week') {
        const day = today.getDay();
        const diffToLastSunday = (day === 0 ? -7 : -day);
        endDate = new Date(today);
        endDate.setDate(today.getDate() + diffToLastSunday);
        startDate = new Date(endDate);
        startDate.setDate(endDate.getDate() - 6);
    } else if (filter === 'this_month') {
        startDate = new Date(today.getFullYear(), today.getMonth(), 1);
        endDate = new Date(today.getFullYear(), today.getMonth() + 1, 0);
    }

    // Convert to Odoo-compatible date strings
    const toOdooDate = (d) => d.toISOString().split('T')[0];

    if (startDate && endDate) {
        domain = [['create_date', '>=', toOdooDate(startDate)], ['create_date', '<=', toOdooDate(endDate)]];
    }

    if (tileType === 'service_appointments') {
        resModel = 'appointment.type';
        name = 'Service Appointments';
    } else if (tileType === 'dlp_cases') {
        resModel = 'dlp.case';
        name = 'DLP Cases';
    } else if (tileType === 'all_workorders') {
        resModel = 'helpdesk.ticket';
        name = 'All WorkOrders';
    }

    this.env.services.action.doAction({
        type: 'ir.actions.act_window',
        name: name,
        res_model: resModel,
        view_mode: 'list,form',
        views: [
            [false, 'list'],
            [false, 'form'],
        ],
        domain: domain,
        target: 'current',
    });
}



     _renderPieChart(data) {
         const renderChart = () => {
             const ctx = document.getElementById('workorderPieChart').getContext('2d');

             // Destroy previous instance if exists
             if (this.pieChart) {
                 this.pieChart.destroy();
             }

             this.pieChart = new Chart(ctx, {
                 type: 'pie',
                 data: {
                     labels: ['All WorkOrders', 'Service Appointments', 'DLP Cases'],
                     datasets: [{
                         data: [
                             data.all_workorder_count,
                             data.service_appointment_count,
                             data.dlp_case_count
                         ],
                         backgroundColor: ['#F4A261','#E96175',  '#43C5B1'],
                         borderWidth: 1
                     }]
                 },
                 options: {
                     responsive: true,
                     plugins: {
                         legend: { position: 'bottom' },
                         tooltip: { enabled: true }
                     }
                 }
             });
         };

         if (typeof Chart === 'undefined') {
             const script = document.createElement('script');
             script.src = "https://cdn.jsdelivr.net/npm/chart.js";
             script.onload = renderChart;
             document.head.appendChild(script);
         } else {
             renderChart();
         }
     }

        _renderStatusChart(stageData) {
            const renderStatus = () => {
                const ctx = document.getElementById('workOrderStatusChart').getContext('2d');
                 // Destroy previous instance if exists
                 if (this.statusChart) {
                     this.statusChart.destroy();
                 }
                this.statusChart = new Chart(ctx, {
                    type: 'doughnut',
                    data: {
                        labels: stageData.stage_labels,
                        datasets: [{
                            data: stageData.stage_counts,
                            backgroundColor: ['#F4A261','#E96175',  '#43C5B1', '#4EA7F2', '#9b59b6', '#1abc9c'],
                            borderWidth: 1
                        }]
                    },
                    options: {
                        responsive: true,
                        plugins: {
                            legend: { position: 'bottom' },
                            tooltip: { enabled: true }
                        }
                    }
                });
            };

            if (typeof Chart === 'undefined') {
                const script = document.createElement('script');
                script.src = "https://cdn.jsdelivr.net/npm/chart.js";
                script.onload = renderStatus;
                document.head.appendChild(script);
            } else {
                renderStatus();
            }
        }

    _renderPriorityBarChart(data) {
        const renderBar = () => {
            if (this.priorityChart) {
                this.priorityChart.destroy();
            }

            const ctx = document.getElementById('priorityBarChart')?.getContext('2d');
            if (!ctx) return;

            this.priorityChart = new Chart(ctx, {
                type: 'bar',
                data: {
                    labels: data.labels,
                    datasets: [{
                        label: 'Number of WorkOrders',
                        data: data.counts,
                        backgroundColor: [
                            'rgba(75, 192, 192, 0.7)',
                            'rgba(255, 206, 86, 0.7)',
                            'rgba(255, 99, 132, 0.7)',
                            'rgba(153, 102, 255, 0.7)',
                        ],
                        borderColor: [
                            'rgba(75, 192, 192, 1)',
                            'rgba(255, 206, 86, 1)',
                            'rgba(255, 99, 132, 1)',
                            'rgba(153, 102, 255, 1)',
                        ],
                        borderWidth: 1,
                        borderRadius: 5,
                    }]
                },
                options: {
                    maintainAspectRatio: false,
                    scales: {
                        y: { beginAtZero: true,
                         ticks: {
                             callback: function(value) {
                                 // Only show tick if it's an integer
                                 return Number.isInteger(value) ? value : null;
                             },

                                        font: {
                                            family: "'Courier New', monospace",
                                            size: 13,
                                            weight: '600',
                                            style: 'normal',
                                        },
                                        color: '#555',
                                    },
                                    grid: {
                                        color: '#eee',
                                    }
                         },
                        x: { grid: { display: false },
                         ticks: {

                                        font: {
                                            family: "'Segoe UI', Tahoma, Geneva, Verdana, sans-serif",
                                            size: 14,
                                            lineHeight: 1.5
                                        },
                                        color: '#333',
                                        }
                         }
                    },
                    plugins: {
                        legend: { display: false }
                    }
                }
            });
        };

        if (typeof Chart === 'undefined') {
            const script = document.createElement('script');
            script.src = "https://cdn.jsdelivr.net/npm/chart.js";
            script.onload = renderBar;
            document.head.appendChild(script);
        } else {
            renderBar();
        }
    }


        _renderResolutionLineChart(data) {
            const renderChart = () => {
                const ctx = document.getElementById('resolutionLineChart')?.getContext('2d');
                if (!ctx) return;
                // Destroy previous instance if exists
                 if (this.resolutionChart) {
                     this.resolutionChart.destroy();
                 }

                this.resolutionChart = new Chart(ctx, {
                    type: 'line',
                    data: {
                        labels: data.labels,
                        datasets: [{
                            label: 'Resolution Typology Count',
                            data: data.counts,
                            borderColor: '#3498db',
                            backgroundColor: 'rgba(52, 152, 219, 0.2)',
                            borderWidth: 2,
                            fill: true,
                            tension: 0.4,
                            pointBackgroundColor: '#3498db',
                            pointBorderColor: '#fff',
                            pointRadius: 5
                        }]
                    },
                    options: {
                        responsive: true,
                        maintainAspectRatio: false,
                        plugins: {
                            legend: { display: true },
                            tooltip: { enabled: true }
                        },
                        scales: {
                            y: {
                                beginAtZero: true,
                                ticks: { stepSize: 1 }
                            }
                        }
                    }
                });
            };

            if (typeof Chart === 'undefined') {
                const script = document.createElement('script');
                script.src = "https://cdn.jsdelivr.net/npm/chart.js";
                script.onload = renderChart;
                document.head.appendChild(script);
            } else {
                renderChart();
            }
        }


}
DlpDashboard.template = "dlp_process.DlpDashboard";
// Register the component with the action tag
actionRegistry.add("dlp_dashboard_tag", DlpDashboard);

