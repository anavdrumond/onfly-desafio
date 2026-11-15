# Declaração de uso de IA

## Ferramenta e modelo

- **Ferramenta:** GitHub Copilot CLI (versão 1.0.112-0), em sessão interativa no terminal.
- **Modelo:** Claude Opus 5.5 (`claude-opus-5.5`).
- **Registro:** exportação da sessão em `entrega/uso-de-ia/sessao.md` (comando `/share file`).

## O que a IA fez

- Leu o README e o código e produziu um overview da arquitetura, do fluxo de processamento e da organização dos testes.
- Apontou os cinco defeitos a partir da comparação entre as regras do README e o código.
- Preparou o ambiente de validação no WSL (Python 3.11.18 via `uv`, venv com `requirements-dev.txt`), registrou o
  resultado de `pytest` e do CLI antes das correções e repetiu após cada etapa para comparação.
- Implementou as correções aprovadas em `status_policy.py`, `stay_calculator.py`, `currency_converter.py`,
  `report_builder.py` e `csv_reservation_repository.py`.
- Mediu o consumo de memória para entradas grandes (`tracemalloc`) e levantou o perfil dos CSVs fornecidos.
- Fez o levantamento dos requisitos do README × código × testes, separando atendidos, divergências e pontos a validar.
- Escreveu os testes adicionais e rodou um teste de mutação numa cópia do projeto para confirmar que eles detectam
  regressões.
- Redigiu esta declaração e o `README-ENTREGA.md`, e conferiu por hash que dados e testes fornecidos não foram
  alterados.

## O que eu fiz

- Conduzi a sessão etapa por etapa, definindo o que investigar, em que ordem e quando apenas analisar sem alterar código.
- Verifiquei cada defeito apontado contra as definições do README antes de autorizar as correções.
- Questionei o limite de leitura e decidi removê-lo por completo, em vez de trocar por outro número, com teste
  dedicado.
- Levantei o risco de memória com entradas grandes, avaliei a alternativa de streaming e decidi registrá-la como
  melhoria futura, sem implementar.
- Defini o escopo dos testes adicionais (apenas cenários com dados consistentes).
- Revisei manualmente o código corrigido, os testes e a documentação de entrega.
