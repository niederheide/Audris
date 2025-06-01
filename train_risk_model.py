"""
Training script for the DORA risk assessment ML model.

This script generates synthetic training data and trains the initial 
machine learning model for risk assessment.
"""

import os
import json
import logging
from app.risk.ml_risk_scorer import ml_risk_scorer

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("dora_assessment.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("dora_assessment")

def train_model():
    """Generate synthetic training data and train the model."""
    logger.info("Starting risk assessment model training")
    
    # Create models directory if it doesn't exist
    os.makedirs('models', exist_ok=True)
    
    # Check if model is already trained
    if ml_risk_scorer.is_model_trained():
        logger.info("Model already trained. To retrain, delete files in the 'models' directory first.")
        return
    
    # Generate synthetic training data
    logger.info("Generating synthetic training data")
    training_data = ml_risk_scorer.generate_synthetic_training_data(n_samples=200)
    
    # Save training data for reference
    with open('models/training_data.json', 'w') as f:
        json.dump(training_data, f, indent=2)
    
    # Train the model
    logger.info("Training risk assessment model")
    results = ml_risk_scorer.train(training_data)
    
    # Log and save results
    if results["status"] == "success":
        logger.info(f"Model trained successfully. Accuracy: {results['accuracy']:.4f}")
        
        # Save metrics for reference
        with open('models/training_metrics.json', 'w') as f:
            json.dump(results, f, indent=2)
    else:
        logger.error(f"Model training failed: {results['message']}")

if __name__ == "__main__":
    train_model()