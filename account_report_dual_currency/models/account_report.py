from odoo import api, fields, models, _

class ResCurrency(models.Model):
    _inherit = 'res.currency'
    
    @api.model
    def _get_query_other_currency_table(self, options):
        ''' Construct the currency table as a mapping company -> rate to convert the amount to the user's company
        currency in a multi-company/multi-currency environment.
        The currency_table is a small postgresql table construct with VALUES.
        :param options: The report options.
        :return:        The query representing the currency table.
        '''

        user_company = self.env.company
        currency = options.get('currency')
        # available_currency = options.get('available_currency')
        # available_currency_list = [cur.get('id') for cur in available_currency]
        user_currency = self.browse(currency)
        if user_currency:
            conversion_date = options['date']['date_to']
            currency_rates = user_currency._get_rates(user_company, conversion_date)
        else:
            companies = user_company
            currency_rates = {user_currency.id: 1.0}

        conversion_rates = []
        for currency_id in user_currency:
            if not user_company.currency_id.id in currency_rates:
                currency_rate_ = user_company.currency_id._get_rates(user_company, conversion_date)
                currency_rates.update(currency_rate_)
            conversion_rates.extend((
                user_company.id,
                currency_rates[currency_id.id] / currency_rates[user_company.currency_id.id],
                currency_id.decimal_places,
            ))
        query = '(VALUES %s) AS other_currency_table(company_id, rate, precision)' % ','.join('(%s, %s, %s)' for i in user_currency)
        return self.env.cr.mogrify(query, conversion_rates).decode(self.env.cr.connection.encoding)

class AccountReport(models.AbstractModel):
    _inherit = 'account.report'

    filter_currency = fields.Boolean(
        string="Currency",
        compute=lambda x: x._compute_report_option_filter('filter_currency'), readonly=False, store=True, depends=['root_report_id'],
    )

    def _init_options_currency(self, options, previous_options=None):
        available_currency = []
        allowed_currency_ids = set()
        available_currency_ids = self.env['res.currency'].search([('active','=',True)])
        # print('********============> available_currency_ids', available_currency_ids)
        for variant in available_currency_ids:
            allowed_currency_ids.add(variant.id)
            available_currency.append({
                'id': variant.id,
                'name': '%s' % (variant.name),
            })
        # print('********============> available_currency', available_currency)
        currency_id = self.env.user.company_id.currency_id
        options['available_currency'] = list(available_currency)
        # if not self.filter_currency:
        #     options['available_currency'] = list({currency_id.id : currency_id.name})
        previous_opt_currency = (previous_options or {}).get('currency')
        if previous_opt_currency in allowed_currency_ids or previous_opt_currency == currency_id.id:
            options['currency'] = previous_opt_currency
        else:
            options['currency'] = currency_id.id