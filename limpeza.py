# limpeza.py
from itertools import combinations

class Limpador:
    def __init__(self, gramatica):
        self.g = gramatica

    def executar(self):
        """Executa a sequência de limpeza: Vazias -> Unitárias -> Inúteis."""
        self._remover_vazias()
        self._remover_unitarias()
        self._remover_inuteis()

    def _remover_vazias(self):
        # 1. Identificar anuláveis
        anulaveis = set()
        mudou = True
        while mudou:
            mudou = False
            for cabeca, producoes in self.g.regras.items():
                if cabeca in anulaveis: continue
                for prod in producoes:
                    if prod == ["eps"] or all(s in anulaveis for s in prod):
                        anulaveis.add(cabeca)
                        mudou = True
                        break
        
        # 2. Gerar novas regras sem eps
        novas_regras = {}
        for cabeca, producoes in self.g.regras.items():
            novas_regras[cabeca] = []
            for prod in producoes:
                if prod == ["eps"]: continue
                indices_anulaveis = [i for i, x in enumerate(prod) if x in anulaveis]
                for i in range(len(indices_anulaveis) + 1):
                    for combo in combinations(indices_anulaveis, i):
                        indices_para_remover = set(combo)
                        nova_prod = [x for k, x in enumerate(prod) if k not in indices_para_remover]
                        if nova_prod and nova_prod not in novas_regras[cabeca]:
                            novas_regras[cabeca].append(nova_prod)
        
        if self.g.inicial in anulaveis:
             if self.g.inicial not in novas_regras: novas_regras[self.g.inicial] = []
             novas_regras[self.g.inicial].append(["eps"])
             
        self.g.regras = novas_regras

    def _remover_unitarias(self):
        unitarios = {v: {v} for v in self.g.variaveis}
        mudou = True
        while mudou:
            mudou = False
            for A in self.g.variaveis:
                if A not in self.g.regras: continue
                for prod in self.g.regras[A]:
                    if len(prod) == 1 and prod[0] in self.g.variaveis:
                        B = prod[0]
                        antes = len(unitarios[A])
                        unitarios[A].update(unitarios[B])
                        if len(unitarios[A]) > antes: mudou = True

        novas_regras = {}
        for A in self.g.variaveis:
            novas_regras[A] = []
            for B in unitarios.get(A, []):
                if B in self.g.regras:
                    for prod in self.g.regras[B]:
                        if not (len(prod) == 1 and prod[0] in self.g.variaveis):
                            if prod not in novas_regras[A]: novas_regras[A].append(prod)
        self.g.regras = novas_regras

    def _remover_inuteis(self):
        # 1. Geradores
        geradores = set()
        mudou = True
        while mudou:
            mudou = False
            for cabeca, producoes in self.g.regras.items():
                if cabeca in geradores: continue
                for prod in producoes:
                    if all((s in self.g.terminais or s in geradores) for s in prod):
                        geradores.add(cabeca)
                        mudou = True; break
        
        regras_temp = {}
        for cabeca in geradores:
            regras_temp[cabeca] = [p for p in self.g.regras.get(cabeca, []) 
                                   if all((s in self.g.terminais or s in geradores) for s in p)]
        self.g.regras = regras_temp
        self.g.variaveis = self.g.variaveis.intersection(geradores)

        # 2. Alcançáveis
        alcancaveis = {self.g.inicial}
        fila = [self.g.inicial]
        while fila:
            atual = fila.pop(0)
            if atual in self.g.regras:
                for prod in self.g.regras[atual]:
                    for s in prod:
                        if s in self.g.variaveis and s not in alcancaveis:
                            alcancaveis.add(s); fila.append(s)
        
        regras_final = {k: v for k, v in self.g.regras.items() if k in alcancaveis}
        self.g.regras = regras_final
        self.g.variaveis = self.g.variaveis.intersection(alcancaveis)