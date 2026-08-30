# Roteiro de apresentação — Sprint 3 (Forzy / Leitura de Placas)

Duração alvo: **10–12 minutos** (14 slides, ~45s cada em média — os slides de resultado podem
render mais tempo, os de código menos). Slide deck: `sprint3_slides.html` (publicado como artifact —
navegação por seta ←/→, espaço, ou clique nas bolinhas/botões).

Sugestão de divisão entre os 5 integrantes (ajustem como preferirem):
- **Bloco 1 — Contexto** (slides 1–3): 1 pessoa
- **Bloco 2 — As 3 abordagens** (slides 4–7): 1 pessoa por abordagem + regex, ou 1 pessoa só
- **Bloco 3 — Avaliação e bug** (slides 8–9): 1 pessoa
- **Bloco 4 — Resultados** (slides 10–12): 1 pessoa
- **Bloco 5 — Limitações, próximos passos, fechamento** (slides 13–14): 1 pessoa

---

## Slide 1 — Título

> "Boa tarde. Na Sprint 2 a gente construiu um protótipo de OCR pra ler placas de identificação de
> equipamentos industriais do projeto Forzy — motores, bombas, refiners de uma fábrica de papel.
> Hoje a gente vem mostrar a evolução: comparamos três abordagens diferentes de leitura, cada uma
> testada nas mesmas 30 imagens, com resultado medido de verdade contra um gabarito manual."

**Não entre em detalhe técnico ainda** — esse slide é só pra situar quem está assistindo.

---

## Slide 2 — Da Sprint 2 pra cá

> "Na Sprint 2 a gente usou só o EasyOCR, em 10 imagens, e mediu só a *confiança* do OCR — não se o
> campo extraído estava certo. Deu 73% de taxa de validade, mas duas placas falharam completamente
> porque a foto pegou o equipamento inteiro, não a placa em si. E toda correção de rotação era
> manual, imagem por imagem.
>
> Essa Sprint ataca isso de frente: rotação automática virou parte do pipeline, a gente estrutura o
> texto bruto em campos via regex, adicionou duas abordagens novas — Tesseract e GPT-4o — e montou
> um conjunto de teste de 30 imagens com gabarito definido à mão, pra ter uma acurácia real pela
> primeira vez."

**Dica:** aponte para os dois cards lado a lado no slide — o contraste "antes/depois" é o gancho da
apresentação inteira.

---

## Slide 3 — Pipeline geral

> "Esse é o fluxo: a imagem sai do dataset, passa por uma padronização de tamanho e contraste, e aí
> se divide em três caminhos paralelos — EasyOCR, Tesseract e GPT-4o — cada um tentando extrair os
> mesmos 5 campos: código do ativo, fabricante, modelo, número de série e potência. No final, tudo
> isso é comparado contra o gabarito que a gente montou manualmente."

**Dica:** é o único slide "arquitetural" — não precisa se alongar, é só orientação visual antes de
entrar em cada abordagem.

---

## Slide 4 — EasyOCR

> "Primeira abordagem: EasyOCR, uma rede neural de detecção e reconhecimento de texto. A diferença
> pra Sprint 2 é esse parâmetro aqui, `rotation_info` — antes a gente corrigia rotação na mão, agora
> o EasyOCR testa a imagem em quatro orientações automaticamente e fica só com as leituras que têm
> confiança acima de 0,5."

Se alguém perguntar "por que 0.5": é o mesmo limiar validado na Sprint 2, mantido por consistência.

---

## Slide 5 — Tesseract

> "Segunda abordagem: Tesseract, o motor de OCR clássico, mais antigo. Ele não tem esse recurso de
> testar múltiplas rotações sozinho, então depende muito mais do pré-processamento — a gente aplica
> CLAHE, que é uma equalização de contraste local, pra realçar texto em placas desgastadas ou
> enferrujadas.
>
> Detalhe técnico que vale mencionar: no Windows, o Tesseract não é instalado via pip como uma
> biblioteca Python normal — é um programa separado que precisa ser instalado à parte, e a gente
> precisa apontar o caminho dele explicitamente no código."

