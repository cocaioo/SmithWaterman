# Smith-Waterman

## Descrição
Implementação do alinhamento de sequências com Smith-Waterman.

## Entrada
O programa lê `input.txt`. O arquivo deve ter 5 linhas:

1. sequência vertical
2. sequência horizontal
3. penalidade de gap (número)
4. penalidade de mismatch (número)
5. pontuação de match (número)

Exemplo:

```text
AATG
TTGA
-2
-1
1
```

## Execução

Interface gráfica (padrão):

```bash
python main.py
```

No Windows:

```bash
py main.py
```

Modo terminal:

```bash
python main.py --modo terminal
```

Com arquivo customizado:

```bash
python main.py --modo terminal --entrada input.txt
```

Atalho opcional para UI:

```bash
python frontend/front-end.py
```

## Saída
A execução produz matrizes de score e alinhamentos.
O resultado retornado por `executar_suite_alinhamento` contém, entre outras, estas chaves:

- `matriz_score_global`, `matriz_score_local`, `matriz_bestscore`
- `vertical_global`, `horizontal_global`, `score_global`
- `vertical_local`, `horizontal_local`, `score_local`
- `vertical_bestscore`, `horizontal_bestscore`, `score_bestscore`

No modo terminal, `main.py` imprime as matrizes e um resumo dos alinhamentos global e local.

## Estrutura

Principais arquivos:

- `main.py` — entrypoint (UI e terminal)
- `input.txt` — arquivo de entrada padrão
- `backend/io_entrada.py` — leitura e parsing
- `backend/alinhamento.py` — algoritmo e tracebacks
- `frontend/aplicacao.py` — interface gráfica

## Requisitos

- Python 3.10+
- `numpy`, `pygame`

Instalação:

```bash
pip install numpy pygame
```