from functools import lru_cache
from pathlib import Path
import torch
from torchvision import models, transforms
from PIL import Image
from app.config import LABELS


@lru_cache(maxsize=1)
def get_model():
    # Le fichier historique contient les poids d'un MobileNet V3 Small.
    model = models.mobilenet_v3_small(weights=None)
    model.classifier[3] = torch.nn.Linear(1024, len(LABELS))
    weights_path = Path(__file__).with_name("vgg16_finetuned.pth")
    model.load_state_dict(torch.load(weights_path, map_location="cpu", weights_only=True))
    model.eval()
    return model


def predict_image(file_path):
    transform = transforms.Compose([
        transforms.Resize((128, 128)),
        transforms.ToTensor(),
        transforms.Normalize(mean=[0.5, 0.5, 0.5], std=[0.5, 0.5, 0.5]),
    ])
    with Image.open(file_path) as image:
        tensor = transform(image.convert("RGB")).unsqueeze(0)
    with torch.inference_mode():
        output = get_model()(tensor)
    return LABELS[output.argmax(1).item()]
