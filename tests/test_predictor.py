import os
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from backend.database.database import Base
from backend.database.models import Transition
from backend.predictor.markov_predictor import MarkovPredictor

@pytest.fixture
def db_session():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(bind=engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    yield session
    session.close()

def test_markov_predictor(db_session):
    predictor = MarkovPredictor(threshold=0.70)
    
    file_a = "/data/file_a.txt"
    file_b = "/data/file_b.txt"
    file_c = "/data/file_c.txt"
    
    # Record A -> B (8 times)
    for _ in range(8):
        predictor.record_transition(db_session, file_a, file_b)
        
    # Record A -> C (2 times)
    for _ in range(2):
        predictor.record_transition(db_session, file_a, file_c)
        
    # P(B|A) = 8 / 10 = 0.80 >= 0.70 (Triggers prediction)
    # P(C|A) = 2 / 10 = 0.20 < 0.70
    predictions = predictor.get_predictions(db_session, file_a)
    assert len(predictions) == 1
    predicted_file, prob = predictions[0]
    assert predicted_file == os.path.abspath(file_b)
    assert prob == 0.80
