from flask_restx import Namespace, Resource, fields
from flask import request, current_app
from app.services.contract_service import ContractService

api = Namespace('contracts', description='Contract related operations')

contract_details_model = api.model('ContractDetails', {
    'contract_name': fields.String(required=True, description='Contract name'),
    'contract_category': fields.String(required=True, description='Contract category'),
    'contract_type': fields.String(required=True, description='Contract type'),
    'party1': fields.String(required=True, description='First party'),
    'party2': fields.String(required=True, description='Second party'),
    'start_date': fields.String(required=True, description='Contract start date (YYYY-MM-DD)'),
    'end_date': fields.String(required=True, description='Contract end date (YYYY-MM-DD)')
})

contract_model = api.model('Contract', {
    'contract_number': fields.String(required=True, description='Contract number'),
    'status': fields.String(required=True, description='Contract status'),
    'details': fields.Nested(contract_details_model, required=True, description='Contract details')
})

negotiate_change_model = api.model('NegotiationChange', {
    'field': fields.String(required=True, description='Field being changed'),
    'old_value': fields.String(required=True, description='Old value'),
    'new_value': fields.String(required=True, description='New value')
})

negotiate_contract_model = api.model('NegotiateContract', {
    'negotiation_status': fields.String(required=True, description='Negotiation status'),
    'proposed_changes': fields.List(fields.Nested(negotiate_change_model), required=True, description='List of proposed changes'),
    'negotiator_notes': fields.String(required=True, description='Negotiator notes')
})

@api.route('/')
class ContractList(Resource):
    @api.expect(contract_model)
    @api.response(201, 'Contract created successfully')
    @api.response(400, 'Missing contract_number or details / Validation error')
    @api.response(500, 'Internal server error')
    def post(self):
        """API to create new contracts."""
        data = request.get_json()
        if not data or 'contract_number' not in data or 'details' not in data:
            return {"message": "Missing contract_number or details"}, 400
        try:
            contract = ContractService.create_contract(current_app.db, data) # type: ignore
            return contract.to_dict(), 201
        except ValueError as e:
            return {"message": str(e)}, 400
        except Exception as e:
            return {"message": "Internal server error"}, 500

@api.route('/<string:contract_number>')
class Contract(Resource):
    @api.response(200, 'Success')
    @api.response(404, 'Contract not found')
    def get(self, contract_number):
        """API to fetch contract data."""
        contract = ContractService.get_contract(current_app.db, contract_number) # type: ignore
        if contract:
            return contract.to_dict(), 200
        return {"message": "Contract not found"}, 404

@api.route('/<string:contract_number>/negotiate')
class NegotiateContract(Resource):
    @api.expect(negotiate_contract_model)
    @api.response(200, 'Contract negotiated successfully')
    @api.response(400, 'Validation error')
    @api.response(500, 'Internal server error')
    def put(self, contract_number):
        """API to negotiate created contracts."""
        data = request.get_json()
        try:
            updated_contract = ContractService.negotiate_contract(current_app.db, contract_number, data) # type: ignore
            return updated_contract.to_dict(), 200
        except ValueError as e:
            return {"message": str(e)}, 400
        except Exception as e:
            return {"message": "Internal server error"}, 500

@api.route('/<string:contract_number>/approve')
class ApproveContract(Resource):
    @api.response(200, 'Contract approved successfully')
    @api.response(400, 'Validation error')
    @api.response(500, 'Internal server error')
    def put(self, contract_number):
        """API to approve existing contracts."""
        try:
            updated_contract = ContractService.approve_reject_contract(current_app.db, contract_number, 'APPROVED') # type: ignore
            return updated_contract.to_dict(), 200
        except ValueError as e:
            return {"message": str(e)}, 400
        except Exception as e:
            return {"message": "Internal server error"}, 500

@api.route('/<string:contract_number>/reject')
class RejectContract(Resource):
    @api.response(200, 'Contract rejected successfully')
    @api.response(400, 'Validation error')
    @api.response(500, 'Internal server error')
    def put(self, contract_number):
        """API to reject existing contracts."""
        try:
            updated_contract = ContractService.approve_reject_contract(current_app.db, contract_number, 'REJECTED') # type: ignore
            return updated_contract.to_dict(), 200
        except ValueError as e:
            return {"message": str(e)}, 400
        except Exception as e:
            return {"message": "Internal server error"}, 500

@api.route('/<string:contract_number>/sign')
class SignContract(Resource):
    @api.response(200, 'Contract signed successfully')
    @api.response(400, 'Validation error')
    @api.response(500, 'Internal server error')
    def put(self, contract_number):
        """API to digitally sign contracts."""
        try:
            updated_contract = ContractService.sign_contract(current_app.db, contract_number) # type: ignore
            return updated_contract.to_dict(), 200
        except ValueError as e:
            return {"message": str(e)}, 400
        except Exception as e:
            return {"message": "Internal server error"}, 500

@api.route('/<string:contract_number>/execute')
class ExecuteContract(Resource):
    @api.response(200, 'Contract executed successfully')
    @api.response(400, 'Validation error')
    @api.response(500, 'Internal server error')
    def put(self, contract_number):
        """API to execute a contract to form the final contract document."""
        try:
            updated_contract, document_info = ContractService.execute_contract(current_app.db, current_app.gridfs, contract_number) # type: ignore
            response_data = updated_contract.to_dict()
            response_data['final_document'] = document_info
            return response_data, 200
        except ValueError as e:
            return {"message": str(e)}, 400
        except Exception as e:
            return {"message": "Internal server error"}, 500

@api.route('/search')
class SearchExecutedContracts(Resource):
    @api.response(200, 'Success')
    def get(self):
        """API to search executed contracts."""
        query_params = request.args.to_dict()
        contracts = ContractService.search_executed_contracts(current_app.db, query_params) # type: ignore
        return [c.to_dict() for c in contracts], 200

@api.route('/<string:contract_number>/renew')
class RenewContract(Resource):
    @api.response(200, 'Contract renewed successfully')
    @api.response(400, 'Validation error')
    @api.response(500, 'Internal server error')
    def put(self, contract_number):
        """API to renew executed contracts if expired."""
        try:
            renewed_contract = ContractService.renew_contract(current_app.db, contract_number) # type: ignore
            return renewed_contract.to_dict(), 200
        except ValueError as e:
            return {"message": str(e)}, 400
        except Exception as e:
            return {"message": "Internal server error"}, 500

@api.route('/migrate')
class MigrateOldContracts(Resource):
    @api.response(200, 'Migration successful')
    @api.response(500, 'Migration failed')
    def post(self):
        """API to migrate older contracts stored in SQL to new system."""
        try:
            migration_summary = ContractService.migrate_older_contracts(current_app.db, current_app.gridfs) # type: ignore
            return migration_summary, 200
        except Exception as e:
            return {"message": f"Migration failed: {str(e)}"}, 500