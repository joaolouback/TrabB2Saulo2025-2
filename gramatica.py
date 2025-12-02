# gramatica.py

class Gramatica:
    def __init__(self, caminho_arquivo=None):
        self.variaveis = set()
        self.terminais = set()
        self.inicial = None
        self.regras = {}  # Ex: {'S': [['a', 'A'], ['eps']]}
        
        if caminho_arquivo:
            self.carregar_do_arquivo(caminho_arquivo)

    def carregar_do_arquivo(self, caminho):
        """
        Lê o arquivo no formato simplificado:
        Linha 1: Variáveis (espaço)
        Linha 2: Terminais (espaço)
        Linha 3: Símbolo Inicial
        Linha 4+: Regras (Cabeça Corpo)
        """
        with open(caminho, 'r', encoding='utf-8') as f:
            # Lê todas as linhas removendo espaços em branco extras nas pontas
            linhas = [l.strip() for l in f.readlines() if l.strip()]

        if len(linhas) < 4:
            raise ValueError("O arquivo de entrada está incompleto ou vazio.")

        # Linha 1: Variáveis (ex: X Y Z K W T)
        self.variaveis = set(linhas[0].split())

        # Linha 2: Terminais (ex: a b c)
        # Nota: removemos 'eps' caso esteja listado nos terminais por engano,
        # pois eps é tratado internamente como vazio.
        term_list = linhas[1].split()
        self.terminais = set([t for t in term_list if t != 'eps'])

        # Linha 3: Símbolo Inicial (ex: X)
        self.inicial = linhas[2].strip()

        # Linha 4 em diante: Regras (ex: X KW)
        for linha in linhas[3:]:
            partes = linha.split()
            
            # Formato esperado: CABECA CORPO
            if len(partes) >= 1:
                cabeca = partes[0]
                
                # Se tiver corpo, pega. Se não (linha incompleta?), ignora ou trata como vazio
                if len(partes) >= 2:
                    corpo_str = partes[1]
                else:
                    # Caso raro: regra sem corpo explícito seria vazio?
                    # Assumindo formato padrão "S eps" para vazio.
                    corpo_str = "" 

                if cabeca not in self.regras:
                    self.regras[cabeca] = []
                
                # Tratamento do Epsilon
                if corpo_str == "eps":
                    self.regras[cabeca].append(["eps"])
                else:
                    # Transforma string em lista: "KW" -> ['K', 'W']
                    self.regras[cabeca].append(list(corpo_str))

    def formatar_saida(self):
        """
        Gera a string de saída NO MESMO FORMATO do arquivo de entrada.
        """
        saida = []
        
        # 1. Variáveis ordenadas
        saida.append(" ".join(sorted(list(self.variaveis))))
        
        # 2. Terminais ordenados
        saida.append(" ".join(sorted(list(self.terminais))))
        
        # 3. Inicial
        saida.append(str(self.inicial))
        
        # 4. Transições
        for cabeca in sorted(list(self.regras.keys())):
            producoes = self.regras[cabeca]
            for prod in producoes:
                # Se for lista vazia ou ['eps'], imprime 'eps'
                if prod == ["eps"]:
                    corpo = "eps"
                else:
                    corpo = "".join(prod)
                
                saida.append(f"{cabeca} {corpo}")
                
        return "\n".join(saida)