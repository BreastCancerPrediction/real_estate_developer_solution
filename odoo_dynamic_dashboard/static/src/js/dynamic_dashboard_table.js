/** @odoo-module **/
import { _t } from "@web/core/l10n/translation";
const { Component, xml } = owl;
import { ConfirmationDialog } from "@web/core/confirmation_dialog/confirmation_dialog";
// import { $ } from "@web/core/utils/odoo";

export class DynamicTableView extends Component {
    setup() {
        this.records = this.props.widget.records || [];
        this.columns = this.props.widget.columns || [];
        this.doAction = this.props.doAction.doAction;
        this.dialog = this.props.dialog;
        this.orm = this.props.orm;
        this.currentPage = 1;
        this.recordsPerPage = 40;
    }

    get totalPages() {
        return Math.ceil(this.props.widget.records.length / this.recordsPerPage);
    }

    get visibleRecords() {
        const start = (this.currentPage - 1) * this.recordsPerPage;
        const end = start + this.recordsPerPage;
        return this.props.widget.records.slice(start, end);
    }

    nextPage() {
        if (this.currentPage < this.totalPages) {
            this.currentPage += 1;
            this.render();
        }
    }

    previousPage() {
        if (this.currentPage > 1) {
            this.currentPage -= 1;
            this.render();
        }
    }

    // Function to get the configuration of the tile
    async getConfiguration(ev){
        ev.stopPropagation();
        ev.preventDefault();
        var id = this.props.widget.id
        await this.doAction({
                type: 'ir.actions.act_window',
                res_model: 'dashboard.block',
                res_id: id,
                view_mode: 'form',
                views: [[false, "form"]]
            });
    }
    // Function to remove the tile
    async removeTile(ev){
        ev.stopPropagation();
        ev.preventDefault();
        this.dialog.add(ConfirmationDialog, {
            title: _t("Delete Confirmation"),
            body: _t("Are you sure you want to delete this item?"),
            confirmLabel: _t("YES, I'M SURE"),
            cancelLabel: _t("NO, GO BACK"),
            confirm: async () => {
                await this.orm.unlink("dashboard.block", [this.props.widget.id]);
                location.reload();
            },
            cancel: () => {},
        });
    }

}
DynamicTableView.template = xml`
<div class="resize-drag p-4 table_cus"
        t-att-data-x="this.props.widget.data_x"
        t-att-data-y="this.props.widget.data_y"
        t-att-style="'height:' + this.props.widget.height + '; width:' + this.props.widget.width + '; transform: translate(' + this.props.widget.translate_x + ', ' + this.props.widget.translate_y + '); background-color: white !important;'"
        t-att-data-id="this.props.widget.id" >

    <!-- Pagination Controls -->
    <div class="pagination-controls d-flex justify-content-end gap-3 mt-3">
        <div class="d-flex gap-3 mb-3">
            <button type="button" class="btn btn-secondary" t-on-click="previousPage" t-att-disabled="currentPage === 1">Prev</button>
            <span class="text-dark mt-2">Page <t t-esc="currentPage"/> of <t t-esc="totalPages"/></span>
            <button type="button" class="btn btn-secondary" t-on-click="nextPage" t-att-disabled="currentPage === totalPages">Next</button>
        </div>
    </div>

    <div class="dynamic-table-container table-container"
        t-att-data-id="this.props.widget.id"
        t-att-data-x="this.props.widget.data_x"
        t-att-data-y="this.props.widget.data_y">
        
        <!-- Edit and Delete icons -->
        <a class="block_setting tile_edit tile-container__setting-icon" style="color:black;" t-on-click="(ev) => this.getConfiguration(ev)">
            <i class="fa fa-edit"/>
        </a>
        <a class="block_delete tile_edit tile-container__delete-icon" style="color:black;" t-on-click="(ev) => this.removeTile(ev)">
            <i class="fa fa-times"/>
        </a>

        <!-- Table Title -->
        <h3 class="chart_title">
            <t t-esc="this.props.widget.name"/>
        </h3>

        <!-- Dynamic Table -->
        <table class="table table-bordered table-striped text-dark mt-4">
            <thead class="bg-light-blue border-dark">
                <tr>
                    <t t-foreach="columns" t-as="col" t-key="col.technical_name">
                      <th t-esc="col.name" style="font-weight: bold;"/>
                    </t>
                </tr>
            </thead>

            <tbody>
                <t t-foreach="visibleRecords" t-as="record" t-key="record.id">
                    <tr>
                        <t t-foreach="columns" t-as="col" t-key="col.technical_name">
                            <td t-esc="record[col.technical_name]"/>
                        </t>
                    </tr>
                </t>
            </tbody>
        </table>
    </div>
</div>
`;


