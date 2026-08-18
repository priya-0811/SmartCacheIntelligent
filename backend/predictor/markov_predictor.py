import os
import logging
from typing import Dict, List, Tuple, Optional
from sqlalchemy.orm import Session
from backend.database.models import Transition
from backend.config import settings

logger = logging.getLogger("smartcache.predictor")

class MarkovPredictor:
    """
    First-order Markov Chain Predictor for access sequence prediction.
    Tracks state transitions A -> B and predicts candidate files for preloading.
    """
    def __init__(self, threshold: float = settings.PRELOAD_THRESHOLD):
        self.threshold = threshold

    def set_threshold(self, new_threshold: float):
        self.threshold = new_threshold

    def record_transition(self, db: Session, prev_filepath: str, curr_filepath: str):
        """
        Increments transition count for (prev_filepath -> curr_filepath) in DB.
        """
        if not prev_filepath or prev_filepath == curr_filepath:
            return

        prev_path = os.path.abspath(prev_filepath)
        curr_path = os.path.abspath(curr_filepath)

        transition = db.query(Transition).filter_by(
            previous_file=prev_path,
            next_file=curr_path
        ).first()

        if transition:
            transition.transition_count += 1
        else:
            transition = Transition(
                previous_file=prev_path,
                next_file=curr_path,
                transition_count=1
            )
            db.add(transition)

        db.commit()

    def get_predictions(self, db: Session, current_filepath: str) -> List[Tuple[str, float]]:
        """
        Returns list of (predicted_filepath, probability) for current_filepath where P > threshold.
        P(B|A) = Transition(A->B) / TotalTransitions(A)
        """
        curr_path = os.path.abspath(current_filepath)
        transitions = db.query(Transition).filter_by(previous_file=curr_path).all()

        if not transitions:
            return []

        total_transitions = sum(t.transition_count for t in transitions)
        if total_transitions == 0:
            return []

        predictions = []
        for t in transitions:
            prob = t.transition_count / total_transitions
            if prob >= self.threshold:
                predictions.append((t.next_file, round(prob, 4)))

        # Sort by highest probability first
        predictions.sort(key=lambda x: x[1], reverse=True)
        return predictions

    def get_all_transitions(self, db: Session) -> List[Dict[str, str | int | float]]:
        """
        Returns detailed transition statistics table.
        """
        transitions = db.query(Transition).all()
        
        # Calculate total transitions per source file
        totals: Dict[str, int] = {}
        for t in transitions:
            totals[t.previous_file] = totals.get(t.previous_file, 0) + t.transition_count

        result = []
        for t in transitions:
            total_src = totals.get(t.previous_file, 1)
            prob = t.transition_count / total_src if total_src > 0 else 0.0
            result.append({
                "id": t.id,
                "previous_file": t.previous_file,
                "next_file": t.next_file,
                "transition_count": t.transition_count,
                "total_source_transitions": total_src,
                "probability": round(prob, 4)
            })

        return result

# Global predictor instance
markov_predictor = MarkovPredictor()
