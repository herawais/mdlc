# -*- coding: utf-8 -*-
# from odoo import http


# class DisableNotifUpdate(http.Controller):
#     @http.route('/disable_notif_update/disable_notif_update/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/disable_notif_update/disable_notif_update/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('disable_notif_update.listing', {
#             'root': '/disable_notif_update/disable_notif_update',
#             'objects': http.request.env['disable_notif_update.disable_notif_update'].search([]),
#         })

#     @http.route('/disable_notif_update/disable_notif_update/objects/<model("disable_notif_update.disable_notif_update"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('disable_notif_update.object', {
#             'object': obj
#         })
