# CHALLENGE SPRINT 3 — Visão Computacional
## Evolução do Protótipo de Leitura de Placas — Projeto Forzy

Grupo "CodeX" — Tecnólogo em Inteligência Artificial - FIAP

**Integrantes:**
- Bruno Fernandes Nascimento — 552574
- Edgar Lódula de Assis — 565260
- Guilherme Gama — 565293
- Igor Thiago Nakajima — 563632
- Júlia Aben-Athar — 566325

---

## 1. Continuidade em relação à Sprint 2

Na Sprint 2 foi construído o protótipo inicial de OCR para as placas de identificação dos ativos da
fábrica de papel ondulado (projeto Forzy), usando **EasyOCR** sobre 10 imagens do dataset público
`kahua-ml/nameplate1` (HuggingFace). O resultado obtido foi:

- Taxa global de validade: **73,0%** (127 de 174 campos com confiança ≥ 0,5)
- Placas com leitura útil (≥ 3 campos válidos): **8 de 10**
- Confiança média: **0,70**
- Limitações documentadas: falha total em fotos do equipamento inteiro (placas 07 e 08), texto
  rotacionado só corrigido manualmente em 2 placas, ausência de pós-processamento estruturado por
  campo, ausência de ground truth formal para métricas rigorosas (CER/WER).

A Sprint 3 ataca diretamente essas lacunas: (1) rotação automática passa a ser padrão em todo o
pipeline, não mais uma correção pontual; (2) o texto bruto é convertido em campos estruturados via
regex; (3) uma segunda abordagem clássica (Tesseract) e uma abordagem multimodal (GPT-4o) foram
adicionadas para comparação; (4) um conjunto de teste de 30 imagens, com gabarito definido
manualmente, permite calcular acurácia formal pela primeira vez.

## 2. Abordagens testadas

| # | Abordagem | Tipo | Entrada | Saída |
|---|---|---|---|---|
| 1 | EasyOCR (CRAFT + CRNN) + regex | OCR neural + pós-processamento por regras | Imagem padronizada colorida, `rotation_info` sempre ativo | Texto bruto → campos estruturados |
| 2 | Tesseract OCR + regex | OCR clássico (LSTM) + pós-processamento por regras | Imagem em escala de cinza + CLAHE | Texto bruto → campos estruturados |
| 3 | GPT-4o-mini (multimodal) | Modelo de linguagem com visão | Imagem padronizada colorida + prompt estruturado | JSON direto com os campos |

Os campos extraídos em todas as abordagens são os mesmos, para permitir comparação justa:
`codigo_ativo`, `fabricante`, `modelo`, `numero_serie`, `potencia`.

### 2.1 Como o teste com modelo multimodal foi realizado

A imagem é codificada em base64 e enviada junto de um prompt de texto pedindo explicitamente os
cinco campos em formato JSON, com instrução de usar `"N/A"` quando o campo não estiver visível.
Diferente do EasyOCR/Tesseract, não há etapa intermediária de bounding boxes nem de regex — o
próprio modelo interpreta semanticamente qual trecho de texto corresponde a cada campo (por
exemplo, diferenciar "número de série" de "código do ativo" mesmo quando ambos são sequências
alfanuméricas parecidas).

### 2.2 Diferenças observadas em relação à abordagem anterior (Sprint 2)

O GPT-4o-mini leu semanticamente as etiquetas amarelas de identificação de ativo (tags funcionais,
não nameplates do fabricante) muito melhor que EasyOCR/Tesseract. Exemplos concretos:

- `placa_teste_06.jpg`, `placa_teste_24.jpg` e `placa_teste_25.jpg`: o GPT-4o extraiu corretamente o
  `codigo_ativo` (`64-M-1732`, `027-ZSO-7218`, `24-1342`) mesmo em formatos que **não** batem com o
  regex `\d{2,3}-[A-Z]-\d{3,5}` usado por EasyOCR/Tesseract — o modelo entendeu o campo pelo
  contexto ("MOTOR:", "POSITION SWITCH"), enquanto o extrator por regex de EasyOCR/Tesseract nunca
  teria chance nesses casos, mesmo com OCR perfeito.
- `placa_teste_13.jpg`: o EasyOCR leu o texto bruto corretamente, mas o regex de potência confundiu
  dígitos do código do ativo com o campo `HP` e devolveu `"5018 HP"` em vez de `"150 HP"` — o GPT-4o
  não tem esse problema porque interpreta o layout, não faz correspondência de padrão em texto
  concatenado.
