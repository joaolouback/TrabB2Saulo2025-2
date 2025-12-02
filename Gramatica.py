import sys
from itertools import chain, combinations

class Gramatica:
    def __init__(self, caminho_arquivo=None):
        self.variaveis = set()
        self.terminais = set()
        self.inicial = None
        self.regras = {}  # Dicionário: {'S': [['a', 'A'], ['eps']]}
        
        if caminho_arquivo:
            self.carregar_do_arquivo(caminho_arquivo)

    def carregar_do_arquivo(self, caminho):
        """Lê o arquivo conforme o formato especificado [cite: 11-22]."""
        with open(caminho, 'r', encoding='utf-8') as f:
            linhas = f.readlines()

        lendo_transicoes = False
        for linha in linhas:
            linha = linha.strip()
            if not linha: continue

            if linha.startswith("Variáveis:"):
                # Lê variáveis (ex: SABCDE) [cite: 12]
                conteudo = linha.split(":")[1].strip()
                self.variaveis = set(list(conteudo))
            
            elif linha.startswith("Terminais:"):
                # Lê terminais, tratando 'eps' [cite: 13, 20]
                conteudo = linha.split(":")[1].strip()
                self.terminais = set()
                # Removemos 'eps' da string para pegar os chars individuais, se houver
                temp = conteudo.replace("eps", "")
                self.terminais = set(list(temp))
                
            elif linha.startswith("Simbolo inicial:"):
                self.inicial = linha.split(":")[1].strip() # [cite: 14]

            elif linha.startswith("Transições:"):
                lendo_transicoes = True # [cite: 15]
                continue

            elif lendo_transicoes:
                # Formato: S aA (espaço é a seta) 
                partes = linha.split()
                if len(partes) >= 2:
                    cabeca = partes[0]
                    corpo_str = partes[1]
                    
                    if cabeca not in self.regras:
                        self.regras[cabeca] = []
                    
                    # Se for eps, tratamos como lista vazia ou marcador especial
                    if corpo_str == "eps":
                        self.regras[cabeca].append(["eps"])
                    else:
                        self.regras[cabeca].append(list(corpo_str))

    def formatar_saida(self):
        """Gera a string no formato do arquivo de entrada[cite: 24, 27]."""
        saida = []
        saida.append(f"Variáveis: {''.join(sorted(list(self.variaveis)))}")
        # Reconstrói string de terminais
        term_str = ''.join(sorted(list(self.terminais))) + "eps"
        saida.append(f"Terminais: {term_str}")
        saida.append(f"Simbolo inicial: {self.inicial}")
        saida.append("Transições:")
        
        for cabeca, producoes in self.regras.items():
            for prod in producoes:
                corpo = "".join(prod)
                saida.append(f"{cabeca} {corpo}")
        return "\n".join(saida)

    # --- PARTE 1: LIMPEZA ---
    
    def remover_producoes_vazias(self):
        """1º Passo: Remover produções-vazias."""
        anulaveis = set()
        
        # Encontrar variáveis anuláveis
        mudou = True
        while mudou:
            mudou = False
            for cabeca, producoes in self.regras.items():
                if cabeca in anulaveis: continue
                for prod in producoes:
                    # Se for eps ou todos os simbolos da produção já são anuláveis
                    if prod == ["eps"] or all(s in anulaveis for s in prod):
                        anulaveis.add(cabeca)
                        mudou = True
                        break
        
        # Gerar novas regras
        novas_regras = {}
        for cabeca, producoes in self.regras.items():
            novas_regras[cabeca] = []
            for prod in producoes:
                if prod == ["eps"]: continue # Remove epsilon direto
                
                # Gera combinações se houver variáveis anuláveis na produção
                indices_anulaveis = [i for i, x in enumerate(prod) if x in anulaveis]
                # Power set dos índices
                for i in range(len(indices_anulaveis) + 1):
                    for combo in combinations(indices_anulaveis, i):
                        # Cria nova produção removendo os anuláveis escolhidos
                        indices_para_remover = set(combo)
                        nova_prod = [x for k, x in enumerate(prod) if k not in indices_para_remover]
                        if nova_prod and nova_prod not in novas_regras[cabeca]:
                            novas_regras[cabeca].append(nova_prod)
        
        # Se o inicial era anulável, adicionar S -> eps (opcional, dependendo da definição estrita)
        if self.inicial in anulaveis:
            if self.inicial not in novas_regras: novas_regras[self.inicial] = []
            novas_regras[self.inicial].append(["eps"])

        self.regras = novas_regras

    def remover_producoes_unidade(self):
        """2º Passo: Remover produções-unidade (A -> B)[cite: 7]."""
        # Identificar pares unitários (A, B) tal que A =>* B
        unitarios = {} # Mapa var -> set(vars alcancaveis por unitario)
        for var in self.variaveis:
            unitarios[var] = {var}
        
        mudou = True
        while mudou:
            mudou = False
            for A in self.variaveis:
                if A not in self.regras: continue
                for prod in self.regras[A]:
                    if len(prod) == 1 and prod[0] in self.variaveis:
                        B = prod[0]
                        # Tudo que B alcança, A também alcança
                        antes = len(unitarios[A])
                        unitarios[A].update(unitarios[B])
                        if len(unitarios[A]) > antes:
                            mudou = True

        novas_regras = {}
        for A in self.variaveis:
            novas_regras[A] = []
            # Para cada B alcançável por A (incluindo o próprio A)
            for B in unitarios.get(A, []):
                if B in self.regras:
                    for prod in self.regras[B]:
                        # Se não for unitária, adiciona a A
                        if not (len(prod) == 1 and prod[0] in self.variaveis):
                            if prod not in novas_regras[A]:
                                novas_regras[A].append(prod)
        
        self.regras = novas_regras

    def remover_producoes_inuteis(self):
        """3º Passo: Remover inúteis (não geradores e inalcançáveis)[cite: 8]."""
        # 1. Identificar Geradores (alcançam terminais)
        geradores = set()
        mudou = True
        while mudou:
            mudou = False
            for cabeca, producoes in self.regras.items():
                if cabeca in geradores: continue
                for prod in producoes:
                    # Se todos os simbolos são terminais ou variáveis geradoras
                    if all((s in self.terminais or s in geradores) for s in prod):
                        geradores.add(cabeca)
                        mudou = True
                        break
        
        # Limpar regras não geradoras
        regras_temp = {}
        for cabeca in geradores:
            regras_temp[cabeca] = []
            for prod in self.regras.get(cabeca, []):
                if all((s in self.terminais or s in geradores) for s in prod):
                    regras_temp[cabeca].append(prod)
        self.regras = regras_temp
        self.variaveis = self.variaveis.intersection(geradores)

        # 2. Identificar Alcançáveis (a partir de S)
        alcancaveis = {self.inicial}
        fila = [self.inicial]
        
        while fila:
            atual = fila.pop(0)
            if atual in self.regras:
                for prod in self.regras[atual]:
                    for simb in prod:
                        if simb in self.variaveis and simb not in alcancaveis:
                            alcancaveis.add(simb)
                            fila.append(simb)
        
        # Limpar inalcançáveis
        regras_final = {}
        for cabeca in alcancaveis:
            if cabeca in self.regras:
                regras_final[cabeca] = self.regras[cabeca]
        
        self.regras = regras_final
        self.variaveis = self.variaveis.intersection(alcancaveis)

    def limpar_gramatica(self):
        """Executa a sequência de limpeza completa[cite: 4, 5]."""
        self.remover_producoes_vazias()
        self.remover_producoes_unidade()
        self.remover_producoes_inuteis()

    # --- PARTE 2: FORMA NORMAL DE CHOMSKY ---

    def converter_para_cnf(self):
        """Converte a gramática limpa para FNC[cite: 26]."""
        # Passo 1: Garantir que terminais apareçam sozinhos (ex: A -> aB vira A -> XB, X -> a)
        novas_vars = {} # map terminal -> nova_variavel
        contador_var = 1
        
        # Copia segura das regras
        regras_atuais = list(self.regras.items())
        self.regras = {k: [] for k in self.variaveis}
        
        for cabeca, producoes in regras_atuais:
            for prod in producoes:
                nova_prod = []
                if len(prod) > 1:
                    for simb in prod:
                        if simb in self.terminais:
                            # Criar ou reusar variável para este terminal
                            if simb not in novas_vars:
                                nome_var = f"X{simb.upper()}" # Ex: XA para 'a'
                                while nome_var in self.variaveis:
                                    nome_var = f"X{contador_var}"
                                    contador_var += 1
                                novas_vars[simb] = nome_var
                                self.variaveis.add(nome_var)
                                self.regras[nome_var] = [[simb]]
                            nova_prod.append(novas_vars[simb])
                        else:
                            nova_prod.append(simb)
                else:
                    nova_prod = prod
                self.regras[cabeca].append(nova_prod)

        # Passo 2: Quebrar produções longas (len > 2)
        # Ex: A -> BCD vira A -> BZ, Z -> CD
        mudou = True
        while mudou:
            mudou = False
            regras_temp = self.regras.copy()
            for cabeca, producoes in regras_temp.items():
                novas_producoes = []
                for prod in producoes:
                    if len(prod) > 2:
                        mudou = True
                        # Quebra: pega os 2 últimos
                        resto = prod[1:]
                        primeiro = prod[0]
                        
                        # Cria nova variável para o resto
                        nova_var = f"Y{contador_var}"
                        contador_var += 1
                        self.variaveis.add(nova_var)
                        self.regras[nova_var] = [resto]
                        
                        novas_producoes.append([primeiro, nova_var])
                    else:
                        novas_producoes.append(prod)
                self.regras[cabeca] = novas_producoes

    # --- PARTE 3: TESTE / DERIVAÇÃO ---

    def testar_palavra(self, palavra_alvo):
        """
        Tenta gerar a palavra passo a passo.
        Nota: Isso simula uma derivação Left-Most (mais à esquerda).
        [cite: 30, 31, 32]
        """
        print(f"\n--- Testando palavra: '{palavra_alvo}' ---")
        
        # Estrutura da fila: (string_atual_lista, historico_derivacao)
        # string_atual_lista contém terminais e variáveis.
        fila = [([self.inicial], [])]
        
        iteracoes = 0
        max_iter = 5000 # Segurança contra loops infinitos
        
        encontrado = False
        
        while fila and iteracoes < max_iter:
            iteracoes += 1
            atual, historico = fila.pop(0) # BFS para encontrar a menor derivação
            
            # Converte lista atual para string para comparação
            atual_str = "".join(atual)
            
            # Verifica se chegamos na palavra (somente terminais)
            terminais_count = sum(1 for x in atual if x in self.terminais)
            if terminais_count == len(atual):
                if atual_str == palavra_alvo:
                    # Sucesso! Imprimir passos
                    print(f"Palavra encontrada! Passos:")
                    curr_str = self.inicial
                    print(f"Início: {curr_str}")
                    for passo in historico:
                        # passo = (regra_aplicada, string_resultante)
                        print(f"Aplicando {passo[0]} -> {passo[1]}")
                    print(f"Resultado Final: {atual_str}")
                    encontrado = True
                    break
                else:
                    continue # Palavra de terminais errada
            
            # Se a string atual já for maior que a alvo (e não tiver eps), descarta (poda)
            if len(atual) > len(palavra_alvo):
                continue

            # Encontra a variável mais à esquerda (Derivação Left-Most)
            idx_var = -1
            var_para_expandir = None
            for i, simb in enumerate(atual):
                if simb in self.variaveis:
                    idx_var = i
                    var_para_expandir = simb
                    break
            
            if var_para_expandir:
                if var_para_expandir in self.regras:
                    for prod in self.regras[var_para_expandir]:
                        novo_estado = atual[:idx_var] + prod + atual[idx_var+1:]
                        nova_str_res = "".join(novo_estado)
                        # Regra formatada: A -> BC
                        regra_str = f"{var_para_expandir} -> {''.join(prod)}"
                        novo_hist = historico + [(regra_str, nova_str_res)]
                        fila.append((novo_estado, novo_hist))

        if not encontrado:
            print(f"Não foi possível gerar a palavra '{palavra_alvo}' (ou limite de iterações atingido).")

