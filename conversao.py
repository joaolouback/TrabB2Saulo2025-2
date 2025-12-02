# conversao.py

class ConversorCNF:
    def __init__(self, gramatica):
        self.g = gramatica
        self.contador_var = 1

    def executar(self):
        """Converte a gramática limpa para Forma Normal de Chomsky."""
        self._isolar_terminais()
        self._quebrar_producoes_longas()

    def _isolar_terminais(self):
        # Garante que terminais apareçam sozinhos ou em produções unitárias
        novas_vars = {} 
        regras_atuais = list(self.g.regras.items())
        self.g.regras = {k: [] for k in self.g.variaveis}
        
        for cabeca, producoes in regras_atuais:
            for prod in producoes:
                nova_prod = []
                if len(prod) > 1:
                    for simb in prod:
                        if simb in self.g.terminais:
                            if simb not in novas_vars:
                                nome_var = f"X{simb.upper()}"
                                while nome_var in self.g.variaveis:
                                    nome_var = f"X{self.contador_var}"
                                    self.contador_var += 1
                                novas_vars[simb] = nome_var
                                self.g.variaveis.add(nome_var)
                                self.g.regras[nome_var] = [[simb]]
                            nova_prod.append(novas_vars[simb])
                        else:
                            nova_prod.append(simb)
                else:
                    nova_prod = prod
                self.g.regras[cabeca].append(nova_prod)

    def _quebrar_producoes_longas(self):
        mudou = True
        while mudou:
            mudou = False
            regras_temp = self.g.regras.copy()
            for cabeca, producoes in regras_temp.items():
                novas_producoes = []
                for prod in producoes:
                    if len(prod) > 2:
                        mudou = True
                        resto = prod[1:]
                        primeiro = prod[0]
                        nova_var = f"Y{self.contador_var}"
                        self.contador_var += 1
                        self.g.variaveis.add(nova_var)
                        self.g.regras[nova_var] = [resto]
                        novas_producoes.append([primeiro, nova_var])
                    else:
                        novas_producoes.append(prod)
                self.g.regras[cabeca] = novas_producoes