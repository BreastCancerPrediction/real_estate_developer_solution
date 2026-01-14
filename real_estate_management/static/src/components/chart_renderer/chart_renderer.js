/** @odoo-module */

import { registry } from "@web/core/registry"
import { loadJS } from "@web/core/assets"
const { Component, onWillStart, useRef, onMounted } = owl

export class ChartRenderer extends Component {
    setup(){
        this.chartRef = useRef("chart")
        
        // Load Chart.js dynamically
        onWillStart(async () => {
            await loadJS("https://cdnjs.cloudflare.com/ajax/libs/Chart.js/4.4.0/chart.umd.min.js")
        })

        onMounted(() => this.renderChart())
    }

    renderChart(){
        const { data } = this.props;  // Expecting this.props.data to be an object with counts of units by status

        // Prepare dynamic labels (statuses) and data (counts) from props
        const labels = Object.keys(data);  // Extract the status keys (e.g., 'vacant', 'assign', etc.)
        const datasetValues = Object.values(data);  // Extract the count values for each status

        console.log("labels===>",labels)
        console.log("datasetValues===>",datasetValues)
        // Render the chart with dynamic data
        new Chart(this.chartRef.el, {
            type: this.props.type,  // Bar chart type (can be changed to other types like 'line')
            data: {
                labels: labels,  // Dynamic labels from the statuses
                datasets: [{
                    label:this.props.title ,
                    data: datasetValues,  // Dynamic count values for each status
                    // backgroundColor: 'rgba(54, 162, 235, 0.2)',  // Optional background color for the bars
                    // borderColor: 'rgba(54, 162, 235, 1)',  // Optional border color for the bars
                    borderWidth: 1
                }]
            },
            options: {
                responsive: true,
                plugins: {
                    legend: {
                        position: 'bottom',
                    },
                    title: {
                        display: true,
                        text: this.props.title,
                        position: 'top',
                    }
                }
            },
        });
    }
}

ChartRenderer.template = "owl.ChartRenderer"












































// /** @odoo-module */

// import { registry } from "@web/core/registry"
// import { loadJS } from "@web/core/assets"
// const { Component, onWillStart, useRef, onMounted } = owl

// export class ChartRenderer extends Component {
//     setup(){
//         this.chartRef = useRef("chart")
//         onWillStart(async ()=>{
//             await loadJS("https://cdnjs.cloudflare.com/ajax/libs/Chart.js/4.4.0/chart.umd.min.js")
//         })

//         onMounted(()=>this.renderChart())
//     }

//     renderChart(){
//         new Chart(this.chartRef.el,
//         {
//           type: this.props.type,
//           data: {
//             labels: [
//                 'Red',
//                 'Blue',
//                 'Yellow'
//               ],
//               datasets: [
//               {
//                 label: 'My First Dataset',
//                 data: [300, 50, 100],
//                 hoverOffset: 4
//               },{
//                 label: 'My Second Dataset',
//                 data: [100, 70, 150],
//                 hoverOffset: 4
//               }]
//           },
//           options: {
//             responsive: true,
//             plugins: {
//               legend: {
//                 position: 'bottom',
//               },
//               title: {
//                 display: true,
//                 text: this.props.title,
//                 position: 'bottom',
//               }
//             }
//           },
//         }
//       );
//     }
// }

// ChartRenderer.template = "owl.ChartRenderer"