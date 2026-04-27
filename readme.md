# Smith-Waterman (Python)

Implementacao do algoritmo de Smith-Waterman desenvolvida na disciplina de Bioinformatica da UFPI, com execucao unificada pelo arquivo main.py.

## O que este projeto faz

- Calcula alinhamento global e local entre duas sequencias.
- Exibe:
	- matriz de score global
	- matriz de score local
- Mostra os alinhamentos resultantes e o melhor score.

## Estrutura do projeto

```text
Smith-Waterman/
	main.py                  # entrypoint unico (ui e terminal)
	input.txt                # entrada padrao
	readme.md

	backend/
		__init__.py
		io_entrada.py          # leitura e parsing da entrada
		alinhamento.py         # algoritmo completo (matrizes, traceback e suite)

	frontend/
		__init__.py
		aplicacao.py           # UI completa (constantes, widgets, formatacao e tela)
		front-end.py           # atalho opcional para UI
```

## Requisitos

- Python 3.10+
- Dependencias:
	- numpy
	- pygame

Instalacao:

```bash
pip install numpy pygame
```

## Como executar

### 1) Interface grafica (padrao)

```bash
python main.py
```

No Windows, se necessario:

```bash
py main.py
```

### 2) Modo terminal

```bash
python main.py --modo terminal
```

Com arquivo customizado:

```bash
python main.py --modo terminal --entrada input.txt
```

### 3) Atalho legado para UI (opcional)

```bash
python frontend/front-end.py
```

## Formato do input.txt

O arquivo [input.txt](input.txt) deve conter 5 linhas:

1. sequencia vertical
2. sequencia horizontal
3. penalidade de gap
4. penalidade de mismatch
5. pontuacao de match

Exemplo:

```text
AATG
TTGA
-2
-1
1
```

## Observacoes

- [main.py](main.py) e o entrypoint principal e unificado para todos os modos.
- [frontend/front-end.py](frontend/front-end.py) foi mantido apenas como atalho de compatibilidade para a UI.
- A estrutura foi simplificada para manter somente modulos com responsabilidade clara e leitura linear.