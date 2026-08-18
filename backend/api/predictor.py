from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from backend.database.database import get_db
from backend.predictor.markov_predictor import markov_predictor

router = APIRouter(prefix="/predictor", tags=["Predictive Preloader"])

@router.get("/transitions")
def get_transitions(db: Session = Depends(get_db)):
    """
    Returns state transition counts and calculated prediction probabilities P(B|A).
    """
    return {
        "threshold": markov_predictor.threshold,
        "transitions": markov_predictor.get_all_transitions(db)
    }

@router.get("/predict")
def predict_next_file(
    filepath: str = Query(..., description="Source file path to predict next file access for"),
    db: Session = Depends(get_db)
):
    """
    Returns candidate files predicted to be accessed next with P(B|A) >= threshold.
    """
    predictions = markov_predictor.get_predictions(db, filepath)
    return {
        "source_file": filepath,
        "threshold": markov_predictor.threshold,
        "predictions": [
            {"predicted_file": path, "probability": prob}
            for path, prob in predictions
        ]
    }