---

## Slide 6 — GPT-4o-mini

> "Terceira abordagem, e a diferente das outras duas: GPT-4o-mini, um modelo de linguagem
> multimodal. Aqui não tem OCR nem regex — a imagem inteira vai em base64 dentro de um prompt que
> pede os 5 campos em JSON. O modelo não está casando padrão de texto, ele está *interpretando* a
> placa — inclusive consegue diferenciar 'número de série' de 'código do ativo' mesmo quando os dois
> são sequências de números parecidas, coisa que regex não consegue fazer sozinho."

---

## Slide 7 — Regex e o bug da lista de fabricantes

> "Só que EasyOCR e Tesseract não devolvem JSON pronto — devolvem texto bruto, que a gente precisa
> converter pros 5 campos usando regex. E aqui a gente encontrou um problema real: o campo
> `fabricante` só reconhece marcas de uma lista fixa. A lista original tinha 8 marcas — WEG, Siemens,
> KSB e outras — mas só **uma** delas, a Siemens, aparecia de fato nas 30 imagens do nosso teste.
> Marcas como WAL-TECH, General Electric, DoALL, apareciam várias vezes nas placas reais, mas nunca
> seriam reconhecidas, mesmo com o OCR lendo o texto perfeitamente.
>
> A gente ampliou a lista com as marcas reais do conjunto de teste, mas o problema estrutural
> continua: é um teto artificial da abordagem por regras, não da qualidade do OCR."

**Esse é um dos pontos mais fortes da apresentação** — mostra pensamento crítico sobre o próprio
pipeline, não só "rodei e deu resultado". Vale caprichar na explicação.

---

## Slide 8 — Gabarito das 30 imagens

> "Pra avaliar de verdade, a gente pegou 30 imagens do dataset — diferentes das 10 já usadas de
> demonstração na Sprint 2 — e definiu manualmente o valor esperado de cada um dos 5 campos,
> olhando a imagem diretamente, sem consultar o que os modelos tinham respondido, pra não influenciar
> o julgamento.
>
> Treze dessas 30 imagens são completamente ilegíveis — foto do equipamento inteiro, corrosão total,
> ou reflexo de luz cobrindo a placa. Isso já era esperado: é o mesmo tipo de falha que a gente já
> tinha visto nas placas 07 e 08 da Sprint 2."

---

## Slide 9 — O bug do "N/A"

> "Durante os testes a gente encontrou um bug sério no próprio cálculo de acurácia, não no OCR. A
> função do pandas que lê o CSV do gabarito trata a string `'N/A'` como valor ausente por padrão, e
> converte pra `NaN` — só que isso só acontecia do lado do gabarito, porque as previsões dos modelos
> ficavam em memória, nunca passavam por essa conversão. Resultado: mesmo quando os dois lados
> concordavam que não tinha nada pra ler, o sistema contava como erro.
>
> Antes de corrigir isso, a acurácia do EasyOCR aparecia como 3,3%. Depois do fix — uma única opção
> a mais no `read_csv` — subiu pra 82,7%. É a mesma extração, o número só estava sendo calculado
> errado."

**Esse slide é ótimo pra mostrar processo de debugging real** — não tenham medo de contar essa
história, mostra maturidade técnica.

---

## Slide 10 — Resultado geral

> "Com o bug corrigido, esse é o resultado final nas 30 imagens: GPT-4o-mini na frente com 85,3% de
> acurácia geral e o menor CER — Character Error Rate, quanto menor melhor —, seguido por EasyOCR
> com 82,7% e Tesseract com 80%.
>
> Mas esse número sozinho engana: 21 das 30 imagens têm gabarito 'N/A' em tudo, e acertar 'não tem
> nada pra ler' conta como acerto igual pras três abordagens. Isso infla a régua toda pra cima. O
> número que separa de verdade as abordagens está no próximo slide."

