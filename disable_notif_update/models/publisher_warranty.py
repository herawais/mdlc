# -*- coding: utf-8 -*-
import logging
from odoo.models import AbstractModel
from odoo import api, release, SUPERUSER_ID
_logger = logging.getLogger(__name__)


class PublisherWarrantyContract(AbstractModel):
    _name = "publisher_warranty.contract"
    _inherit = "publisher_warranty.contract"

    @api.model
    def _get_message(self):
        msg = {
        }
        return msg
    def update_notification(self, cron_mode=True):
        """
        Send a message to Odoo's publisher warranty server to check the
        validity of the contracts, get notifications, etc...

        @param cron_mode: If true, catch all exceptions (appropriate for usage in a cron).
        @type cron_mode: boolean
        """
        return True