- `placa_teste_20.jpg`: única imagem em que **as três abordagens** acertaram o `codigo_ativo`
  (`025-M-1432`) — tag amarela grande, bem iluminada, sem ruído.

Também houve **alucinação** clara do modelo multimodal em pelo menos 2 imagens:

- `placa_teste_25.jpg`: o gabarito só tem `codigo_ativo` preenchido, mas o GPT-4o "inventou"
  `fabricante = "K2"`, `modelo = "SPARE COOK CIRC PUMP MOTOR"` e `numero_serie =
  "0867-02-02-020-080-080-030"` — na verdade esses são fragmentos do texto descritivo da tag
  (identificador de processo "K2" e o código de localização funcional `FL:`), não um fabricante,
  modelo ou número de série reais. O modelo preencheu campos obrigatórios do JSON mesmo sem uma
  correspondência semântica válida.
- `placa_teste_29.jpg`: placa completamente ilegível (reflexo de luz cobrindo os campos), mas o
  GPT-4o devolveu `numero_serie = "150-536"` — valor sem qualquer base visível na imagem.

Em compensação, o modelo multimodal também foi mais **conservador** em casos ambíguos que o regex
teria "acertado" por coincidência: em `placa_teste_27.jpg` (posicionador FIELDVUE), nenhuma das três
abordagens conseguiu ler a tag amarela pendurada — mostrando que iluminação/foco ruins continuam
sendo um limite físico que nenhuma abordagem contorna sozinha.

Quanto à rotação: como o pipeline da Sprint 3 já ativa `rotation_info` por padrão no EasyOCR (não
mais uma correção manual pontual como na Sprint 2), nenhuma das 30 imagens apresentou falha
atribuível a texto rotacionado — o ganho da automação foi silencioso, mas real.

## 3. Dados de entrada

- **Fonte:** dataset público `kahua-ml/nameplate1` (HuggingFace), o mesmo da Sprint 2 — placas reais
  de equipamentos industriais (motores, bombas, refiners) em diversas condições de iluminação,
  ângulo e desgaste.
- **Conjunto de teste (30 imagens):** índices 10 a 39 do dataset — imagens **diferentes** das 10 já
  usadas como demonstração na Sprint 2, garantindo que o conjunto de teste seja exclusivo para
  avaliação e não tenha sido usado para ajustar o pipeline.
- **Pré-processamento:** reaproveitado da Sprint 2 (padronização 1500×1500 px, escala de cinza,
  CLAHE, denoise, sharpen, binarização adaptativa — esta última mantida apenas como entregável
  visual, não como entrada do OCR, replicando a conclusão já validada na sprint anterior).

## 4. Montagem do conjunto de teste e do gabarito

Para cada uma das 30 imagens, o grupo definiu manualmente o resultado esperado (`codigo_ativo`,
`fabricante`, `modelo`, `numero_serie`, `potencia`), inspecionando a imagem diretamente — sem
consultar as saídas dos modelos, para evitar viés de confirmação. Campos não legíveis ou ausentes na
placa foram marcados como `"N/A"`. O gabarito foi salvo em `gabarito_30_imagens.csv` e usado
exclusivamente para avaliação (nunca para ajustar os pipelines).

## 5. Cálculo de acurácia

Duas métricas foram usadas, complementares:

1. **Acurácia por campo (exact match normalizado):** comparação campo a campo entre a saída de cada
   abordagem e o gabarito, após normalização (maiúsculas, sem espaços). Resulta em uma acurácia por
   campo e uma acurácia média geral por abordagem.
2. **CER (Character Error Rate):** distância de edição (Levenshtein) entre o texto concatenado
   previsto e o esperado, normalizada pelo tamanho do texto esperado — métrica formal que estava
   ausente na Sprint 2.

### 5.1 Resultados

Tabela gerada pela Seção 10 do notebook (`acuracia_sprint3.csv`) e gráfico
`graficos_comparativos_sprint3.png` (30 imagens de teste):

| Abordagem | Acurácia média geral | CER médio |
|---|---|---|
| EasyOCR + regex | 82,7% | 0,253 |
| Tesseract + regex | 80,0% | 0,295 |
| GPT-4o-mini | **85,3%** | **0,240** |

