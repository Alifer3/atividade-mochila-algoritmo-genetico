import os
import csv
import matplotlib.pyplot as plt
from algoritmo_genetico import carregar_dados, executar_algoritmo_genetico

def main():
    os.makedirs("graficos", exist_ok=True)
    sementes = [1, 2, 3, 4, 5]

    entradas = [
        ("entrada_01.csv", "entradas/entrada_01.csv"),
        ("entrada_02.csv", "entradas/entrada_02.csv"),
        ("entrada_03.csv", "entradas/entrada_03.csv"),
        ("entrada_04.csv", "entradas/entrada_04.csv"),
        ("entrada_05.csv", "entradas/entrada_05.csv")
    ]

    # Experimentos a realizar:
    # 1. Configuração padrão nas 5 entradas
    # 2. Entrada 05 com mutação = 0.01
    # 3. Entrada 05 com população = 100

    experimentos = []

    # Configuração Padrão
    for nome_arq, caminho in entradas:
        experimentos.append({
            "nome_config": "Padrão (Pop=50, Mut=0.05)",
            "arquivo_nome": nome_arq,
            "caminho": caminho,
            "populacao": 50,
            "mutacao": 0.05,
            "geracoes": 100,
            "cruzamento": 0.8,
            "torneio": 3,
            "elite": 1
        })

    # Variações para entrada_05
    experimentos.append({
        "nome_config": "Mutação Reduzida (Pop=50, Mut=0.01)",
        "arquivo_nome": "entrada_05.csv",
        "caminho": "entradas/entrada_05.csv",
        "populacao": 50,
        "mutacao": 0.01,
        "geracoes": 100,
        "cruzamento": 0.8,
        "torneio": 3,
        "elite": 1
    })

    experimentos.append({
        "nome_config": "População Aumentada (Pop=100, Mut=0.05)",
        "arquivo_nome": "entrada_05.csv",
        "caminho": "entradas/entrada_05.csv",
        "populacao": 100,
        "mutacao": 0.05,
        "geracoes": 100,
        "cruzamento": 0.8,
        "torneio": 3,
        "elite": 1
    })

    tabela_resumo = []
    detalhes_melhores_por_entrada = {}
    historicos_graficos = {}

    print("=== INICIANDO EXECUÇÃO DOS EXPERIMENTOS ===")

    for exp in experimentos:
        print(f"\nRodando: {exp['arquivo_nome']} | Config: {exp['nome_config']}")
        itens, capacidade = carregar_dados(exp["caminho"])

        valores_execucoes = []
        tempos_execucoes = []
        melhor_execucao_exp = None

        for semente in sementes:
            res = executar_algoritmo_genetico(
                itens=itens,
                capacidade=capacidade,
                tamanho_pop=exp["populacao"],
                num_geracoes=exp["geracoes"],
                taxa_cruzamento=exp["cruzamento"],
                taxa_mutacao=exp["mutacao"],
                tamanho_torneio=exp["torneio"],
                elite=exp["elite"],
                semente=semente
            )

            sol = res["melhor_solucao"]
            valores_execucoes.append(sol["valor"])
            tempos_execucoes.append(res["tempo_execucao"])

            if melhor_execucao_exp is None or sol["valor"] > melhor_execucao_exp["solucao"]["valor"]:
                melhor_execucao_exp = {
                    "semente": semente,
                    "solucao": sol,
                    "capacidade": capacidade,
                    "historico": res["historico_melhor_valido"],
                    "tempo": res["tempo_execucao"]
                }

            # Guardar histórico da semente 1 para cada entrada (ou melhor histórico) para o gráfico
            chave_hist = f"{exp['arquivo_nome']}_{exp['nome_config']}_s{semente}"
            historicos_graficos[chave_hist] = res["historico_melhor_valido"]

        maior_val = max(valores_execucoes)
        media_val = sum(valores_execucoes) / len(valores_execucoes)
        tempo_medio = sum(tempos_execucoes) / len(tempos_execucoes)

        tabela_resumo.append({
            "Configuração": exp["nome_config"],
            "Entrada": exp["arquivo_nome"],
            "Sem_1": valores_execucoes[0],
            "Sem_2": valores_execucoes[1],
            "Sem_3": valores_execucoes[2],
            "Sem_4": valores_execucoes[3],
            "Sem_5": valores_execucoes[4],
            "Maior_Valor": maior_val,
            "Media_Valor": round(media_val, 2),
            "Tempo_Medio_s": round(tempo_medio, 5)
        })

        # Armazenar a melhor solução global para cada entrada (na config padrão)
        nome_arq = exp["arquivo_nome"]
        if exp["nome_config"].startswith("Padrão"):
            detalhes_melhores_por_entrada[nome_arq] = melhor_execucao_exp

    # Salvar tabela CSV
    with open("resultados_experimentos.csv", "w", newline="", encoding="utf-8") as f:
        colunas = ["Configuração", "Entrada", "Sem_1", "Sem_2", "Sem_3", "Sem_4", "Sem_5", "Maior_Valor", "Media_Valor", "Tempo_Medio_s"]
        writer = csv.DictWriter(f, fieldnames=colunas)
        writer.writeheader()
        writer.writerows(tabela_resumo)

    print("\n=== TABELA DE RESULTADOS DOS EXPERIMENTOS ===")
    print(f"{'Configuração':<38} | {'Entrada':<15} | {'S1':<4} {'S2':<4} {'S3':<4} {'S4':<4} {'S5':<4} | {'Maior':<6} | {'Média':<7} | {'Tempo Médio (s)':<15}")
    print("-" * 110)
    for linha in tabela_resumo:
        print(f"{linha['Configuração']:<38} | {linha['Entrada']:<15} | {linha['Sem_1']:<4} {linha['Sem_2']:<4} {linha['Sem_3']:<4} {linha['Sem_4']:<4} {linha['Sem_5']:<4} | {linha['Maior_Valor']:<6} | {linha['Media_Valor']:<7} | {linha['Tempo_Medio_s']:<15}")

    print("\n=== MELHOR EXECUÇÃO DE CADA ENTRADA (CONFIGURAÇÃO PADRÃO) ===")
    for nome_arq, dados in detalhes_melhores_por_entrada.items():
        sol = dados["solucao"]
        print(f"\nEntrada: {nome_arq}")
        print(f"  Semente: {dados['semente']}")
        print(f"  Vetor binário: {sol['cromossomo']}")
        print(f"  Itens selecionados: {', '.join(sol['itens_selecionados'])}")
        print(f"  Peso total: {sol['peso']} kg / Capacidade: {dados['capacidade']} kg")
        print(f"  Valor total: {sol['valor']}")

    # Geração dos Gráficos de Evolução
    print("\n=== GERANDO GRÁFICOS DE EVOLUÇÃO ===")
    # 1 gráfico para cada uma das 5 entradas
    for idx in range(1, 6):
        nome_csv = f"entrada_0{idx}.csv"
        plt.figure(figsize=(10, 6))

        # Plotar as 5 sementes da configuração padrão para demonstrar estocasticidade e convergência
        cores = ["#1f77b4", "#ff7f0e", "#2ca02c", "#d62728", "#9467bd"]
        for s, cor in zip(sementes, cores):
            chave = f"{nome_csv}_Padrão (Pop=50, Mut=0.05)_s{s}"
            hist = historicos_graficos[chave]
            plt.plot(hist, label=f"Semente {s} (Final: {hist[-1]})", color=cor, alpha=0.8, linewidth=1.8)

        plt.title(f"Evolução da Melhor Aptidão Válida - {nome_csv} (Configuração Padrão)", fontsize=14, fontweight="bold")
        plt.xlabel("Geração", fontsize=12)
        plt.ylabel("Melhor Valor Válido (Utilidade)", fontsize=12)
        plt.grid(True, linestyle="--", alpha=0.6)
        plt.legend(title="Execuções", loc="lower right", frameon=True)
        plt.tight_layout()
        caminho_grafico = f"graficos/evolucao_entrada_0{idx}.png"
        plt.savefig(caminho_grafico, dpi=300)
        plt.close()
        print(f"Gráfico salvo: {caminho_grafico}")

    # Gráfico comparativo extra para a entrada 05 (Padrão vs Mut=0.01 vs Pop=100)
    plt.figure(figsize=(10, 6))
    for semente, estilo in zip([1, 2, 3], ["-", "--", ":"]):
        h_padrao = historicos_graficos[f"entrada_05.csv_Padrão (Pop=50, Mut=0.05)_s{semente}"]
        h_mut = historicos_graficos[f"entrada_05.csv_Mutação Reduzida (Pop=50, Mut=0.01)_s{semente}"]
        h_pop = historicos_graficos[f"entrada_05.csv_População Aumentada (Pop=100, Mut=0.05)_s{semente}"]

        if semente == 1:
            plt.plot(h_padrao, label="Padrão (Pop=50, Mut=0.05)", color="#1f77b4", linewidth=2)
            plt.plot(h_mut, label="Mutação Reduzida (Mut=0.01)", color="#ff7f0e", linewidth=2)
            plt.plot(h_pop, label="População Aumentada (Pop=100)", color="#2ca02c", linewidth=2)
        else:
            plt.plot(h_padrao, color="#1f77b4", alpha=0.5, linestyle=estilo)
            plt.plot(h_mut, color="#ff7f0e", alpha=0.5, linestyle=estilo)
            plt.plot(h_pop, color="#2ca02c", alpha=0.5, linestyle=estilo)

    plt.title("Comparação de Configurações - entrada_05.csv (Semente 1 em destaque)", fontsize=13, fontweight="bold")
    plt.xlabel("Geração", fontsize=12)
    plt.ylabel("Melhor Valor Válido (Utilidade)", fontsize=12)
    plt.grid(True, linestyle="--", alpha=0.6)
    plt.legend(title="Configurações", loc="lower right", frameon=True)
    plt.tight_layout()
    caminho_comp = "graficos/comparativo_entrada_05.png"
    plt.savefig(caminho_comp, dpi=300)
    plt.close()
    print(f"Gráfico salvo: {caminho_comp}")

    print("\nExperimentos concluídos com sucesso!")

if __name__ == "__main__":
    main()