---

## Slide 11 — Resultado por campo (o que importa)

> "Filtrando só os casos em que o gabarito tinha um valor real pra comparar, a diferença fica clara:
> em código do ativo o GPT-4o acerta 75% contra 25% do EasyOCR e 12,5% do Tesseract. Em modelo,
> número de série e potência — campos que exigem entender o layout da placa, não só reconhecer um
> padrão de texto — EasyOCR e Tesseract ficam em zero por cento, e o GPT-4o entre 50 e 75%.
>
> Só em fabricante os três empatam tecnicamente, e isso não é força do regex — é porque esse campo
> depende da lista fixa de marcas que a gente mostrou no slide 7."

---

## Slide 12 — Casos concretos

> "Pra ilustrar com exemplos reais: numa das imagens, o EasyOCR leu o texto certo, mas o regex
> confundiu dígitos do código do ativo com o campo de potência e devolveu '5018 HP' em vez de
> '150 HP' — um erro de regras, não de leitura. Em outra imagem, com uma tag amarela grande e bem
> iluminada, as três abordagens acertaram — mostrando que em boas condições de captura a diferença
> quase desaparece.
>
> Mas o GPT-4o também tem um risco real: em duas imagens ele **alucinou**. Numa delas, inventou um
> fabricante e um número de série a partir de texto que não tinha nada a ver com esses campos. Na
> outra, numa placa completamente ilegível por reflexo de luz, ele devolveu um número de série que
> não tem base nenhuma na imagem. Isso é o principal risco de usar um modelo de linguagem em
> produção: diferente do regex, que só preenche um campo quando o padrão realmente bate, o modelo
> pode responder com confiança mesmo errado."

---

## Slide 13 — Limitações e Sprint 4

> "Resumindo as limitações: o campo modelo nunca é preenchido pelo regex, porque não existe um
> padrão de texto genérico entre fabricantes diferentes. Treze das 30 imagens são falha total nas
> três abordagens — o problema é a captura da foto, não o método de leitura. O GPT-4o tem custo por
> chamada de API e pode alucinar. E o gabarito foi definido por uma pessoa só, por inspeção visual,
> então tem uma margem de subjetividade em placas parcialmente legíveis.
>
> Pra Sprint 4, os próximos passos: detecção automática da região da placa antes do OCR, tipo um
> YOLO treinado pra nameplates, que ataca direto essas 13 falhas totais; um pipeline híbrido, usando
> regex pra códigos de ativo já bem resolvidos e reservando o GPT-4o só pros campos ambíguos, pra
> cortar custo de API; e por fim integrar essa leitura de placas com a planta visual e os sensores
> Pepperl+Fuchs que a gente desenhou lá na Sprint 2."

---

## Slide 14 — Fechamento

> "Era isso. Notebook completo, gabarito, resultados brutos e esse material estão todos no
> repositório da Sprint 3. Ficamos à disposição para perguntas."

---

## Perguntas prováveis (e respostas rápidas)

- **"Por que não usar só o GPT-4o, já que ele ganhou?"** — Custo e latência por imagem, e ele
  aluciona em placas ilegíveis com a mesma confiança que acerta as legíveis. Por isso o plano da
  Sprint 4 é um pipeline híbrido, não substituir tudo por LLM.
- **"O gabarito não é enviesado, já que só uma pessoa definiu?"** — É uma limitação real, documentada
  no relatório. Em placas parcialmente legíveis, preferimos marcar como N/A a arriscar um valor
  "quase certo" como verdade absoluta.
- **"Por que a acurácia geral (85%) é tão mais alta que a por campo (25-75%)?"** — Porque 21 das 30
  imagens têm gabarito totalmente vazio, e acertar "não achei nada" conta como acerto — ver slides
  10 e 11.