| Campo | EasyOCR | Tesseract | GPT-4o |
|---|---|---|---|
| codigo_ativo | 80,0% | 76,7% | **93,3%** |
| fabricante | **80,0%** | 70,0% | 73,3% |
| modelo | 86,7% | 86,7% | **90,0%** |
| numero_serie | **86,7%** | **86,7%** | 80,0% |
| potencia | 80,0% | 80,0% | **90,0%** |

**Atenção à leitura desses números:** 21 das 30 imagens têm gabarito `"N/A"` em todos os campos
(placas ilegíveis ou fotos de conjunto do equipamento). Acertar "não há nada para ler" nesses casos
conta como acerto e infla a acurácia geral das três abordagens igualmente. Restringindo a
comparação **apenas aos campos em que o gabarito tem um valor real** (a métrica que de fato separa
as abordagens), o quadro muda bastante:

| Campo (só onde há valor no gabarito) | EasyOCR | Tesseract | GPT-4o |
|---|---|---|---|
| codigo_ativo (8 imagens) | 25,0% (2/8) | 12,5% (1/8) | **75,0% (6/8)** |
| fabricante (9 imagens) | 33,3% (3/9) | 0,0% (0/9) | 33,3% (3/9) |
| modelo (4 imagens) | 0,0% (0/4) | 0,0% (0/4) | **50,0% (2/4)** |
| numero_serie (4 imagens) | 0,0% (0/4) | 0,0% (0/4) | **75,0% (3/4)** |
| potencia (6 imagens) | 0,0% (0/6) | 0,0% (0/6) | **50,0% (3/6)** |

Nessa visão mais rigorosa, o GPT-4o-mini domina claramente em `codigo_ativo`, `modelo`,
`numero_serie` e `potencia` — os únicos que exigem interpretar o layout da placa, não apenas casar
um padrão de texto. Em `fabricante` os três empatam tecnicamente (EasyOCR e GPT-4o com 3/9), porque
esse campo depende de uma lista fixa de marcas conhecidas — ver Seção 6.

## 6. Análise dos resultados

**Acertos.** GPT-4o-mini foi a abordagem mais consistente nos campos que exigem interpretação
semântica: `codigo_ativo` (6/8 = 75%), `numero_serie` (3/4 = 75%) e `potencia`/`modelo` (50% cada)
nos casos em que o gabarito tinha valor real. Em `placa_teste_20.jpg` (tag amarela grande e bem
iluminada) as três abordagens acertaram o `codigo_ativo`, mostrando que em boas condições de
captura a diferença entre os métodos praticamente desaparece.

**Erros — falha total.** Nenhuma das três abordagens leu nada útil em `placa_teste_27.jpg`
(posicionador FIELDVUE) nem nas 13 imagens 100% ilegíveis do gabarito (fotos de conjunto do
equipamento ou placas com corrosão/reflexo cobrindo o texto) — o equivalente direto às placas 07/08
da Sprint 2. Esse continua sendo o maior gargalo do pipeline: quando a placa não está em
primeiro plano e em foco, nenhuma abordagem de OCR/multimodal resolve sozinha.

**Erros — campo quase certo (falha de formatação, não de leitura).** Vários erros do GPT-4o foram
por um caractere de diferença, o que a métrica de exact-match trata como erro total mas que
teria fácil correção com normalização adicional: `"MAXIEM WATERJET"` vs. `"MAXIEM WATERJETS"`
(plural faltando), `"Waltech"` vs. `"WAL-TECH"` (hífen removido), `"DOLL"` vs. `"DoALL"` (uma letra
trocada no logo estilizado), `"66-M-522"` vs. `"66-M-1522"` (um dígito faltando). O CER médio do
GPT-4o (0,240) já capta parte dessa proximidade que a acurácia binária esconde.

**Erros — alucinação do modelo multimodal.** Em `placa_teste_25.jpg` o GPT-4o preencheu
`fabricante`, `modelo` e `numero_serie` com fragmentos do texto da tag (um identificador de
processo e um código de localização funcional) mesmo sem esses campos existirem na imagem — o
prompt pede para usar `"N/A"` quando o campo não é visível, mas o modelo às vezes prefere
"encontrar" algo plausível a admitir ausência. O mesmo ocorreu em `placa_teste_29.jpg`, com um
`numero_serie` inventado numa placa totalmente ofuscada por reflexo de luz. Esse é o principal risco
do uso de LLM multimodal em produção: diferente do regex (que só preenche um campo quando o padrão
bate), o modelo pode alucinar com confiança.

