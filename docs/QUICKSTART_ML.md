# Quick Start: ML-Enhanced VisioNova

## Activate ML Environment (every session)
```powershell
cd "E:\Personal Projects\VisioNova"
.venv310\Scripts\Activate.ps1
```

## Start Server
```powershell
python backend/app.py
```

## Verify GPU is Working
```powershell
python -c "import torch; print('GPU:', torch.cuda.get_device_name(0) if torch.cuda.is_available() else 'CPU only')"
```

## Expected Startup Logs
```
INFO:image_detector.ml_detector:Loading Deepfake detector on cuda...
INFO:image_detector.ml_detector:Deepfake detector loaded successfully
INFO:image_detector.ml_detector:Loading UniversalFakeDetect (CLIP) on cuda...
INFO:image_detector.ml_detector:UniversalFakeDetect loaded successfully
INFO:image_detector.ensemble_detector:EnsembleDetector initialized (GPU: True, ML models: True)
```

## Test with Sample Image
Upload any AI-generated image to: `http://localhost:5000`

Expected result:
- **AI Probability**: 85-99%
- **Confidence**: 90-95%
- **Models Used**: dima806 (30%) + CLIP (30%) + Statistical (20%) + Others (20%)

## Switch Back to Regular Environment
```powershell
deactivate  # Exit .venv310
.venv\Scripts\Activate.ps1  # Activate regular Python 3.13
```

---

**Remember**: Always use `.venv310` when running the backend server for GPU acceleration!
