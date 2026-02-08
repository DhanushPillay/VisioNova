# Notebooks

Jupyter notebooks for training and experimentation.

## Files

- **DeBERTa_Training_Notebook.ipynb** - Local training notebook for DeBERTa text classifier
- **VisioNova_Colab_Training.ipynb** - Google Colab version for GPU training

## Usage

### Local Training
```powershell
# Install Jupyter
pip install jupyter notebook

# Launch notebook
jupyter notebook notebooks/DeBERTa_Training_Notebook.ipynb
```

### Google Colab Training
1. Upload `VisioNova_Colab_Training.ipynb` to Google Colab
2. Enable GPU runtime (Runtime → Change runtime type → T4 GPU)
3. Run all cells to train model
4. Download trained model to `backend/text_detector/model/`
