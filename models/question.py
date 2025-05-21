class Question:
    def __init__(self, text, options, correct_option, difficulty):
        self.text = text
        self.options = options
        self.correct_option = correct_option
        self.difficulty = difficulty
        self.used_help = {
            "skip": False,
            "eliminate": False,
            "hint": False
        }
        # Adicionando dicas para cada pergunta
        self.hint = self.generate_hint()

    def generate_hint(self):
        # Gerando dicas baseadas no assunto e dificuldade
        if "Matematica" in self.text:
            if "7 x 8" in self.text:
                return "Dica: Lembre-se da tabuada do 7 ou do 8."
            elif "área de um círculo" in self.text:
                return "Dica: A fórmula da área do círculo é π vezes raio ao quadrado."
            elif "equação 2x²" in self.text:
                return "Dica: Use a fórmula de Bhaskara para resolver equações quadráticas."
        elif "Fisica" in self.text:
            if "unidade de medida da força" in self.text:
                return "Dica: A unidade recebeu o nome de um famoso cientista."
            elif "lançado verticalmente" in self.text:
                return "Dica: No ponto mais alto, a velocidade vertical é zero, mas a aceleração continua."
            elif "capacitor de placas paralelas" in self.text:
                return "Dica: A capacitância é inversamente proporcional à distância entre as placas."
        return "Dica: Pense cuidadosamente sobre o tema da pergunta."