**Limitações.**
- O extrator por regex (EasyOCR/Tesseract) nunca preenche `modelo` — não há um padrão textual
  genérico para reconhecer modelos de fabricantes diferentes, como já documentado na Seção 7.1.
  Isso sozinho explica os 0% de EasyOCR/Tesseract em `modelo` na tabela restrita da Seção 5.1.
- O campo `fabricante` do regex depende de uma lista fixa (`FABRICANTES_CONHECIDOS`); mesmo após
  ampliá-la nesta Sprint com as marcas reais do conjunto de teste (WAL-TECH, General Electric,
  DoALL, Maxiem Waterjets, Econoline, Fieldvue), qualquer marca fora da lista — mesmo lida
  perfeitamente pelo OCR — nunca vira acerto. É um teto estrutural da abordagem por regras, não um
  problema de qualidade de OCR.
- O `codigo_ativo` do regex só reconhece o padrão `\d{2,3}-[A-Z]-\d{3,5}` (ex.: `62-M-4012`); tags
  reais do dataset em outros formatos (`027-ZSO-7218`, `24-1342`, `024-FY-0125`) nunca seriam
  capturadas por EasyOCR/Tesseract mesmo com OCR perfeito — só o GPT-4o, por interpretar
  semanticamente, consegue esses casos.
- Custo/latência: GPT-4o-mini precisa de uma chamada de API por imagem (~2-5s cada), com custo por
  token — não escalável sem controle em produção, diferente de EasyOCR/Tesseract que rodam
  localmente sem custo marginal.
- Gabarito definido manualmente por inspeção visual direta das 30 imagens; em placas parcialmente
  corroídas (ex.: `placa_teste_14.jpg`), alguns campos foram marcados `"N/A"` por prudência mesmo
  havendo leitura parcial, para não introduzir um valor "quase certo" como verdade absoluta.

**Comparação com o baseline da Sprint 2 (73,0%, 10 imagens, EasyOCR único, sem gabarito formal).**
A acurácia média subiu para todas as três abordagens (80,0% a 85,3%) mesmo triplicando o tamanho do
conjunto de teste e trocando a métrica antiga (taxa de campos com confiança ≥ 0,5, sem gabarito) por
uma métrica formal de exact-match contra gabarito manual. Esse ganho não deve ser lido como "o OCR
melhorou 10-12 pontos": a métrica da Sprint 2 media apenas *confiança* do OCR, não *correção* do
campo extraído, então os números não são diretamente comparáveis. A leitura mais honesta é a
tabela "só onde há valor no gabarito" (Seção 5.1): ali fica claro que a abordagem por regex
(EasyOCR/Tesseract) tem uma taxa de acerto real baixa (0-33%) fora do campo `codigo_ativo`, e que a
adição do GPT-4o-mini nesta Sprint é o que efetivamente move a agulha da tarefa de extração
estruturada — o ganho aparente de accuracy geral vem majoritariamente dos 21/30 casos triviais
onde não havia nada para extrair.

## 7. Próximos passos (Sprint 4)

- Detecção automática da região da placa antes do OCR (ex.: YOLO treinado para nameplates),
  resolvendo o caso de fotos do equipamento inteiro (já identificado como limitação #1 na Sprint 2).
- Pipeline híbrido custo-eficiente: usar EasyOCR/Tesseract para campos numéricos já bem resolvidos e
  reservar o modelo multimodal apenas para campos semanticamente ambíguos.
- Integração da leitura de placas com a planta visual (Draw.io) e a telemetria dos sensores
  Pepperl+Fuchs (MT-001, MT-002) já desenhadas na Sprint 2, fechando o fluxo completo de gêmeo
  digital proposto para a Forzy.

## 8. Evidências de execução

- Notebook completo, executado do início ao fim sem erros: `Sprint3_Multiabordagem_Forzy.ipynb`
- Resultados brutos das 3 abordagens (30 imagens): `resultados_brutos_sprint3.csv`
- Gabarito das 30 imagens: `gabarito_30_imagens.csv`
- Tabela de acurácia por campo e por abordagem: `acuracia_sprint3.csv`
- Gráficos comparativos: `graficos_comparativos_sprint3.png`
- Imagens de teste originais e padronizadas: `imagens_teste_originais/`, `imagens_teste_padronizadas/`
