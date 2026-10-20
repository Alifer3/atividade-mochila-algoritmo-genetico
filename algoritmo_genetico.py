import csv
import random
import time
import argparse
from typing import List, Dict, Tuple, Optional, Any


def carregar_dados(caminho_csv: str) -> Tuple[List[Dict[str, Any]], int]:
    """
    Lê o arquivo CSV contendo os itens da mochila e a capacidade.
    Formato esperado de colunas: item, peso, valor, capacidade
    """
    itens = []
    capacidade_esperada = None

    with open(caminho_csv, mode="r", encoding="utf-8") as f:
        leitor = csv.DictReader(f)
        for linha_num, linha in enumerate(leitor, start=1):
            item_nome = linha["item"].strip()
            peso = int(linha["peso"].strip())
            valor = int(linha["valor"].strip())
            cap_linha = int(linha["capacidade"].strip())

            if capacidade_esperada is None:
                capacidade_esperada = cap_linha
            elif cap_linha != capacidade_esperada:
                raise ValueError(
                    f"Inconsistência de capacidade na linha {linha_num}: "
                    f"esperada {capacidade_esperada}, encontrada {cap_linha}."
                )

            itens.append({
                "item": item_nome,
                "peso": peso,
                "valor": valor
            })

    if capacidade_esperada is None:
        raise ValueError(f"O arquivo {caminho_csv} está vazio ou não possui dados válidos.")

    return itens, capacidade_esperada


def avaliar_cromossomo(cromossomo: List[int], itens: List[Dict[str, Any]], capacidade: int) -> Tuple[int, int, int, bool]:
    """
    Avalia um cromossomo binário.
    Retorna: (aptidao, peso_total, valor_total, valido)
    f(x) = V(x) se P(x) <= C, senão 0.
    """
    peso_total = 0
    valor_total = 0

    for gene, item in zip(cromossomo, itens):
        if gene == 1:
            peso_total += item["peso"]
            valor_total += item["valor"]

    valido = peso_total <= capacidade
    aptidao = valor_total if valido else 0

    return aptidao, peso_total, valor_total, valido


def criar_populacao_inicial(tamanho_pop: int, num_itens: int, prob_um: float = 0.3) -> List[List[int]]:
    """
    Gera a população inicial com cromossomos aleatórios.
    Cada gene tem probabilidade 'prob_um' de começar com 1.
    Inclui o vetor de zeros na primeira posição como solução válida de referência.
    """
    populacao = []
    # Vetor de zeros como referência inicial válida
    populacao.append([0] * num_itens)

    for _ in range(tamanho_pop - 1):
        individuo = [1 if random.random() < prob_um else 0 for _ in range(num_itens)]
        populacao.append(individuo)

    return populacao


def selecao_torneio(populacao: List[List[int]], aptidoes: List[int], tamanho_torneio: int = 3) -> List[int]:
    """
    Seleciona um indivíduo por torneio de tamanho k e retorna uma cópia dele.
    """
    indices_candidatos = random.sample(range(len(populacao)), tamanho_torneio)
    melhor_indice = max(indices_candidatos, key=lambda idx: aptidoes[idx])
    return populacao[melhor_indice][:]


def cruzamento_um_ponto(pai1: List[int], pai2: List[int], taxa_cruzamento: float = 0.8) -> Tuple[List[int], List[int]]:
    """
    Aplica cruzamento de 1 ponto com probabilidade taxa_cruzamento.
    Sem cruzamento, retorna cópias dos pais.
    """
    if random.random() < taxa_cruzamento and len(pai1) > 1:
        ponto_corte = random.randint(1, len(pai1) - 1)
        filho1 = pai1[:ponto_corte] + pai2[ponto_corte:]
        filho2 = pai2[:ponto_corte] + pai1[ponto_corte:]
        return filho1, filho2
    else:
        return pai1[:], pai2[:]


def mutacao(cromossomo: List[int], taxa_mutacao: float = 0.05) -> List[int]:
    """
    Aplica mutação bit-flip (0 <-> 1) em cada gene com probabilidade taxa_mutacao.
    """
    novo = cromossomo[:]
    for i in range(len(novo)):
        if random.random() < taxa_mutacao:
            novo[i] = 1 - novo[i]
    return novo


