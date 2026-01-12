# app.py — hardened lazy-loading to eliminate 500s and surface clear errors

import os
import logging
import numpy as np
import tensorflow as tf
from flask import Flask, request, jsonify
from flask_cors import CORS
from transformers import BertTokenizer, TFBertForSequenceClassification

# --- SETUP & CONFIGURATION ---
app = Flask(__name__)
CORS(app)  # Allow local dev frontend
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'
logging.basicConfig(level=logging.INFO)

# --- GLOBAL MODEL VARIABLES ---
text_tokenizer = None
text_model = None
face_model = None
voice_model = None
meta_model = None

# --- MODEL PATHS (ensure these exist) ---
HF_TEXT_DIR = os.environ.get("HF_TEXT_DIR", "bert_text_model")
FACE_MODEL_PATH = os.environ.get("FACE_MODEL_PATH", "trisense_face_model_tf")
VOICE_MODEL_PATH = os.environ.get("VOICE_MODEL_PATH", "trisense_voice_model_tf")
META_MODEL_PATH = os.environ.get("META_MODEL_PATH", "trisense_meta_model.h5")

# --- LAZY LOADERS ---
def load_text_models():
    global text_tokenizer, text_model
    if text_tokenizer is not None and text_model is not None:
        return
    logging.info("Loading text tokenizer and model from: %s", HF_TEXT_DIR)
    try:
        text_tokenizer = BertTokenizer.from_pretrained(HF_TEXT_DIR)
        text_model = TFBertForSequenceClassification.from_pretrained(HF_TEXT_DIR)
        logging.info("Text models loaded.")
    except Exception as e:
        logging.exception("Failed to load text models from %s: %s", HF_TEXT_DIR, e)
        raise

def load_face_model():
    global face_model
    if face_model is not None:
        return
    logging.info("Loading face model from: %s", FACE_MODEL_PATH)
    try:
        face_model = tf.keras.models.load_model(FACE_MODEL_PATH)
        logging.info("Face model loaded.")
    except Exception as e:
        logging.exception("Failed to load face model from %s: %s", FACE_MODEL_PATH, e)
        raise

def load_voice_model():
    global voice_model
    if voice_model is not None:
        return
    logging.info("Loading voice model from: %s", VOICE_MODEL_PATH)
    try:
        voice_model = tf.keras.models.load_model(VOICE_MODEL_PATH)
        logging.info("Voice model loaded.")
    except Exception as e:
        logging.exception("Failed to load voice model from %s: %s", VOICE_MODEL_PATH, e)
        raise

def load_meta_model():
    global meta_model
    if meta_model is not None:
        return
    logging.info("Loading meta model from: %s", META_MODEL_PATH)
    try:
        meta_model = tf.keras.models.load_model(META_MODEL_PATH)
        logging.info("Meta model loaded.")
    except Exception as e:
        logging.exception("Failed to load meta model from %s: %s", META_MODEL_PATH, e)
        raise

# --- HEALTH & READINESS ---
@app.route("/health", methods=["GET"])
def health():
    status = {
        "text_ready": text_tokenizer is not None and text_model is not None,
        "face_ready": face_model is not None,
        "voice_ready": voice_model is not None,
        "meta_ready": meta_model is not None,
    }
    return jsonify({"status": status}), 200

@app.route("/ready", methods=["GET"])
def ready():
    # Try loading quickly to report readiness
    try:
        load_text_models()
        load_meta_model()
    except Exception:
        pass
    return jsonify({
        "ready": all([
            text_tokenizer is not None and text_model is not None,
            meta_model is not None
        ])
    }), 200

# --- ANALYZE ENDPOINT (example) ---
@app.route("/api/analyze", methods=["POST"])
def analyze():
    try:
        data = request.get_json(force=True, silent=False)
        if not data or "text" not in data:
            return jsonify({"error": "Missing 'text' in request body"}), 400

        # Ensure required models are loaded
        try:
            load_text_models()
            load_meta_model()
        except Exception as e:
            # Model load failure: do not 500 blindly; tell the client clearly
            return jsonify({
                "error": "Model load failed",
                "details": str(e)
            }), 503

        text_input = data["text"]
        # Tokenize
        inputs = text_tokenizer(
            text_input,
            return_tensors="tf",
            truncation=True,
            padding="max_length",
            max_length=128
        )
        # Predict
        outputs = text_model(inputs)
        logits = outputs.logits.numpy().tolist()

        # Example meta aggregation (dummy)
        result = {
            "logits": logits,
            "anxiety_score": float(np.clip(np.mean(outputs.logits.numpy()), 0.0, 1.0))
        }
        return jsonify(result), 200

    except Exception as e:
        logging.exception("Unhandled error in /api/analyze: %s", e)
        # Return a controlled JSON error instead of bare 500
        return jsonify({
            "error": "Internal server error",
            "message": str(e)
        }), 500

# --- MAIN ---
if __name__ == "__main__":
    # Avoid loading all models at startup; keep memory and boot time small
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)), debug=True)
