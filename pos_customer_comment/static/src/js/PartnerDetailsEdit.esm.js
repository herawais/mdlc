/** @odoo-module **/
import PartnerDetailsEdit from "point_of_sale.PartnerDetailsEdit";
import Registries from "point_of_sale.Registries";

const PartnerDetailsEditComment = (OriginalPartnerDetailsEdit) =>
    class extends OriginalPartnerDetailsEdit {
        setup() {
            super.setup();
            this.changes = {
                ...this.changes,
                pos_comment: this.props.partner.pos_comment || "",
                identification_id: this.props.partner.identification_id || "",
                rif: this.props.partner.rif || "",

            };
        }
    };

Registries.Component.extend(PartnerDetailsEdit, PartnerDetailsEditComment);
