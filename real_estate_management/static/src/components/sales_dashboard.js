/** @odoo-module */

import { registry } from "@web/core/registry"
import { KpiCard } from "./kpi_card/kpi_card"
import { ChartRenderer } from "./chart_renderer/chart_renderer"
import { loadJS } from "@web/core/assets"
import { useService } from "@web/core/utils/hooks"
const { Component, onWillStart, useRef, onMounted, useState } = owl



export class OwlSalesDashboard extends Component {
    setup(){
        this.state = useState({
            quotations: {
                value:10,
                percentage:6,
            },
            opportunities: {
                value:10,
                percentage:6,
            },
            vacant_units:{
                value:10,
                percentage:10
            },
            assign_units:{
                value:10,
                percentage:10  
            },
            booked_units:{
                value:10,
                percentage:10      
            },
            occupied_units:{
                value:10,
                percentage:10      
            },
            all_units:{},
            properties:{},
            monthlySales:{},
            yearlySales:{},
            partners:{},
            projects:{},
            period:90,
        })
        this.orm = useService("orm")
        this.actionService = useService("action")

        onWillStart(async ()=>{
            this.getDates()
            await this.getQuotations()
            await this.getOrders()
            await this.getOpportunities()
            await this.getVacantUnits()
            await this.getAssignUnits()
            await this.getBookedUnits()
            await this.getOccupiedUnits()
            await this.getAllUnits()
            await this.getAllProperties()
            await this.getSaleOrdersMonthwise()
            await this.fetchOpportunityCustomers()
            await this.getSaleOrdersYearwise()
            await this.getAllProjects()

        })

    }

    async onChangePeriod(){
        this.getDates()
        await this.getQuotations()
        await this.getOrders()
        await this.getOpportunities()
        await this.getVacantUnits()
        await this.getAssignUnits()
        await this.getBookedUnits()
        await this.getOccupiedUnits()
        await this.getAllUnits()
        await this.getAllProperties()
        await this.getSaleOrdersMonthwise()
        await this.fetchOpportunityCustomers()
        await this.getSaleOrdersYearwise()
        await this.getAllProjects()

    }

    getDates() {
    const { period } = this.state;

    const formatDate = (days) => {
        const date = new Date();
        date.setDate(date.getDate() - days);
        return date.toISOString().split('T')[0];  // Format to 'YYYY-MM-DD'
    };

    this.state.current_date = formatDate(period);
    this.state.previous_date = formatDate(period * 2);
}

    async getQuotations(){
        let domain = [['state', 'in', ['sent', 'draft']]]
        if (this.state.period > 0){
            domain.push(['date_order','>', this.state.current_date])
        }
        const data = await this.orm.searchCount("sale.order", domain)
        this.state.quotations.value = data

        // previous period
        let prev_domain = [['state', 'in', ['sent', 'draft']]]
        if (this.state.period > 0){
            prev_domain.push(['date_order','>', this.state.previous_date], ['date_order','<=', this.state.current_date])
        }
        const prev_data = await this.orm.searchCount("sale.order", prev_domain)
        const percentage = ((data - prev_data)/prev_data) * 100
        this.state.quotations.percentage = percentage.toFixed(2)
    }

    async getAllProjects() {
        try {
            const projects = await this.orm.searchRead(
                'project.project', 
                [],               
                ['id', 'name'],
            );
            const projectOptions = projects.map(project => ({
                id: project.id,
                name: project.name,
            }));
            this.state.projects = projectOptions;
    
            console.log("Projects fetched:", projectOptions);
        } catch (error) {
            console.error("Failed to fetch projects:", error);
        }
    }

