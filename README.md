# Sprint 3 — Leitura de Placas Multiabordagem (Projeto Forzy)

Challenge Sprint 3 — Visão Computacional · Tecnólogo em Inteligência Artificial · FIAP

**Grupo "CodeX"**

| RM | Integrante |
|---|---|
| 552574 | Bruno Fernandes Nascimento |
| 565260 | Edgar Lódula de Assis |
| 565293 | Guilherme Gama |
| 563632 | Igor Thiago Nakajima |
| 566325 | Júlia Aben-Athar |

---

## O que é este projeto

Continuação do protótipo de OCR construído na Sprint 2 para leitura de placas de identificação de
ativos industriais (motores, bombas, refiners) da fábrica de papel do projeto Forzy, usando o
dataset público [`kahua-ml/nameplate1`](https://huggingface.co/datasets/kahua-ml/nameplate1)
(HuggingFace).

Na Sprint 2 apenas o **EasyOCR** foi testado, em 10 imagens, medindo só a confiança do OCR (73,0%
de taxa de validade), sem gabarito formal. Esta Sprint amplia o protótipo em três frentes:

1. **Três abordagens comparadas lado a lado** — EasyOCR, Tesseract OCR e um modelo multimodal
   (GPT-4o-mini) — todas extraindo os mesmos 5 campos: `codigo_ativo`, `fabricante`, `modelo`,
   `numero_serie`, `potencia`.
2. **Conjunto de teste dedicado de 30 imagens** (índices 10–39 do dataset, diferentes das 10 já
   usadas de demonstração na Sprint 2), com **gabarito definido manualmente** por inspeção direta
   de cada imagem, sem consultar as saídas dos modelos.
3. **Métricas formais de acurácia** — exact-match por campo e CER (Character Error Rate) — que
   não existiam na Sprint 2.

## Resultado

| Abordagem | Acurácia média geral | CER médio |
|---|---|---|
| EasyOCR + regex | 82,7% | 0,253 |
| Tesseract + regex | 80,0% | 0,295 |
| **GPT-4o-mini** | **85,3%** | **0,240** |

Esse número geral é inflado por 21 das 30 imagens terem gabarito `"N/A"` em tudo (placas ilegíveis
ou fotos do equipamento inteiro) — acertar "não há nada pra ler" conta como acerto igual pras três
abordagens. Filtrando **apenas os casos em que o gabarito tem um valor real**, a diferença fica
clara:

| Campo (só onde há valor no gabarito) | EasyOCR | Tesseract | GPT-4o |
|---|---|---|---|
| codigo_ativo (8 imagens) | 25,0% | 12,5% | **75,0%** |
| fabricante (9 imagens) | 33,3% | 0,0% | 33,3% |
| modelo (4 imagens) | 0,0% | 0,0% | **50,0%** |
| numero_serie (4 imagens) | 0,0% | 0,0% | **75,0%** |
| potencia (6 imagens) | 0,0% | 0,0% | **50,0%** |

O GPT-4o-mini domina nos campos que exigem interpretar o layout da placa, não só casar um padrão de
texto — mas também **alucina** em placas ilegíveis, inventando valores plausíveis quando deveria
responder `"N/A"`. Análise completa, exemplos concretos e limitações no
[relatório técnico](relatorio_tecnico_sprint3.md).

## Estrutura do repositório

```
Sprint3_Multiabordagem_Forzy.ipynb   Notebook principal — as 3 abordagens, ponta a ponta
relatorio_tecnico_sprint3.md         Relatório técnico completo (metodologia, resultados, análise)
apresentacao_sprint3.html            Slides da apresentação (abrir direto no navegador)
gabarito_30_imagens.csv              Gabarito manual das 30 imagens de teste
resultados_brutos_sprint3.csv        Saída bruta das 3 abordagens para as 30 imagens
acuracia_sprint3.csv                 Acurácia por campo e por abordagem
graficos_comparativos_sprint3.png    Gráficos comparativos gerados pelo notebook
requirements.txt                     Dependências Python
```

## Como rodar

```bash
python -m venv venv
venv\Scripts\pip install -r requirements.txt          # Windows
```

- **Tesseract OCR** é um binário do sistema, não vai pelo pip — instale separadamente
  ([UB-Mannheim build](https://github.com/UB-Mannheim/tesseract/wiki) no Windows) e ajuste o
  caminho em `pytesseract.pytesseract.tesseract_cmd` no notebook, se necessário.
- **`OPENAI_API_KEY`** — crie um arquivo `.env` na raiz do projeto com:
  ```
  OPENAI_API_KEY=sk-...
  ```
  (o notebook carrega essa variável via `python-dotenv`; a abordagem GPT-4o-mini só roda com ela
  configurada — EasyOCR e Tesseract funcionam sem chave nenhuma).

Depois é só abrir `Sprint3_Multiabordagem_Forzy.ipynb` e rodar as células em ordem.

## Próximos passos (Sprint 4)

- Detecção automática da região da placa antes do OCR (YOLO), atacando as falhas totais causadas
  por fotos do equipamento inteiro.
- Pipeline híbrido: regex para campos já bem resolvidos + GPT-4o-mini só para campos ambíguos,
  reduzindo custo de API.
- Segundo passo de validação para reduzir a taxa de alucinação do modelo multimodal.
- Integração com a planta visual e a telemetria dos sensores Pepperl+Fuchs desenhadas na Sprint 2.
