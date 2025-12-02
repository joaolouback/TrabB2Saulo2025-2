# main.py
import sys
from gramatica import Gramatica
from limpeza import Limpador
from conversao import ConversorCNF

def testar_palavra(gramatica, palavra_alvo):
    """Parte 3: Derivação passo a passo [cite: 30-32]."""
    print(f"\n--- Testando: '{palavra_alvo}' ---")
    fila = [([gramatica.inicial], [])]
    encontrado = False
    max_iter = 5000
    iteracoes = 0
    
    while fila and iteracoes < max_iter:
        iteracoes += 1
        atual, historico = fila.pop(0)
        atual_str = "".join(atual)
        
        # Verifica sucesso
        if sum(1 for x in atual if x in gramatica.terminais) == len(atual):
            if atual_str == palavra_alvo:
                print(f"Palavra encontrada! Passos:")
                print(f"Início: {gramatica.inicial}")
                for r, res in historico:
                    print(f"Aplicando {r} -> {res}")
                print(f"Resultado Final: {atual_str}")
                encontrado = True
                break
            else: continue
            
        if len(atual) > len(palavra_alvo): continue

        # Expansão (Left-Most)
        idx_var = -1
        var_para_expandir = None
        for i, simb in enumerate(atual):
            if simb in gramatica.variaveis:
                idx_var = i; var_para_expandir = simb; break
        
        if var_para_expandir and var_para_expandir in gramatica.regras:
            for prod in gramatica.regras[var_para_expandir]:
                novo_estado = atual[:idx_var] + prod + atual[idx_var+1:]
                regra_str = f"{var_para_expandir} -> {''.join(prod)}"
                fila.append((novo_estado, historico + [(regra_str, "".join(novo_estado))]))

    if not encontrado:
        print(f"Palavra '{palavra_alvo}' não gerada ou limite atingido.")

def main():
    nome_arquivo = 'entrada.txt' # [cite: 11]
    
    try:
        g = Gramatica(nome_arquivo)
    except FileNotFoundError:
        print(f"Erro: Crie o arquivo '{nome_arquivo}' na pasta.")
        return

    print("--- Gramática Original ---")
    print(g.formatar_saida())
    print("-" * 30)

    # Parte 1: Limpeza [cite: 23]
    limpador = Limpador(g)
    limpador.executar()
    print("\n--- Gramática Limpa (Parte 1) [cite: 24] ---")
    print(g.formatar_saida())
    print("-" * 30)

    # Parte 2: Conversão [cite: 26]
    conversor = ConversorCNF(g)
    conversor.executar()
    print("\n--- Gramática FNC (Parte 2) [cite: 27] ---")
    print(g.formatar_saida())
    print("-" * 30)

    # Parte 3: Testes [cite: 28]
    print("\nDigite uma palavra para testar (ou 'sair'):")
    while True:
        entrada = input("> ")
        if entrada.lower() == 'sair': break
        testar_palavra(g, entrada)

if __name__ == "__main__":
    main()