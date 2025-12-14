import joblib
from pathlib import Path
import warnings
warnings.filterwarnings('ignore', category=UserWarning)

SCRIPT_DIR = Path(__file__).parent

MODEL_PATH = SCRIPT_DIR / 'models/penguin_classifier.pkl'

model = joblib.load(MODEL_PATH)
print(type(model))  # Verify the model is loaded correctly