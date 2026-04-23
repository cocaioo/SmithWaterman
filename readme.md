# Smith-Waterman (Python)

Implementacao do algoritmo de Smith-Waterman desenvolvida na disciplina de Bioinformatica da UFPI, com versao em terminal e interface grafica (Pygame).

## O que este projeto faz

- Calcula alinhamento global e local entre duas sequencias.
- Exibe:
	- matriz de score global
	- matriz de ponteiros global
	- matriz de score local
	- matriz de ponteiros local
- Mostra os alinhamentos resultantes e o melhor score.

## Estrutura do projeto

```text
Smith-Waterman/
	main.py                  # entrypoint backend (terminal)
	front-end.py             # entrypoint UI (Pygame)
	input.txt                # entrada padrao
	readme.md

	backend/
		__init__.py
		constantes.py          # constantes de ponteiro e tolerancia
		io_entrada.py          # leitura e parsing da entrada
		matriz.py              # construcao de matrizes e scores candidatos
		ponteiros.py           # codificacao/decodificacao e escolha de direcao
		alinhamento.py         # traceback e montagem dos alinhamentos
		suite.py               # orquestracao do pipeline de alinhamento

	frontend/
		__init__.py
		aplicacao.py           # classe principal da UI
		widgets.py             # campo de entrada e botao
		constantes_ui.py       # cores, dimensoes e FPS
		formatacao.py          # renderizacao de matrizes em texto
		padroes.py             # carga de valores padrao (input.txt)
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

### 1) Backend no terminal

```bash
python main.py
```

No Windows, se necessario:

```bash
py main.py
```

### 2) Interface grafica

```bash
python front-end.py
```

No Windows, se necessario:

```bash
py front-end.py
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

- [main.py](main.py) e [front-end.py](front-end.py) foram mantidos como entrypoints para facilitar execucao.
- A logica principal foi modularizada em [backend/](backend) e [frontend/](frontend) para melhorar legibilidade e manutencao.