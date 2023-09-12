# -*- coding: utf-8 -*-

from odoo import fields, models, api, _, tools
from collections import defaultdict
from odoo.tools import float_is_zero
import logging
_logger = logging.getLogger(__name__)
from odoo.exceptions import UserError



class PosSession(models.Model):
	_inherit = 'pos.session'

	igtf_move_ids = fields.Many2many("account.move",string="IGTF Moves")

	def _loader_params_res_company(self):
		result = super(PosSession, self)._loader_params_res_company()
		result['search_params']['fields'].extend(['is_igtf','igtf_percentage'])
		return result

	def _loader_params_pos_payment_method(self):
		result = super(PosSession, self)._loader_params_pos_payment_method()
		result['search_params']['fields'].extend(['is_igtf'])
		return result

	def _loader_params_res_partner(self):
		result = super(PosSession, self)._loader_params_res_partner()
		result['search_params']['fields'].extend(['rif'])
		return result


	# def _validate_session(self):
	# 	res = super(PosSession, self)._validate_session()
	# 	for stmnt in self.statement_ids:
	# 		pay_method = self.env['pos.payment.method'].search([
	# 			('is_igtf','=',True)])
	# 		if pay_method :
				
	# 			move_vals = {
	# 				'move_type': 'entry',
	# 				'date': fields.Date.today(),
	# 				'ref': self.name +'-IGTF-'+ stmnt.journal_id.name,
	# 				'journal_id': stmnt.journal_id.id,
	# 				'currency_id' : stmnt.currency_id.id
	# 			}
	# 			move_vals['line_ids'] = [(0, 0, line_vals) for line_vals in self._prepare_move_line_default_vals_igft(stmnt.id,write_off_line_vals=None)]
	# 			igtf_move_id = self.env['account.move'].create(move_vals)
	# 			igtf_move_id._post(soft=False)
	# 			self.write({
	# 				'igtf_move_ids' : [(4,igtf_move_id.id)],
	# 			})
	# 	return res

	# def _prepare_move_line_default_vals_igft(self,stmnt, write_off_line_vals=None):
	# 	''' Prepare the dictionary to create the default account.move.lines for the current payment.
	# 	:param write_off_line_vals: Optional dictionary to create a write-off account.move.line easily containing:
	# 		* amount:       The amount to be added to the counterpart amount.
	# 		* name:         The label to set on the line.
	# 		* account_id:   The account on which create the write-off.
	# 	:return: A list of python dictionary to be passed to the account.move.line's 'create' method.
	# 	'''
	# 	self.ensure_one()
	# 	stmnt_id = self.env['account.bank.statement'].sudo().browse(stmnt)
	# 	journal_id = stmnt_id.journal_id
	# 	write_off_line_vals = write_off_line_vals or {}

	# 	if not journal_id.payment_debit_account_id or not journal_id.payment_credit_account_id:
	# 		raise UserError(_(
	# 			"You can't create a new payment without an outstanding payments/receipts account set on the %s journal.",
	# 			journal_id.display_name))

	# 	# Compute amounts.
	# 	write_off_amount_currency = 0.0

		

	# 	if stmnt_id.igtf_pos_amount >= 0:
	# 		# Receive money.
	# 		liquidity_amount_currency = stmnt_id.igtf_pos_amount
	# 	elif stmnt_id.igtf_pos_amount < 0 :
	# 		# Send money.
	# 		liquidity_amount_currency = -stmnt_id.igtf_pos_amount
	# 		write_off_amount_currency *= -1
	# 	else:
	# 		liquidity_amount_currency = write_off_amount_currency = 0.0

	# 	write_off_balance = stmnt_id.currency_id._convert(
	# 		write_off_amount_currency,
	# 		self.company_id.currency_id,
	# 		self.company_id,
	# 		fields.Date.today(),
	# 	)
	# 	liquidity_balance = stmnt_id.currency_id._convert(
	# 		liquidity_amount_currency,
	# 		self.company_id.currency_id,
	# 		self.company_id,
	# 		fields.Date.today(),
	# 	)
	# 	counterpart_amount_currency = -liquidity_amount_currency - write_off_amount_currency
	# 	counterpart_balance = -liquidity_balance - write_off_balance
	# 	currency_id = stmnt_id.currency_id.id

		
	# 	liquidity_line_name = stmnt_id.pos_session_id.name +'-IGTF-'+ journal_id.name,

	# 	# Compute a default label to set on the journal items.

	# 	line_vals_list = [
	# 		# Liquidity line.
	# 		{
	# 			'name': 'Comision IGTF Divisa',
	# 			'date_maturity': fields.Date.today(),
	# 			'amount_currency': liquidity_amount_currency,
	# 			'currency_id': currency_id,
	# 			'debit': liquidity_balance if liquidity_balance > 0.0 else 0.0,
	# 			'credit': -liquidity_balance if liquidity_balance < 0.0 else 0.0,
	# 			'account_id': journal_id.payment_credit_account_id.id if liquidity_balance < 0.0 else journal_id.payment_debit_account_id.id,
	# 		},
	# 		# Receivable / Payable.
	# 		{
	# 			'name': 'Comision IGTF Divisa',
	# 			'date_maturity': fields.Date.today(),
	# 			'amount_currency': counterpart_amount_currency,
	# 			'currency_id': currency_id,
	# 			'debit': counterpart_balance if counterpart_balance > 0.0 else 0.0,
	# 			'credit': -counterpart_balance if counterpart_balance < 0.0 else 0.0,
	# 			'account_id': self.company_id.receivable_account_id.id if liquidity_balance < 0.0 else self.company_id.payable_account_id.id,
	# 		},
	# 	]
	# 	return line_vals_list

	def _accumulate_amounts(self, data):
		print("\n\nmakwna=======================")
		# Accumulate the amounts for each accounting lines group
		# Each dict maps `key` -> `amounts`, where `key` is the group key.
		# E.g. `combine_receivables_bank` is derived from pos.payment records
		# in the self.order_ids with group key of the `payment_method_id`
		# field of the pos.payment record.
		amounts = lambda: {'amount': 0.0, 'amount_converted': 0.0}
		tax_amounts = lambda: {'amount': 0.0, 'amount_converted': 0.0, 'base_amount': 0.0, 'base_amount_converted': 0.0}
		split_receivables_bank = defaultdict(amounts)
		split_receivables_cash = defaultdict(amounts)
		split_receivables_pay_later = defaultdict(amounts)
		combine_receivables_bank = defaultdict(amounts)
		print("combine_receivables_bank=====================",combine_receivables_bank)
		combine_receivables_cash = defaultdict(amounts)
		combine_receivables_pay_later = defaultdict(amounts)
		combine_invoice_receivables = defaultdict(amounts)
		split_invoice_receivables = defaultdict(amounts)
		sales = defaultdict(amounts)
		taxes = defaultdict(tax_amounts)
		stock_expense = defaultdict(amounts)
		stock_return = defaultdict(amounts)
		stock_output = defaultdict(amounts)
		rounding_difference = {'amount': 0.0, 'amount_converted': 0.0}
		# Track the receivable lines of the order's invoice payment moves for reconciliation
		# These receivable lines are reconciled to the corresponding invoice receivable lines
		# of this session's move_id.
		combine_inv_payment_receivable_lines = defaultdict(lambda: self.env['account.move.line'])
		split_inv_payment_receivable_lines = defaultdict(lambda: self.env['account.move.line'])
		rounded_globally = self.company_id.tax_calculation_rounding_method == 'round_globally'
		pos_receivable_account = self.company_id.account_default_pos_receivable_account_id
		currency_rounding = self.currency_id.rounding
		for order in self.order_ids:
			order_is_invoiced = order.is_invoiced
			for payment in order.payment_ids:
				amount = payment.amount
				if float_is_zero(amount, precision_rounding=currency_rounding):
					continue
				date = payment.payment_date
				payment_method = payment.payment_method_id
				is_split_payment = payment.payment_method_id.split_transactions
				payment_type = payment_method.type

				# If not pay_later, we create the receivable vals for both invoiced and uninvoiced orders.
				#   Separate the split and aggregated payments.
				# Moreover, if the order is invoiced, we create the pos receivable vals that will balance the
				# pos receivable lines from the invoice payments.
				if payment_type != 'pay_later':
					if is_split_payment and payment_type == 'cash':
						split_receivables_cash[payment] = self._update_amounts(split_receivables_cash[payment], {'amount': amount}, date)
					elif not is_split_payment and payment_type == 'cash':
						combine_receivables_cash[payment_method] = self._update_amounts(combine_receivables_cash[payment_method], {'amount': amount}, date)
					elif is_split_payment and payment_type == 'bank':
						split_receivables_bank[payment] = self._update_amounts(split_receivables_bank[payment], {'amount': amount}, date)
					elif not is_split_payment and payment_type == 'bank':
						combine_receivables_bank[payment_method] = self._update_amounts(combine_receivables_bank[payment_method], {'amount': amount}, date)

					# Create the vals to create the pos receivables that will balance the pos receivables from invoice payment moves.
					if order_is_invoiced:
						if is_split_payment:
							split_inv_payment_receivable_lines[payment] |= payment.account_move_id.line_ids.filtered(lambda line: line.account_id == pos_receivable_account)
							split_invoice_receivables[payment] = self._update_amounts(split_invoice_receivables[payment], {'amount': payment.amount}, order.date_order)
						else:
							combine_inv_payment_receivable_lines[payment_method] |= payment.account_move_id.line_ids.filtered(lambda line: line.account_id == pos_receivable_account)
							combine_invoice_receivables[payment_method] = self._update_amounts(combine_invoice_receivables[payment_method], {'amount': payment.amount}, order.date_order)

				# If pay_later, we create the receivable lines.
				#   if split, with partner
				#   Otherwise, it's aggregated (combined)
				# But only do if order is *not* invoiced because no account move is created for pay later invoice payments.
				if payment_type == 'pay_later' and not order_is_invoiced:
					if is_split_payment:
						split_receivables_pay_later[payment] = self._update_amounts(split_receivables_pay_later[payment], {'amount': amount}, date)
					elif not is_split_payment:
						combine_receivables_pay_later[payment_method] = self._update_amounts(combine_receivables_pay_later[payment_method], {'amount': amount}, date)

			if not order_is_invoiced:
				order_taxes = defaultdict(tax_amounts)

				if order.igtf_amount > 0:
					income_acnt = order.company_id.receivable_account_id
					if not income_acnt:
						raise UserError(_('Please define income account for IGTF under company '))
					sale_key1 = (
						# account
						income_acnt.id,
						# sign
						1,
						# for taxes
						tuple(),
						tuple(),
					)	
					sales[sale_key1] = self._update_amounts(sales[sale_key1], {'amount': order.igtf_amount}, order.date_order)

				for order_line in order.lines:
					line = self._prepare_line(order_line)
					# Combine sales/refund lines
					sale_key = (
						# account
						line['income_account_id'],
						# sign
						-1 if line['amount'] < 0 else 1,
						# for taxes
						tuple((tax['id'], tax['account_id'], tax['tax_repartition_line_id']) for tax in line['taxes']),
						line['base_tags'],
					)
					sales[sale_key] = self._update_amounts(sales[sale_key], {'amount': line['amount']}, line['date_order'])
					# Combine tax lines
					for tax in line['taxes']:
						tax_key = (tax['account_id'] or line['income_account_id'], tax['tax_repartition_line_id'], tax['id'], tuple(tax['tag_ids']))
						order_taxes[tax_key] = self._update_amounts(
							order_taxes[tax_key],
							{'amount': tax['amount'], 'base_amount': tax['base']},
							tax['date_order'],
							round=not rounded_globally
						)
				for tax_key, amounts in order_taxes.items():
					if rounded_globally:
						amounts = self._round_amounts(amounts)
					for amount_key, amount in amounts.items():
						taxes[tax_key][amount_key] += amount

				if self.company_id.anglo_saxon_accounting and order.picking_ids.ids:
					# Combine stock lines
					stock_moves = self.env['stock.move'].sudo().search([
						('picking_id', 'in', order.picking_ids.ids),
						('company_id.anglo_saxon_accounting', '=', True),
						('product_id.categ_id.property_valuation', '=', 'real_time')
					])
					for move in stock_moves:
						exp_key = move.product_id._get_product_accounts()['expense']
						out_key = move.product_id.categ_id.property_stock_account_output_categ_id
						amount = -sum(move.sudo().stock_valuation_layer_ids.mapped('value'))
						stock_expense[exp_key] = self._update_amounts(stock_expense[exp_key], {'amount': amount}, move.picking_id.date, force_company_currency=True)
						if move.location_id.usage == 'customer':
							stock_return[out_key] = self._update_amounts(stock_return[out_key], {'amount': amount}, move.picking_id.date, force_company_currency=True)
						else:
							stock_output[out_key] = self._update_amounts(stock_output[out_key], {'amount': amount}, move.picking_id.date, force_company_currency=True)

				if self.config_id.cash_rounding:
					diff = order.amount_paid - order.amount_total
					rounding_difference = self._update_amounts(rounding_difference, {'amount': diff}, order.date_order)

				# Increasing current partner's customer_rank
				partners = (order.partner_id | order.partner_id.commercial_partner_id)
				partners._increase_rank('customer_rank')

		if self.company_id.anglo_saxon_accounting:
			global_session_pickings = self.picking_ids.filtered(lambda p: not p.pos_order_id)
			if global_session_pickings:
				stock_moves = self.env['stock.move'].sudo().search([
					('picking_id', 'in', global_session_pickings.ids),
					('company_id.anglo_saxon_accounting', '=', True),
					('product_id.categ_id.property_valuation', '=', 'real_time'),
				])
				for move in stock_moves:
					exp_key = move.product_id._get_product_accounts()['expense']
					out_key = move.product_id.categ_id.property_stock_account_output_categ_id
					amount = -sum(move.stock_valuation_layer_ids.mapped('value'))
					stock_expense[exp_key] = self._update_amounts(stock_expense[exp_key], {'amount': amount}, move.picking_id.date, force_company_currency=True)
					if move.location_id.usage == 'customer':
						stock_return[out_key] = self._update_amounts(stock_return[out_key], {'amount': amount}, move.picking_id.date, force_company_currency=True)
					else:
						stock_output[out_key] = self._update_amounts(stock_output[out_key], {'amount': amount}, move.picking_id.date, force_company_currency=True)
		MoveLine = self.env['account.move.line'].with_context(check_move_validity=False)

		data.update({
			'taxes':                               taxes,
			'sales':                               sales,
			'stock_expense':                       stock_expense,
			'split_receivables_bank':              split_receivables_bank,
			'combine_receivables_bank':            combine_receivables_bank,
			'split_receivables_cash':              split_receivables_cash,
			'combine_receivables_cash':            combine_receivables_cash,
			'combine_invoice_receivables':         combine_invoice_receivables,
			'split_receivables_pay_later':         split_receivables_pay_later,
			'combine_receivables_pay_later':       combine_receivables_pay_later,
			'stock_return':                        stock_return,
			'stock_output':                        stock_output,
			'combine_inv_payment_receivable_lines': combine_inv_payment_receivable_lines,
			'rounding_difference':                 rounding_difference,
			'MoveLine':                            MoveLine,
			'split_invoice_receivables': split_invoice_receivables,
			'split_inv_payment_receivable_lines': split_inv_payment_receivable_lines,
		})
		return data


	
	def _prepare_balancing_line_vals(self, imbalance_amount, move):
		account = self._get_balancing_account()
		account = self.company_id.payable_account_id
		if not account:
			raise UserError(_(
				"Please Configure Account Details First in Company Go TO Company ==> Select Account 'Cuenta Pagos IGTF'	."))
		partial_vals = {
			'name': _('Difference at closing PoS session'),
			'account_id': account.id,
			'move_id': move.id,
			'partner_id': False,
		}
		# `imbalance_amount` is already in terms of company currency so it is the amount_converted
		# param when calling `_credit_amounts`. amount param will be the converted value of
		# `imbalance_amount` from company currency to the session currency.
		imbalance_amount_session = 0
		if (not self.is_in_company_currency):
			imbalance_amount_session = self.company_id.currency_id._convert(imbalance_amount, self.currency_id, self.company_id, fields.Date.context_today(self))
		return self._credit_amounts(partial_vals, imbalance_amount_session, imbalance_amount)

	