    async getSaleOrdersYearwise() {
        const saleOrders = await this.orm.searchRead(
            'sale.order',
            [],
            ['date_order']
        );
    
        const currentYear = new Date().getFullYear();
        const yearsRange = [];
        const startYear = currentYear - 5; 
        for (let year = startYear; year <= currentYear; year++) {
            yearsRange.push(year);
        }
    
        const yearwiseData = {};
        yearsRange.forEach(year => {
            yearwiseData[year] = 0; 
        });
    
        saleOrders.forEach(order => {
            const orderDate = new Date(order.date_order);
            const year = orderDate.getFullYear();
    
            if (yearwiseData[year] !== undefined) {
                yearwiseData[year] += 1; 
            }
        });    
        this.state.yearlySales = yearwiseData;
    }

    async getAllUnits() {
        let domain = [
            ['status', 'in', ['vacant', 'assign', 'booked', 'occupied']],
        ];
        if (this.state.period > 0) {
            domain.push(['create_date', '>', this.state.current_date]);
        }
        const groupByStatus = await this.orm.readGroup(
            'product.template',
            domain, 
            ['status'],
            ['status'],
        );
        const statusCounts = {
            vacant: 0,
            assign: 0,
            booked: 0,
            occupied: 0,
        };
        groupByStatus.forEach(result => {
            console.log("result:", result);
            statusCounts[result.status] = result['status_count'];
        });
        console.log("Units count by status:", statusCounts);
        this.state.all_units = statusCounts;
    }

    // async getAllProperties() {
    //     const allRecords = await this.orm.searchRead(
    //         'property.property',
    //         [],                
    //         ['property_type']
    //     );
    //     console.log("Fetched all records:", allRecords);
    //     if (!allRecords || allRecords.length === 0) {
    //         console.warn("No records found.");
    //         return;
    //     }
    //     const proptypeCounts = allRecords.reduce((acc, record) => {
    //         const type = record.property_type || "Undefined";
    //         acc[type] = (acc[type] || 0) + 1;      
    //         return acc;
    //     }, {});
    //     console.log("Count of each property type:", proptypeCounts);
    //     this.state.properties = proptypeCounts
    //     const labels = Object.keys(proptypeCounts);
    //     const data = Object.values(proptypeCounts);
    //     console.log("Chart Labels:", labels);
    //     console.log("Chart Data:", data);
    // }

    async getAllProperties() {
        const propertyTypeOptions = await this.orm.call(
            'property.property',
            'fields_get',
            ['property_type']
        );
        const selectionMapping = Object.fromEntries(
            propertyTypeOptions.property_type.selection
        );
        const allRecords = await this.orm.searchRead(
            'property.property',
            [],                
            ['property_type']
        );
        if (!allRecords || allRecords.length === 0) {
            console.warn("No records found.");
            return;
        }
        const proptypeCounts = allRecords.reduce((acc, record) => {
            const type = selectionMapping[record.property_type] || "Undefined";
            acc[type] = (acc[type] || 0) + 1;      
            return acc;
        }, {});
        this.state.properties = proptypeCounts;
        const labels = Object.keys(proptypeCounts);
        const data = Object.values(proptypeCounts);
    }
    
    // async getAllPartners() {
    //     const partners = await this.orm.searchRead(
    //         'res.partner',
    //         [],
    //         ['image_128','name', 'email', 'phone', 'function']
    //     );
    //     console.log("partners===>",partners)
    //     this.state.partners = partners;
    // }

    async fetchOpportunityCustomers() {
        const partners = await this.orm.call('crm.lead', 'get_opportunity_customers', [['']]);
        this.state.partners = partners;
    }

