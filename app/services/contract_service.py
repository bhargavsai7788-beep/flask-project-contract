# app/services/contract_service.py
import logging
from app.models.contract import Contract
from datetime import datetime
from gridfs import GridFS
import io

# Configure basic logging (add this at the top of the file for quick debugging)
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class ContractService:
    @staticmethod
    def create_contract(db, data):
        logging.info(f"Attempting to create contract with data: {data}")
        try:
            contract_number = data['contract_number']
            logging.info(f"Checking for existing contract: {contract_number}")
            if db.contracts.find_one({"contract_number": contract_number}):
                logging.warning(f"Contract with number {contract_number} already exists.")
                raise ValueError(f"Contract with number {contract_number} already exists.")

            logging.info(f"Creating Contract object for {contract_number} with status 'NEW' and details: {data['details']}")
            contract = Contract(contract_number, "NEW", data['details'])

            logging.info(f"Converting contract object to dictionary: {contract.to_dict()}")
            contract_dict = contract.to_dict()

            logging.info(f"Inserting contract into MongoDB collection 'contracts'.")
            db.contracts.insert_one(contract_dict)
            logging.info(f"Contract {contract_number} successfully inserted.")
            return contract
        except Exception as e:
            logging.error(f"Error during contract creation: {e}", exc_info=True) # exc_info=True prints traceback
            raise # Re-raise the exception so Flask's error handler can catch it

    @staticmethod
    def get_contract(db, contract_number):
        contract_data = db.contracts.find_one({"contract_number": contract_number})
        if contract_data:
            return Contract.from_dict(contract_data)
        return None

    @staticmethod
    def _update_contract_status(db, contract_number, new_status, allowed_previous_statuses):
        contract = ContractService.get_contract(db, contract_number)
        if not contract:
            raise ValueError("Contract not found.")
        if contract.status not in allowed_previous_statuses:
            raise ValueError(f"Cannot transition from '{contract.status}' to '{new_status}'.")

        db.contracts.update_one(
            {"contract_number": contract_number},
            {"$set": {"status": new_status, "updated_at": datetime.utcnow()}}
        )
        contract.status = new_status
        contract.updated_at = datetime.utcnow()
        return contract

    @staticmethod
    def negotiate_contract(db, contract_number, negotiation_data):
        contract = ContractService._update_contract_status(db, contract_number, "NEGOTIATION", ["NEW"])
        # Update negotiation details
        db.contracts.update_one(
            {"contract_number": contract_number},
            {"$set": {"details.negotiation": negotiation_data, "updated_at": datetime.utcnow()}}
        )
        contract.details['negotiation'] = negotiation_data
        return contract

    @staticmethod
    def approve_reject_contract(db, contract_number, status):
        # Contract cannot jump intermediate stages
        if status == "APPROVED":
            return ContractService._update_contract_status(db, contract_number, "APPROVED", ["NEGOTIATION"])
        elif status == "REJECTED":
            return ContractService._update_contract_status(db, contract_number, "REJECTED", ["NEGOTIATION"])
        else:
            raise ValueError("Invalid approval status.")

    @staticmethod
    def sign_contract(db, contract_number):
        return ContractService._update_contract_status(db, contract_number, "SIGNED", ["APPROVED"])

    @staticmethod
    def execute_contract(db, gridfs, contract_number):
        contract = ContractService._update_contract_status(db, contract_number, "EXECUTED", ["SIGNED"])

        # Simulate creating a final contract document
        document_content = f"Final Contract Document for {contract_number}\n\nDetails: {contract.details}"

        # Store the document in GridFS
        file_id = gridfs.put(io.BytesIO(document_content.encode('utf-8')), filename=f"{contract_number}_final_contract.txt", contract_number=contract_number)

        # Update contract in MongoDB with document ID
        db.contracts.update_one(
            {"contract_number": contract_number},
            {"$set": {"final_document_id": str(file_id), "updated_at": datetime.utcnow()}}
        )
        contract.details['final_document_id'] = str(file_id) # Add to contract object for response
        return contract, {"document_id": str(file_id), "filename": f"{contract_number}_final_contract.txt"}

    @staticmethod
    def search_executed_contracts(db, query_params):
        # Example: search by contract_number or keywords in details
        search_query = {"status": "EXECUTED"}
        if 'contract_number' in query_params:
            search_query["contract_number"] = query_params['contract_number']
        if 'keyword' in query_params:
            # Create a list of conditions for the $or operator
            # This will search for the keyword in multiple fields
            keyword = query_params['keyword']
            regex_query = {"$regex": keyword, "$options": "i"}
            
            # Build the list of search conditions for the $or clause
            or_conditions = [
                {"details.contract_name": regex_query},
                {"details.contract_category": regex_query},
                {"details.party1": regex_query},
                {"details.party2": regex_query} # You can add as many fields as you need
            ]
            
            # Add the $or operator to the main search_query
            # This will find documents matching any of the conditions in or_conditions
            search_query["$or"] = or_conditions # type: ignore

        contracts_data = db.contracts.find(search_query)
        return [Contract.from_dict(c) for c in contracts_data]

    @staticmethod
    def renew_contract(db, contract_number):
        contract = ContractService.get_contract(db, contract_number)
        if not contract:
            raise ValueError("Contract not found.")
        # Assuming an 'expiration_date' in details
        if contract.status == "EXECUTED": # You might also want to check if it's "EXPIRED"
            # For simplicity, we just mark as RENEWED.
            # In a real system, you'd create a new contract version or update expiration date.
            db.contracts.update_one(
                {"contract_number": contract_number},
                {"$set": {"status": "RENEWED", "updated_at": datetime.utcnow(), "details.last_renewal_date": datetime.utcnow()}}
            )
            contract.status = "RENEWED"
            contract.updated_at = datetime.utcnow()
            contract.details['last_renewal_date'] = datetime.utcnow()
            return contract
        else:
            raise ValueError(f"Contract status must be 'EXECUTED' to be renewed. Current status: {contract.status}")

    @staticmethod
    def migrate_older_contracts(db, gridfs_db):
        """
        Simulates migration from an older SQL-based system.
        In a real scenario, this would connect to the SQL DB, fetch data,
        and insert into MongoDB/GridFS.
        """
        # Placeholder for connecting to old SQL DB
        # For demonstration, we'll just create some dummy old contracts
        migrated_count = 0

        # Simulate fetching old contract data (e.g., from an SQL query result)
        old_contracts_data = [
            {"contract_number": "OLD-001", "old_status": "COMPLETED", "old_text": "This is an old contract text 1."},
            {"contract_number": "OLD-002", "old_status": "ARCHIVED", "old_text": "This is another old contract text 2."}
        ]

        for old_contract in old_contracts_data:
            contract_number = old_contract["contract_number"]
            if not db.contracts.find_one({"contract_number": contract_number}):
                # Create new contract entry
                new_contract_details = {
                    "migrated_from_sql": True,
                    "old_system_status": old_contract["old_status"],
                    "original_content_summary": old_contract["old_text"]
                }
                new_contract = Contract(contract_number, "MIGRATED", new_contract_details)
                db.contracts.insert_one(new_contract.to_dict())

                # Store old document content in GridFS if applicable
                old_document_content = f"Original content of old contract {contract_number}: {old_contract['old_text']}"
                file_id = gridfs_db.put(io.BytesIO(old_document_content.encode('utf-8')), 
                                            filename=f"{contract_number}_old_document.txt", 
                                            contract_number=contract_number, 
                                            migrated=True)

                db.contracts.update_one(
                    {"contract_number": contract_number},
                    {"$set": {"migrated_document_id": str(file_id), "updated_at": datetime.utcnow()}}
                )
                migrated_count += 1

        return {"status": "success", "migrated_count": migrated_count, "message": "Migration simulated successfully."}