def executar_algoritmo_genetico(
    itens: List[Dict[str, Any]],
    capacidade: int,
    tamanho_pop: int = 50,
    num_geracoes: int = 100,
    taxa_cruzamento: float = 0.8,
    taxa_mutacao: float = 0.05,
    tamanho_torneio: int = 3,
    elite: int = 1,
    prob_um_inicial: float = 0.3,
    semente: Optional[int] = None
) -> Dict[str, Any]:
    """
    Executa o Algoritmo Genético para o problema da mochila binária.
    Mede apenas o tempo de execução do algoritmo com time.perf_counter().
    """
    if semente is not None:
        random.seed(semente)

    num_itens = len(itens)

    # Início da medição de tempo
    t_inicio = time.perf_counter()

    populacao = criar_populacao_inicial(tamanho_pop, num_itens, prob_um=prob_um_inicial)

    # Melhor solução válida encontrada ao longo de toda a execução
    melhor_solucao_valida = {
        "cromossomo": [0] * num_itens,
        "aptidao": 0,
        "peso": 0,
        "valor": 0,
        "valido": True,
        "geracao_encontrada": 0
    }

    historico_melhor_valido = []

    for geracao in range(num_geracoes + 1):
        # Avaliação da população atual
        avaliacoes = [avaliar_cromossomo(ind, itens, capacidade) for ind in populacao]
        aptidoes = [av[0] for av in avaliacoes]

        # Atualizar a melhor solução válida
        for ind, (apt, peso, val, valido) in zip(populacao, avaliacoes):
            if valido and val > melhor_solucao_valida["valor"]:
                melhor_solucao_valida = {
                    "cromossomo": ind[:],
                    "aptidao": apt,
                    "peso": peso,
                    "valor": val,
                    "valido": True,
                    "geracao_encontrada": geracao
                }

        # Registra a melhor solução válida até o momento
        historico_melhor_valido.append(melhor_solucao_valida["valor"])

        # Se for a última geração, encerra o laço
        if geracao == num_geracoes:
            break

        # Identificar elite (indivíduo com maior aptidão na geração atual)
        melhor_idx_geracao = max(range(len(populacao)), key=lambda idx: aptidoes[idx])
        elite_individuo = populacao[melhor_idx_geracao][:]

        nova_populacao = []
        # Elitismo: copia os melhores indivíduos para a próxima geração
        for _ in range(elite):
            nova_populacao.append(elite_individuo[:])

        # Preencher o restante da população com filhos gerados
        while len(nova_populacao) < tamanho_pop:
            pai1 = selecao_torneio(populacao, aptidoes, tamanho_torneio)
            pai2 = selecao_torneio(populacao, aptidoes, tamanho_torneio)

            filho1, filho2 = cruzamento_um_ponto(pai1, pai2, taxa_cruzamento)

            filho1 = mutacao(filho1, taxa_mutacao)
            nova_populacao.append(filho1)

            if len(nova_populacao) < tamanho_pop:
                filho2 = mutacao(filho2, taxa_mutacao)
                nova_populacao.append(filho2)

        populacao = nova_populacao

    t_fim = time.perf_counter()
    tempo_execucao = t_fim - t_inicio

    # Itens selecionados na melhor solução válida
    itens_selecionados = [
        itens[i]["item"]
        for i, gene in enumerate(melhor_solucao_valida["cromossomo"])
        if gene == 1
    ]

    melhor_solucao_valida["itens_selecionados"] = itens_selecionados

    return {
        "melhor_solucao": melhor_solucao_valida,
        "historico_melhor_valido": historico_melhor_valido,
        "tempo_execucao": tempo_execucao,
        "capacidade": capacidade,
        "num_itens": num_itens,
        "parametros": {
            "tamanho_pop": tamanho_pop,
            "num_geracoes": num_geracoes,
            "taxa_cruzamento": taxa_cruzamento,
            "taxa_mutacao": taxa_mutacao,
            "tamanho_torneio": tamanho_torneio,
            "elite": elite,
            "semente": semente
        }
    }


def main():
    parser = argparse.ArgumentParser(description="Algoritmo Genético para o Problema da Mochila Binária")
    parser.add_argument("-a", "--arquivo", type=str, default="entradas/entrada_01.csv", help="Caminho do arquivo CSV de entrada")
    parser.add_argument("-p", "--populacao", type=int, default=50, help="Tamanho da população (padrão: 50)")
    parser.add_argument("-g", "--geracoes", type=int, default=100, help="Número de gerações (padrão: 100)")
    parser.add_argument("-c", "--cruzamento", type=float, default=0.8, help="Taxa de cruzamento (padrão: 0.8)")
    parser.add_argument("-m", "--mutacao", type=float, default=0.05, help="Taxa de mutação por gene (padrão: 0.05)")
    parser.add_argument("-t", "--torneio", type=int, default=3, help="Tamanho do torneio (padrão: 3)")
    parser.add_argument("-e", "--elite", type=int, default=1, help="Quantidade de indivíduos no elitismo (padrão: 1)")
    parser.add_argument("-s", "--semente", type=int, default=None, help="Semente para reprodução de experimentos")

    args = parser.parse_args()

    print(f"--- Executando Algoritmo Genético: Mochila Binária ---")
    print(f"Arquivo: {args.arquivo}")
    print(f"Parâmetros: Pop={args.populacao}, Ger={args.geracoes}, Cruzamento={args.cruzamento}, "
          f"Mutação={args.mutacao}, Torneio={args.torneio}, Elite={args.elite}, Semente={args.semente}")

    itens, capacidade = carregar_dados(args.arquivo)

    resultado = executar_algoritmo_genetico(
        itens=itens,
        capacidade=capacidade,
        tamanho_pop=args.populacao,
        num_geracoes=args.geracoes,
        taxa_cruzamento=args.cruzamento,
        taxa_mutacao=args.mutacao,
        tamanho_torneio=args.torneio,
        elite=args.elite,
        semente=args.semente
    )

    sol = resultado["melhor_solucao"]
    print("\n--- Resultado da Melhor Solução Válida ---")
    print(f"Vetor binário: {sol['cromossomo']}")
    print(f"Itens selecionados: {', '.join(sol['itens_selecionados']) if sol['itens_selecionados'] else 'Nenhum'}")
    print(f"Peso Total: {sol['peso']} kg / Capacidade: {capacidade} kg")
    print(f"Valor Total (Utilidade): {sol['valor']}")
    print(f"Geração em que foi encontrada: {sol['geracao_encontrada']}")
    print(f"Tempo de execução: {resultado['tempo_execucao']:.4f} segundos")


if __name__ == "__main__":
    main()