    async getSaleOrdersMonthwise() {
        const saleOrders = await this.orm.searchRead(
            'sale.order',
            [],
            ['date_order']
        );
        const monthNames = [
            'January', 'February', 'March', 'April', 'May', 'June',
            'July', 'August', 'September', 'October', 'November', 'December'
        ];
        const allMonths = [];
        const year = new Date().getFullYear();
        for (let month = 0; month < 12; month++) {
            const monthLabel = `${monthNames[month]} ${year}`
            allMonths.push(monthLabel);
        }
        const monthwiseData = {};
        allMonths.forEach(month => {
            monthwiseData[month] = 0;
        });
        saleOrders.forEach(order => {
            const orderDate = new Date(order.date_order);
            const monthIndex = orderDate.getMonth(); 
            const monthLabel = `${monthNames[monthIndex]} ${orderDate.getFullYear()}`;
    
            if (monthwiseData[monthLabel] !== undefined) {
                monthwiseData[monthLabel] += 1; 
            }
        });
        this.state.monthlySales = monthwiseData;
    }
    


    async getOpportunities(){
        let domain = [
            // ['stage_id.name', 'in', ['sent', 'draft']], 
            ['type', '=', 'opportunity'] 
        ];
        if (this.state.period > 0){
            domain.push(['create_date','>', this.state.current_date])
        }
        const data = await this.orm.searchCount("crm.lead", domain)
        console.log("data====>",data)
        this.state.opportunities.value = data

        // previous period
        let prev_domain = [['type', '=', 'opportunity']]
        if (this.state.period > 0){
            prev_domain.push(['create_date','>', this.state.previous_date], ['create_date','<=', this.state.current_date])
        }
        const prev_data = await this.orm.searchCount("crm.lead", prev_domain)
        const percentage = ((data - prev_data)/prev_data) * 100
        this.state.opportunities.percentage = percentage.toFixed(2)
    }

    async getVacantUnits() {
        let domain = [
            ['status', 'in', ['vacant']], 
        ];
        if (this.state.period > 0) {
            domain.push(['create_date', '>', this.state.current_date]);
        }
        console.log("Vacant units domain:", domain);
        const data = await this.orm.searchCount("product.template", domain);
        console.log("units data====>", data);
        this.state.vacant_units.value = data;
        let prev_domain = [
            ['status', 'in', ['vacant']]
        ];
        if (this.state.period > 0) {
            prev_domain.push(['create_date', '>', this.state.previous_date], ['create_date', '<=', this.state.current_date]);
        }
        const prev_data = await this.orm.searchCount("product.template", prev_domain);
        const percentage = prev_data > 0 ? ((data - prev_data) / prev_data) * 100 : 0;
        this.state.vacant_units.percentage = percentage.toFixed(2);
    }

    async getAssignUnits() {
        let domain = [
            ['status', 'in', ['assign']], 
        ];
        if (this.state.period > 0) {
            domain.push(['create_date', '>', this.state.current_date]);
        }
        console.log("assign units domain:", domain);
        const data = await this.orm.searchCount("product.template", domain);
        console.log("assign units data====>", data);
        this.state.assign_units.value = data;
        let prev_domain = [
            ['status', 'in', ['assign']]
        ];
        if (this.state.period > 0) {
            prev_domain.push(['create_date', '>', this.state.previous_date], ['create_date', '<=', this.state.current_date]);
        }
        const prev_data = await this.orm.searchCount("product.template", prev_domain);
        const percentage = prev_data > 0 ? ((data - prev_data) / prev_data) * 100 : 0;
        this.state.assign_units.percentage = percentage.toFixed(2);
    }

    async getBookedUnits() {
        let domain = [
            ['status', 'in', ['booked']], 
        ];
        if (this.state.period > 0) {
            domain.push(['create_date', '>', this.state.current_date]);
        }
        console.log("booked units domain:", domain);
        const data = await this.orm.searchCount("product.template", domain);
        console.log("booked units data====>", data);
        this.state.booked_units.value = data;
        let prev_domain = [
            ['status', 'in', ['booked']]
        ];
        if (this.state.period > 0) {
            prev_domain.push(['create_date', '>', this.state.previous_date], ['create_date', '<=', this.state.current_date]);
        }
        const prev_data = await this.orm.searchCount("product.template", prev_domain);
        const percentage = prev_data > 0 ? ((data - prev_data) / prev_data) * 100 : 0;
        this.state.booked_units.percentage = percentage.toFixed(2);
    }

