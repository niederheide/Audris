#!/usr/bin/env python3
"""
Test script specifically for the ML risk assessment model.
This simplified test focuses on validating the ML risk scoring functionality.
"""

import os
import sys
import json
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("ml_test")

# Add app directory to path
sys.path.append(os.path.abspath("."))

# Import ML risk scorer
try:
    from app.risk.ml_risk_scorer import ml_risk_scorer
    logger.info("Successfully imported ML risk scorer")
except Exception as e:
    logger.error(f"Error importing ML risk scorer: {e}")
    sys.exit(1)

def test_training():
    """Test ML model training functionality."""
    print("\n=== Testing ML Model Training ===\n")
    
    # Check if model is already trained
    if ml_risk_scorer.is_model_trained():
        print("ML model is already trained")
    else:
        print("ML model is not trained")
    
    # Generate synthetic training data
    print("\nGenerating synthetic training data...")
    training_data = ml_risk_scorer.generate_synthetic_training_data(n_samples=100)
    print(f"Generated {len(training_data)} synthetic training samples")
    
    # Train the model
    print("\nTraining ML model...")
    results = ml_risk_scorer.train(training_data)
    
    # Check training results
    if results["status"] == "success":
        print(f"Model trained successfully")
        print(f"Training accuracy: {results.get('accuracy', 0):.4f}")
        
        # Save metrics for reference
        with open('ml_training_metrics.json', 'w') as f:
            json.dump(results, f, indent=2)
            print("Training metrics saved to ml_training_metrics.json")
    else:
        print(f"Model training failed: {results.get('message', 'Unknown error')}")

def test_prediction():
    """Test ML model prediction functionality."""
    print("\n=== Testing ML Model Prediction ===\n")
    
    # Check if model is trained
    if not ml_risk_scorer.is_model_trained():
        print("ML model is not trained, skipping prediction test")
        return
    
    # Create sample risk assessment responses
    test_responses = {
        "criticality": {
            "Supports critical banking function": True,
            "Connected to core banking systems": True,
            "Processes sensitive customer data": True,
            "Required for financial reporting": False,
            "Required for regulatory compliance": True
        },
        "outsourcing_chain": {
            "Multiple sub-processors involved": True,
            "International transfers required": True,
            "Complex contractual arrangements": False,
            "Limited visibility of chain": False,
            "Cross-border data flows": True
        },
        "service_type": {
            "Core banking functionality": True,
            "Cloud service": True,
            "Data processing service": False,
            "Analytics service": False,
            "Operational support": True
        },
        "data_sensitivity": {
            "Contains PII of EU citizens": True,
            "Includes financial transaction data": True,
            "Contains authentication credentials": True,
            "Includes strategic business information": False,
            "Contains regulated financial data": True
        }
    }
    
    # Run prediction
    print("Running risk prediction on test data...")
    prediction = ml_risk_scorer.predict_risk(test_responses)
    
    # Print prediction results
    print("\nPrediction results:")
    print(f"Risk classification: {prediction.get('risk_classification', 'Unknown')}")
    print(f"Risk score: {prediction.get('risk_score', 0)}")
    print(f"DORA critical: {'Yes' if prediction.get('dora_critical', False) else 'No'}")
    print(f"Confidence: {prediction.get('confidence', 0):.2f}")
    
    # Print component scores
    component_scores = prediction.get("component_scores", {})
    print("\nComponent scores:")
    for component, score in component_scores.items():
        print(f"- {component}: {score}")
    
    # Print class probabilities if available
    probabilities = prediction.get("probabilities", {})
    if probabilities:
        print("\nClass probabilities:")
        for risk_class, prob in probabilities.items():
            print(f"- {risk_class}: {prob:.2f}")

if __name__ == "__main__":
    print("Starting ML Risk Model Tests...\n")
    
    # Run tests
    test_training()
    test_prediction()
    
    print("\nML Risk Model Tests completed")