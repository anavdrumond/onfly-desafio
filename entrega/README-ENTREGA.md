# Entrega — Consolidador de reservas de hotel

## Defeitos corrigidos

| # | Arquivo | Defeito | Causa raiz |
|-|-|-|-|
| 1 | `src/onfly_report/services/status_policy.py` | `NO_SHOW` entrava em noites, valores, `by_month` e `top_hotels`. | `is_billable` excluía apenas `CANCELLED` (`status != "CANCELLED"`) em vez de aceitar só `CONFIRMED`. |
| 2 | `src/onfly_report/services/stay_calculator.py` | Noites erradas/negativas na virada de mês/ano (30/01 → 02/02 dava `-28`). | Subtraía o dia do mês (`checkout.day - checkin.day`) em vez da diferença entre as datas (`(checkout - checkin).days`). |
| 3 | `src/onfly_report/services/currency_converter.py` | Valores em moeda estrangeira subavaliados (100 USD viravam ~18,45 BRL). | Dividia pela taxa em vez de multiplicar e passava por `float`, violando a regra de usar `Decimal` no dinheiro. |
| 4 | `src/onfly_report/services/report_builder.py` | `top_hotels` mostrava os hotéis de **menor** valor. | A ordenação usava `total_brl` crescente; agora é decrescente com desempate por `hotel_id` crescente. |
| 5 | `src/onfly_report/repositories/csv_reservation_repository.py` | O dataset de 300 reservas gerava relatório com 200. | A leitura interrompia silenciosamente após 200 linhas (`if len(rows) == 200: break`). |

## Como investiguei

1. Li o README como especificação e mapeei cada regra (status, noites, câmbio, exatidão, ordenação, contrato) para o
   componente responsável (`services/*`, `repositories/*`, `report_builder.py`).
2. Rodei `pytest -q` e o CLI na amostra e no dataset completo **antes** de qualquer alteração, guardando a saída para
   comparação (5/5 testes falhando; noites negativas, total BRL incorreto, 200 de 300 reservas).
3. Corrigi um defeito por componente, com mudanças mínimas, e revalidei contra os testes e a tabela de amostra do README.
4. O teto de 200 linhas não é coberto pelos testes fornecidos: escrevi primeiro `tests/test_input_size.py`
   (250 reservas), confirmei que falhava e só então removi o limite.
5. Confrontei cada requisito comportamental do README com o código e os testes. Para os que estavam sem cobertura e
   envolvem dados consistentes, adicionei testes (abaixo). Para garantir que eles detectam regressões, rodei um teste de
   mutação numa cópia do projeto: 13 defeitos injetados um a um (half-even, `float` no câmbio, arredondar por item,
   empate sem `hotel_id`, `by_month` sem ordem ou pelo check-out, ignorar quartos, `--top` padrão/validação, versão,
   offset, média sem noites) — todos detectados.

### Testes adicionados

| Arquivo | Cobre |
|-|-|
| `tests/test_input_size.py` | Todas as reservas do arquivo são processadas (sem teto de linhas). |
| `tests/test_room_nights.py` | Virada de ano, fevereiro bissexto/comum, múltiplos quartos e média por noite de quarto. |
| `tests/test_money_rounding.py` | Half-up em empate exato, soma exata com arredondamento só na serialização, câmbio EUR. |
| `tests/test_by_month.py` | Mês do check-in, apenas `CONFIRMED`, ordem ascendente entre anos. |
| `tests/test_top_hotels_rules.py` | Agregação por hotel só com `CONFIRMED`, menos hotéis que `--top`, desempate por `hotel_id`. |
| `tests/test_no_billable.py` | Arquivo só com cabeçalho e sem `CONFIRMED`: totais zerados e média `"0.00"`. |
| `tests/test_cli_contract.py` | Códigos de saída `2` (`--top` inválido, argumento ou arquivo ausente), padrões de `--output`/`--top`, resumo no stdout, schema e formatos. |
| `tests/test_validation_sample.py` | Tabela "Amostra de validação" do README como regressão automatizada. |
| `tests/cli_runner.py` | Helper para executar o CLI com argumentos arbitrários (sem exigir código `0`). |

Cenários que dependem de entrada inconsistente (moeda sem taxa, CSV fora de UTF-8, datas fora de `YYYY-MM-DD`,
status desconhecido, `checkout <= checkin`, `rooms <= 0`) ficaram fora do escopo, pois o README garante dados
consistentes.

## Decisões e tradeoffs

### Remoção do limite de leitura

O README define `total_reservations` como o *número de reservas no arquivo* e não menciona limite algum. Qualquer teto
fixo (200, 300, 1000…) quebraria o contrato assim que o arquivo crescesse, e o corte era silencioso (sem log nem erro).
Por isso o limite foi removido, sem ser substituído por outro valor.

**Tradeoff assumido:** sem teto, o consumo de memória passa a crescer sem limite com o tamanho da entrada. A
implementação atual materializa o arquivo inteiro duas vezes (lista de `RawRow` com o `dict` de cada linha e lista de
`Reservation`) antes de agregar. Medição com `tracemalloc` (Python 3.11, dataset replicado):