    async getOccupiedUnits() {
        let domain = [
            ['status', 'in', ['occupied']], 
        ];
        if (this.state.period > 0) {
            domain.push(['create_date', '>', this.state.current_date]);
        }
        console.log("occupied units domain:", domain);
        const data = await this.orm.searchCount("product.template", domain);
        console.log("occupied units data====>", data);
        this.state.occupied_units.value = data;
        let prev_domain = [
            ['status', 'in', ['occupied']]
        ];
        if (this.state.period > 0) {
            prev_domain.push(['create_date', '>', this.state.previous_date], ['create_date', '<=', this.state.current_date]);
        }
        const prev_data = await this.orm.searchCount("product.template", prev_domain);
        const percentage = prev_data > 0 ? ((data - prev_data) / prev_data) * 100 : 0;
        this.state.occupied_units.percentage = percentage.toFixed(2);
    }
    
    async getOrders(){
        let domain = [['state', 'in', ['sale', 'done', 'sold']]]
        if (this.state.period > 0){
            domain.push(['date_order','>', this.state.current_date])
        }
        const data = await this.orm.searchCount("sale.order", domain)
        //this.state.quotations.value = data

        // previous period
        let prev_domain = [['state', 'in', ['sale', 'done']]]
        if (this.state.period > 0){
            prev_domain.push(['date_order','>', this.state.previous_date], ['date_order','<=', this.state.current_date])
        }
        const prev_data = await this.orm.searchCount("sale.order", prev_domain)
        const percentage = ((data - prev_data)/prev_data) * 100
        //this.state.quotations.percentage = percentage.toFixed(2)

        //revenues
        const current_revenue = await this.orm.readGroup("sale.order", domain, ["amount_total:sum"], [])
        const prev_revenue = await this.orm.readGroup("sale.order", prev_domain, ["amount_total:sum"], [])
        const revenue_percentage = ((current_revenue[0].amount_total - prev_revenue[0].amount_total) / prev_revenue[0].amount_total) * 100

        //average
        const current_average = await this.orm.readGroup("sale.order", domain, ["amount_total:avg"], [])
        const prev_average = await this.orm.readGroup("sale.order", prev_domain, ["amount_total:avg"], [])
        const average_percentage = ((current_average[0].amount_total - prev_average[0].amount_total) / prev_average[0].amount_total) * 100

        this.state.orders = {
            value: data,
            percentage: percentage.toFixed(2),
            revenue: `$${(current_revenue[0].amount_total/1000).toFixed(2)}K`,
            revenue_percentage: revenue_percentage.toFixed(2),
            average: `$${(current_average[0].amount_total/1000).toFixed(2)}K`,
            average_percentage: average_percentage.toFixed(2),
        }

        //this.env.services.company
    }

    async viewQuotations(){
        let domain = [['state', 'in', ['sent', 'draft']]]
        if (this.state.period > 0){
            domain.push(['date_order','>', this.state.current_date])
        }

        let list_view = await this.orm.searchRead("ir.model.data", [['name', '=', 'view_quotation_tree_with_onboarding']], ['res_id'])

        this.actionService.doAction({
            type: "ir.actions.act_window",
            name: "Quotations",
            res_model: "sale.order",
            domain,
            views: [
                [list_view.length > 0 ? list_view[0].res_id : false, "list"],
                [false, "form"],
            ]
        })
    }

    async viewVacantUnits(){
        let domain = [['status', 'in', ['vacant']]]
        if (this.state.period > 0){
            domain.push(['create_date','>', this.state.current_date])
        }

        let list_view = await this.orm.searchRead("ir.model.data", [['name', '=', 'product_template_tree_view']], ['res_id'])

        this.actionService.doAction({
            type: "ir.actions.act_window",
            name: "Vacant Units",
            res_model: "product.template",
            domain,
            views: [
                [list_view.length > 0 ? list_view[0].res_id : false, "list"],
                [false, "form"],
            ]
        })
    }

