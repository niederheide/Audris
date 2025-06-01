"""
Main entry point for the DORA Assessment Agent.

This module initializes the application components and provides
the core functionality for the DORA Assessment Agent.
"""

from typing import Dict, Any, List, Optional, Tuple
import os
import sys
import uuid
import datetime
import io

# Import application components
from app.config import config
from app.utils.logger import Logger
from app.contracts.parser import DocumentParser
from app.contracts.clause_extractor import ClauseExtractor
from app.contracts.compliance_checker import ComplianceChecker
from app.risk.qualifier import ICTRiskQualifier
from app.risk.contract_risk_extractor import ContractRiskExtractor
from app.risk.rules import DORARules
from app.onboarding.checklist import OnboardingChecklist
from app.onboarding.validator import OnboardingValidator
from app.register.database import db_handler as postgres_db_handler
from app.register.builder import RegisterBuilder
from app.register.exporter import RegisterExporter
from app.alerts.notifier import ComplianceAlertEngine
from app.utils.file_loader import FileLoader
from app.database.handler import DatabaseHandler
from app.database.contract_repository import ContractRepository

class DORAAssessmentAgent:
    """
    Main application class for the DORA Assessment Agent.
    
    This class orchestrates all the components of the application
    and provides the core functionality.
    """
    
    def __init__(self):
        """Initialize the DORA Assessment Agent."""
        # Initialize logger
        self.logger = Logger(
            log_level=config.get("log_level", "INFO"),
            log_file=config.get("log_file")
        )
        self.logger.info("Initializing DORA Assessment Agent")
        
        # Use PostgreSQL database handler
        self.db_handler = postgres_db_handler
        
        # Initialize new database handler and contract repository
        self.database_handler = DatabaseHandler()
        self.database_handler.initialize_schema()
        self.contract_repository = ContractRepository(self.database_handler)
        
        # Initialize components
        self.document_parser = DocumentParser()
        self.clause_extractor = ClauseExtractor()
        self.compliance_checker = ComplianceChecker()
        self.risk_qualifier = ICTRiskQualifier()
        self.contract_risk_extractor = ContractRiskExtractor()
        self.dora_rules = DORARules()
        self.onboarding_checklist = OnboardingChecklist()
        self.onboarding_validator = OnboardingValidator(self.onboarding_checklist)
        self.register_builder = RegisterBuilder(self.db_handler)
        self.register_exporter = RegisterExporter()
        self.alert_engine = ComplianceAlertEngine(self.db_handler)
        self.file_loader = FileLoader()
        
        self.logger.info("DORA Assessment Agent initialized")
    
    def process_contract(self, file_content: bytes, filename: str) -> Dict[str, Any]:
        """
        Process a contract document and extract DORA-relevant clauses.
        
        Args:
            file_content: Binary content of the file
            filename: Name of the file
            
        Returns:
            Dictionary with extracted clauses and compliance assessment
        """
        self.logger.info(f"Processing contract: {filename}")
        
        try:
            # Parse document
            paragraphs = self.document_parser.parse_document(file_content, filename)
            
            # Extract clauses
            extracted_clauses = self.clause_extractor.extract_relevant_clauses(paragraphs)
            
            # Evaluate clause completeness
            clause_evaluation = self.clause_extractor.evaluate_clause_completeness(extracted_clauses)
            
            # Check compliance
            compliance_results = self.compliance_checker.check_compliance(extracted_clauses)
            
            self.logger.info(f"Contract processed successfully: {filename}")
            
            contract_analysis = {
                "filename": filename,
                "processed_at": datetime.datetime.now().isoformat(),
                "paragraphs_count": len(paragraphs),
                "extracted_clauses": extracted_clauses,
                "clause_evaluation": clause_evaluation,
                "compliance_results": compliance_results
            }
            
            # Save the contract to the repository
            try:
                contract_id = self.contract_repository.save_contract(contract_analysis)
                contract_analysis['id'] = contract_id
                self.logger.info(f"Contract saved to repository with ID: {contract_id}")
            except Exception as e:
                self.logger.warning(f"Failed to save contract to repository: {str(e)}")
                
            return contract_analysis
            
        except Exception as e:
            self.logger.error(f"Error processing contract: {str(e)}", exc_info=True)
            raise
    
    def extract_risk_factors_from_contract(self, contract_analysis: Dict[str, Any]) -> Dict[str, Dict[str, bool]]:
        """
        Extract risk factors from contract analysis results.
        
        Args:
            contract_analysis: Contract analysis results
            
        Returns:
            Dictionary with risk factors that can be used for ICT risk assessment
        """
        self.logger.info("Extracting risk factors from contract analysis")
        
        try:
            risk_factors = self.contract_risk_extractor.extract_risk_factors(contract_analysis)
            
            self.logger.info("Risk factors extracted successfully from contract")
            
            return risk_factors
            
        except Exception as e:
            self.logger.error(f"Error extracting risk factors from contract: {str(e)}", exc_info=True)
            return {}
    
    def assess_ict_risk(self, responses: Dict[str, Dict[str, bool]], 
                        contract_analysis: Optional[Dict[str, Any]] = None,
                        service_details: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Assess ICT risk based on questionnaire responses and optionally contract analysis.
        
        Args:
            responses: Dictionary with questionnaire responses
            contract_analysis: Contract analysis results (optional)
            service_details: Service details (optional)
            
        Returns:
            Dictionary with risk assessment results
        """
        self.logger.info("Performing ICT risk assessment")
        
        try:
            # If contract analysis is provided, extract risk factors
            contract_risk_factors = {}
            if contract_analysis:
                contract_risk_factors = self.contract_risk_extractor.extract_risk_factors(contract_analysis)
                self.logger.info("Extracted risk factors from contract analysis")
            
            # If service details are provided, extract risk factors
            service_risk_factors = {}
            if service_details:
                service_risk_factors = self.contract_risk_extractor.extract_risk_from_service_details(service_details)
                self.logger.info("Extracted risk factors from service details")
            
            # Merge user responses with extracted risk factors
            enriched_responses = responses.copy()
            
            # Initialize extracted_factors
            extracted_factors = {}
            
            if contract_risk_factors or service_risk_factors:
                # Merge all risk factors
                extracted_factors = self.contract_risk_extractor.merge_risk_factors(
                    contract_risk_factors, service_risk_factors
                )
                
                # Add factors to user responses where not already specified
                for category, factors in extracted_factors.items():
                    if category not in enriched_responses:
                        enriched_responses[category] = {}
                    
                    for factor, value in factors.items():
                        # Only use extracted factor if user hasn't specified it
                        if factor not in enriched_responses[category]:
                            enriched_responses[category][factor] = value
            
            # Perform risk assessment with enriched responses
            risk_assessment = self.risk_qualifier.qualify_ict_risk(enriched_responses)
            
            self.logger.info("ICT risk assessment completed successfully")
            
            # Create auto-detected factors list
            auto_detected_factors = []
            if extracted_factors:
                auto_detected_factors = list(set(
                    factor for category in extracted_factors.values() 
                    for factor, value in category.items() if value
                ))
            
            return {
                "assessed_at": datetime.datetime.now().isoformat(),
                "responses": enriched_responses,
                "original_responses": responses,
                "auto_detected_factors": auto_detected_factors,
                "assessment_results": risk_assessment
            }
            
        except Exception as e:
            self.logger.error(f"Error in ICT risk assessment: {str(e)}", exc_info=True)
            raise
    
    def validate_onboarding_data(self, data: Dict[str, Dict[str, Any]]) -> Dict[str, Any]:
        """
        Validate vendor onboarding data.
        
        Args:
            data: Vendor onboarding data
            
        Returns:
            Dictionary with validation results
        """
        self.logger.info("Validating vendor onboarding data")
        
        try:
            validation_results = self.onboarding_validator.validate_data(data)
            
            log_level = "info" if validation_results["is_valid"] else "warning"
            getattr(self.logger, log_level)("Onboarding validation completed", validation_results)
            
            return validation_results
            
        except Exception as e:
            self.logger.error(f"Error validating onboarding data: {str(e)}", exc_info=True)
            raise
    
    def create_register_entry(self, onboarding_data: Dict[str, Dict[str, Any]], 
                             risk_assessment: Optional[Dict[str, Any]] = None,
                             contract_analysis: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Create a register entry from vendor onboarding and assessment data.
        
        Args:
            onboarding_data: Vendor onboarding data
            risk_assessment: Risk assessment results (optional)
            contract_analysis: Contract analysis results (optional)
            
        Returns:
            Dictionary with register entry data and ID
        """
        self.logger.info("Creating register entry")
        
        try:
            entry = self.register_builder.create_register_entry(
                onboarding_data, 
                risk_assessment=risk_assessment,
                contract_analysis=contract_analysis
            )
            
            # Save entry to database
            entry_id = self.register_builder.save_register_entry(entry)
            
            # Generate alerts if risk assessment or contract analysis provided
            if risk_assessment or contract_analysis:
                self.alert_engine.generate_alerts(
                    entry_id, 
                    entry, 
                    compliance_results=contract_analysis,
                    risk_assessment=risk_assessment
                )
            
            self.logger.info(f"Register entry created: {entry_id}")
            
            return {
                "entry_id": entry_id,
                "entry_data": entry
            }
            
        except Exception as e:
            self.logger.error(f"Error creating register entry: {str(e)}", exc_info=True)
            raise
    
    def export_register(self, format_type: str = "json") -> Tuple[str, bytes]:
        """
        Export the register in the specified format.
        
        Args:
            format_type: Format type ('json', 'csv', or 'excel')
            
        Returns:
            Tuple of (filename, content)
        """
        self.logger.info(f"Exporting register in {format_type} format")
        
        try:
            # Get all register entries
            entries = self.register_builder.get_all_entries()
            
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            
            if format_type.lower() == 'json':
                content = self.register_exporter.export_to_json(entries)
                filename = f"dora_register_{timestamp}.json"
                return filename, content.encode('utf-8')
                
            elif format_type.lower() == 'csv':
                content = self.register_exporter.export_to_csv(entries)
                filename = f"dora_register_{timestamp}.csv"
                return filename, content.encode('utf-8')
                
            elif format_type.lower() == 'excel':
                content = self.register_exporter.export_to_excel(entries)
                filename = f"dora_register_{timestamp}.xlsx"
                return filename, content
                
            else:
                raise ValueError(f"Unsupported format type: {format_type}")
                
        except Exception as e:
            self.logger.error(f"Error exporting register: {str(e)}", exc_info=True)
            raise
    
    def get_register_summary(self) -> Dict[str, Any]:
        """
        Get a summary of the register.
        
        Returns:
            Dictionary with register summary
        """
        self.logger.info("Generating register summary")
        
        try:
            entries = self.register_builder.get_all_entries()
            summary = self.register_exporter.generate_summary_report(entries)
            
            self.logger.info("Register summary generated successfully")
            
            return summary
            
        except Exception as e:
            self.logger.error(f"Error generating register summary: {str(e)}", exc_info=True)
            raise
    
    def get_active_alerts(self) -> List[Dict[str, Any]]:
        """
        Get active alerts.
        
        Returns:
            List of active alerts
        """
        self.logger.info("Retrieving active alerts")
        
        try:
            alerts = self.alert_engine.get_active_alerts()
            
            self.logger.info(f"Retrieved {len(alerts)} active alerts")
            
            return alerts
            
        except Exception as e:
            self.logger.error(f"Error retrieving alerts: {str(e)}", exc_info=True)
            raise
    
    def get_saved_contracts(self) -> List[Dict[str, Any]]:
        """
        Get all saved contracts.
        
        Returns:
            List of saved contracts
        """
        self.logger.info("Retrieving saved contracts")
        
        try:
            contracts = self.contract_repository.get_all_contracts()
            
            self.logger.info(f"Retrieved {len(contracts)} saved contracts")
            
            return contracts
            
        except Exception as e:
            self.logger.error(f"Error retrieving saved contracts: {str(e)}", exc_info=True)
            return []
    
    def get_contract_by_id(self, contract_id: str) -> Optional[Dict[str, Any]]:
        """
        Get a contract by ID.
        
        Args:
            contract_id: ID of the contract to retrieve
            
        Returns:
            Contract data or None if not found
        """
        self.logger.info(f"Retrieving contract with ID: {contract_id}")
        
        try:
            contract = self.contract_repository.get_contract(contract_id)
            
            if contract:
                self.logger.info(f"Contract retrieved: {contract.get('filename', 'Unknown')}")
            else:
                self.logger.warning(f"Contract not found: {contract_id}")
                
            return contract
            
        except Exception as e:
            self.logger.error(f"Error retrieving contract: {str(e)}", exc_info=True)
            return None
    
    def search_contracts(self, search_term: str) -> List[Dict[str, Any]]:
        """
        Search contracts by filename or vendor name.
        
        Args:
            search_term: Term to search for
            
        Returns:
            List of matching contracts
        """
        self.logger.info(f"Searching contracts for: {search_term}")
        
        try:
            contracts = self.contract_repository.search_contracts(search_term)
            
            self.logger.info(f"Found {len(contracts)} contracts matching: {search_term}")
            
            return contracts
            
        except Exception as e:
            self.logger.error(f"Error searching contracts: {str(e)}", exc_info=True)
            return []
    
    def delete_contract(self, contract_id: str) -> bool:
        """
        Delete a contract by ID.
        
        Args:
            contract_id: ID of the contract to delete
            
        Returns:
            True if successful, False otherwise
        """
        self.logger.info(f"Deleting contract with ID: {contract_id}")
        
        try:
            result = self.contract_repository.delete_contract(contract_id)
            
            if result:
                self.logger.info(f"Contract deleted: {contract_id}")
            else:
                self.logger.warning(f"Failed to delete contract: {contract_id}")
                
            return result
            
        except Exception as e:
            self.logger.error(f"Error deleting contract: {str(e)}", exc_info=True)
            return False
            
    def update_alert_status(self, alert_id: str, status: str) -> bool:
        """
        Update the status of an alert.
        
        Args:
            alert_id: ID of the alert to update
            status: New status ('resolved' or 'dismissed')
            
        Returns:
            True if successful, False otherwise
        """
        self.logger.info(f"Updating alert {alert_id} status to {status}")
        
        try:
            if status.lower() == 'resolved':
                result = self.alert_engine.resolve_alert(alert_id)
            elif status.lower() == 'dismissed':
                result = self.alert_engine.dismiss_alert(alert_id)
            else:
                raise ValueError(f"Invalid alert status: {status}")
            
            log_level = "info" if result else "warning"
            getattr(self.logger, log_level)(f"Alert {alert_id} status update to {status}", {"success": result})
            
            return result
            
        except Exception as e:
            self.logger.error(f"Error updating alert status: {str(e)}", exc_info=True)
            raise
    
    def process_contract_basic(self, file_content: bytes, filename: str) -> Dict[str, Any]:
        """
        Process a contract document with basic functionality (no OpenAI required).
        
        Args:
            file_content: Binary content of the uploaded file
            filename: Name of the uploaded file
            
        Returns:
            Dictionary with extraction results
        """
        self.logger.info(f"Processing contract using basic mode: {filename}")
        
        # Extract file extension
        ext = filename.split('.')[-1].lower()
        
        # Basic extraction without AI
        extracted_text = ""
        
        try:
            # Process PDF
            if ext == 'pdf':
                import pdfplumber
                
                with pdfplumber.open(io.BytesIO(file_content)) as pdf:
                    for page in pdf.pages:
                        extracted_text += page.extract_text() or ""
            
            # Process DOCX
            elif ext == 'docx':
                import docx
                
                doc = docx.Document(io.BytesIO(file_content))
                for para in doc.paragraphs:
                    extracted_text += para.text + "\n"
            
            else:
                return {
                    "error": f"Unsupported file format: {ext}",
                    "status": "error"
                }
            
            # Basic parsing with simple keyword search
            clauses = {
                "exit_strategy": [],
                "sub_outsourcing": [],
                "service_levels": [],
                "audit_rights": [],
                "data_protection": []
            }
            
            # Simple keyword-based extraction
            paragraphs = extracted_text.split('\n\n')
            
            for i, para in enumerate(paragraphs):
                para_lower = para.lower()
                
                # Exit strategy
                if any(keyword in para_lower for keyword in ["exit", "termination", "transition"]):
                    clauses["exit_strategy"].append({
                        "text": para,
                        "source": f"Page {i//10 + 1}",
                        "dora_requirements": ["Exit planning", "Transition arrangements"]
                    })
                
                # Sub-outsourcing
                if any(keyword in para_lower for keyword in ["subcontract", "sub-contract", "subprovider", "third party"]):
                    clauses["sub_outsourcing"].append({
                        "text": para,
                        "source": f"Page {i//10 + 1}",
                        "dora_requirements": ["Sub-outsourcing approval", "Chain monitoring"]
                    })
                
                # Service levels
                if any(keyword in para_lower for keyword in ["sla", "service level", "performance"]):
                    clauses["service_levels"].append({
                        "text": para,
                        "source": f"Page {i//10 + 1}",
                        "dora_requirements": ["Service metrics", "Performance monitoring"]
                    })
                
                # Audit rights
                if any(keyword in para_lower for keyword in ["audit", "inspect", "examination"]):
                    clauses["audit_rights"].append({
                        "text": para,
                        "source": f"Page {i//10 + 1}",
                        "dora_requirements": ["Audit rights", "Information access"]
                    })
                
                # Data protection
                if any(keyword in para_lower for keyword in ["data", "privacy", "gdpr", "personal information"]):
                    clauses["data_protection"].append({
                        "text": para,
                        "source": f"Page {i//10 + 1}",
                        "dora_requirements": ["Data location", "Processing restrictions"]
                    })
            
            # Generate basic compliance assessment
            compliance_results = {
                "overall_compliance": 0.5,  # Default to 50% without AI analysis
                "article_compliance": {
                    "DORA Article 28": {"compliance_score": 0.5},
                    "DORA Article 29": {"compliance_score": 0.5},
                    "DORA Article 30": {"compliance_score": 0.5}
                },
                "gaps": [
                    {"article": "DORA Article 30", "requirement": "Cannot perform detailed gap analysis without AI capabilities"}
                ],
                "recommendations": [
                    {"article": "General", "recommendation": "Enable OpenAI API for full contract analysis capabilities"}
                ]
            }
            
            # Count found clauses to adjust compliance score
            found_clauses = sum(1 for category in clauses.values() if len(category) > 0)
            if found_clauses >= 4:
                compliance_results["overall_compliance"] = 0.7
            elif found_clauses <= 1:
                compliance_results["overall_compliance"] = 0.3
                
            # Return results
            return {
                "filename": filename,
                "processed_at": datetime.datetime.now().isoformat(),
                "extracted_text": extracted_text[:1000] + "...",  # Truncated for UI display
                "extracted_clauses": clauses,
                "compliance_results": compliance_results,
                "clause_evaluation": {
                    category: {
                        "fulfilled_requirements": [],
                        "gaps": ["Full evaluation requires OpenAI API"]
                    } for category in clauses
                },
                "status": "success"
            }
        
        except Exception as e:
            self.logger.error(f"Error in basic contract processing: {str(e)}")
            return {
                "error": f"Error processing document: {str(e)}",
                "status": "error"
            }

# Create global instance of the agent
dora_agent = DORAAssessmentAgent()