| Reservas | CSV | Pico de memória | Por reserva |
|-|-|-|-|
| 10.000 | 1,5 MB | 18 MB | ~1,8 KB |
| 100.000 | 14,9 MB | 180 MB | ~1,8 KB |
| 500.000 | 74,6 MB | 903 MB | ~1,8 KB |

A memória é linear, ~12× o tamanho do CSV: algo como 1,8 GB para 1 milhão de reservas, com risco de OOM em
containers/máquinas pequenas. O tempo de processamento também é linear (O(n)) e não muda com o modelo de leitura; as
ordenações atuam só sobre meses e hotéis.

**Mitigação possível (não implementada):** processar em streaming. Todas as agregações são somas/contagens exatas em
`Decimal`, então podem ser acumuladas linha a linha; o estado necessário é proporcional apenas ao número de meses e
hotéis, não ao de reservas. Isso exigiria transformar `CsvReservationRepository.read()` em gerador e unir contagem de
status, filtro e agregação em uma única passada no `ReportBuilder`, mantendo a ordem lógica
`ler → converter → contar → filtrar → agregar` por linha. Não foi implementada porque os volumes do desafio (300
reservas) estão ordens de grandeza abaixo do ponto de risco, e o foco da entrega é a correção dos defeitos.

## Como validar

Ambiente usado na validação: WSL Ubuntu, Python 3.11.18, pytest 8.3.4 (`requirements-dev.txt`).

```bash
python3.11 -m venv .venv
source .venv/bin/activate
pip install -r requirements-dev.txt

pytest -q

PYTHONPATH=src python -m onfly_report \
  --input data/reservas_hoteis.csv \
  --rates data/taxas_cambio.csv \
  --output output/report.json

PYTHONPATH=src python -m onfly_report \
  --input data/exemplo-validacao.csv \
  --rates data/taxas_cambio.csv \
  --output output/exemplo.json      # comparar com a tabela "Amostra de validação" do README
```

Saída obtida (código de saída `0` nos dois casos):

```
Reservas: 300 | Confirmadas: 235 | Noites: 1347 | Total BRL: 396170.00
Reservas: 12 | Confirmadas: 9 | Noites: 28 | Total BRL: 7566.00
```

A amostra confere campo a campo com o README (`summary`, `by_month` e `top_hotels`), verificação automatizada em
`tests/test_validation_sample.py`.

| Dataset completo | Antes | Depois |
|-|-|-|
| `total_reservations` | 200 | 300 |
| `total_room_nights` | -1393 | 1347 |
| `total_amount_brl` | 193218.53 | 396170.00 |

Os arquivos `data/*.csv` e os testes fornecidos (`tests/helpers.py` e `tests/test_{currency,nights,regression_report,status_rules,top_hotels}.py`)
foram conferidos por SHA-256 contra o pacote original do desafio: idênticos.

## Resultado do `pytest`

Antes das correções (mensagens de falha resumidas):

```
FFFFF                                                                    [100%]
FAILED tests/test_currency.py::test_currency_conversion_to_brl - AssertionError: '118.45' == '642.00'
FAILED tests/test_nights.py::test_nights_across_month_boundary - assert -28 == 3
FAILED tests/test_regression_report.py::test_regression_report_on_sample - total_amount_brl '1018.45' != '1542.00'
FAILED tests/test_status_rules.py::test_status_rules_exclude_cancelled_and_no_show - '120.00' == '100.00'
FAILED tests/test_top_hotels.py::test_top_hotels_are_ranked_descending - ['H04', 'H03', 'H02'] == ['H01', 'H02', 'H03']
5 failed
```

Depois das correções:

```
.............................                                            [100%]
29 passed
```

Os 5 testes fornecidos passam sem alteração; os demais 24 são os testes adicionais listados em "Como investiguei".

## Limitações conhecidas e melhorias futuras

Fora do escopo desta entrega, pois o README garante que os dados são consistentes e esses cenários não ocorrem nos
arquivos fornecidos:

- **Processamento em streaming** para entradas muito grandes (ver "Decisões e tradeoffs").
- **Moeda sem taxa** termina com código `1` (`KeyError`), e não `2` (entrada inválida).
- **CSV fora de UTF-8** gera `UnicodeDecodeError`, não tratado pelos repositórios, e termina com código `1`.
- **Datas:** `date.fromisoformat` do Python 3.11 aceita formatos além de `YYYY-MM-DD` (ex.: `20250110`).
- **Normalização de moeda e status:** a moeda é convertida para maiúsculas na tabela de câmbio, mas não na reserva
  (`usd` termina com código `1`); status fora dos três valores, inclusive em minúsculas, entra em `total_reservations`
  sem entrar em nenhuma contagem por status.
- **Estadias inválidas** (`checkout <= checkin`, `rooms <= 0`) não são rejeitadas.

## Uso de IA

Usei assistente de IA. A exportação da sessão e a declaração estão em `entrega/uso-de-ia/`.