    async viewAssignUnits(){
        let domain = [['status', 'in', ['assign']]]
        if (this.state.period > 0){
            domain.push(['create_date','>', this.state.current_date])
        }

        let list_view = await this.orm.searchRead("ir.model.data", [['name', '=', 'product_template_tree_view']], ['res_id'])

        this.actionService.doAction({
            type: "ir.actions.act_window",
            name: "Assign Units",
            res_model: "product.template",
            domain,
            views: [
                [list_view.length > 0 ? list_view[0].res_id : false, "list"],
                [false, "form"],
            ]
        })
    }

    async viewBookedUnits(){
        let domain = [['status', 'in', ['booked']]]
        if (this.state.period > 0){
            domain.push(['create_date','>', this.state.current_date])
        }

        let list_view = await this.orm.searchRead("ir.model.data", [['name', '=', 'product_template_tree_view']], ['res_id'])

        this.actionService.doAction({
            type: "ir.actions.act_window",
            name: "Booked Units",
            res_model: "product.template",
            domain,
            views: [
                [list_view.length > 0 ? list_view[0].res_id : false, "list"],
                [false, "form"],
            ]
        })
    }

    async viewOccupiedUnits(){
        let domain = [['status', 'in', ['occupied']]]
        if (this.state.period > 0){
            domain.push(['create_date','>', this.state.current_date])
        }

        let list_view = await this.orm.searchRead("ir.model.data", [['name', '=', 'product_template_tree_view']], ['res_id'])

        this.actionService.doAction({
            type: "ir.actions.act_window",
            name: "Occupied Units",
            res_model: "product.template",
            domain,
            views: [
                [list_view.length > 0 ? list_view[0].res_id : false, "list"],
                [false, "form"],
            ]
        })
    }


    async viewOpportunities() {
        let domain = [
            ['type', '=', 'opportunity'] 
        ];
        if (this.state.period > 0) {
            domain.push(['create_date', '>', this.state.current_date]);
        }
    
        let list_view = await this.orm.searchRead("ir.model.data", [['name', '=', 'crm_case_tree_view_oppor']], ['res_id']);
        // let form_view = await this.orm.searchRead("ir.model.data", [['name', '=', 'view_crm_lead_form']], ['res_id']);
    
        this.actionService.doAction({
            type: "ir.actions.act_window",
            name: "Opportunities",
            res_model: "crm.lead",
            domain,
            views: [
                [list_view.length > 0 ? list_view[0].res_id : false, "list"],  
                // [form_view.length > 0 ? form_view[0].res_id : false, "form"], 
            ]
        });
    }
    
    viewOrders(){
        let domain = [['state', 'in', ['sale', 'done']]]
        if (this.state.period > 0){
            domain.push(['date_order','>', this.state.current_date])
        }

        this.actionService.doAction({
            type: "ir.actions.act_window",
            name: "Quotations",
            res_model: "sale.order",
            domain,
            context: {group_by: ['date_order']},
            views: [
                [false, "list"],
                [false, "form"],
            ]
        })
    }

    viewRevenues(){
        let domain = [['state', 'in', ['sale', 'done']]]
        if (this.state.period > 0){
            domain.push(['date_order','>', this.state.current_date])
        }

        this.actionService.doAction({
            type: "ir.actions.act_window",
            name: "Quotations",
            res_model: "sale.order",
            domain,
            context: {group_by: ['date_order']},
            views: [
                [false, "pivot"],
                [false, "form"],
            ]
        })
    }
}

OwlSalesDashboard.template = "owl.OwlSalesDashboard"
OwlSalesDashboard.components = { KpiCard, ChartRenderer }

registry.category("actions").add("owl.sales_dashboard", OwlSalesDashboard)
