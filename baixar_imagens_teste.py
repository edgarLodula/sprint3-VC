import os
from datasets import load_dataset

dataset = load_dataset("kahua-ml/nameplate1")

os.makedirs("imagens_teste_originais", exist_ok=True)

INICIO_TESTE = 10
N_TESTE = 30

caminhos_teste = []
for offset in range(N_TESTE):
    idx = INICIO_TESTE + offset
    img = dataset["train"][idx]["image"]
    caminho = f"imagens_teste_originais/placa_teste_{offset+1:02d}.jpg"
    img.convert("RGB").save(caminho)
    caminhos_teste.append(caminho)
    

