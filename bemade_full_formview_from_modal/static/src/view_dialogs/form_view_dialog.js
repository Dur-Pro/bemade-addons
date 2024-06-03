/** @odoo-module **/

import { patch } from "@web/core/utils/patch";
import { useService } from "@web/core/utils/hooks";
import { X2ManyFieldDialog } from "@web/views/fields/relational_utils"
import { FormViewDialog } from "@web/views/view_dialogs/form_view_dialog"

patch(X2ManyFieldDialog.prototype, {
    setup () {
        super.setup();
        this.action = useService('action')
        this.env.dialogData.onOpenButtonClicked = this.onOpenButtonClicked.bind(this);
    },
    onOpenButtonClicked: function () {
        this.action.doAction({
            type: "ir.actions.act_window",
            res_model: this.record.resModel,
            res_id: this.record.resId,
            views: [[false, "form"]],
            target: "current",
            context: this.props.context,
        })
    }
})

patch(FormViewDialog.prototype, {
    setup () {
        super.setup();
        this.action = useService('action')
        this.onOpenButtonClicked = this.onOpenButtonClicked.bind(this);
    },
    onOpenButtonClicked() {
        this.action.doAction({
            type: "ir.actions.act_window",
            res_model: this.props.resModel,
            res_id: this.props.resId,
            views: [[false, "form"]],
            target: "current",
            context: this.props.context,
        })
    }
})