# --- EXECUÇÃO ---

def main():
    # 1. Carregar
    # Substitua 'input.txt' pelo nome exato do seu arquivo na pasta
    nome_arquivo = 'entrada.txt' 
    print(f"Lendo arquivo: {nome_arquivo}...\n")
    
    try:
        g = Gramatica(nome_arquivo)
    except FileNotFoundError:
        print("Erro: Arquivo não encontrado. Crie um arquivo 'entrada.txt' com o conteúdo do PDF.")
        return

    print("--- Gramática Original ---")
    print(g.formatar_saida())
    print("-" * 30)

    # 2. Limpeza (Parte 1)
    g.limpar_gramatica()
    print("\n--- Gramática Limpa (Parte 1) --- ")
    print(g.formatar_saida())
    print("-" * 30)

    # 3. Conversão CNF (Parte 2)
    g.converter_para_cnf()
    print("\n--- Gramática na Forma Normal de Chomsky (Parte 2) --- [cite: 27]")
    print(g.formatar_saida())
    print("-" * 30)

    # 4. Testes (Parte 3)
    # Lista de palavras para testar (edite conforme necessário)
    palavras_teste = ["aa", "abba", "ba"] # Exemplo
    
    print("\nDigite uma palavra para testar (ou 'sair'):")
    while True:
        entrada = input("> ")
        if entrada.lower() == 'sair': break
        g.testar_palavra(entrada)

if __name__ == "__main__":
    main()