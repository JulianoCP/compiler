import ply.lex as lex
import tokens

tokens = tokens.Toke()

t_SE = r'se'
t_FIM = r'fim'
t_ATE = r'até'
t_LEIA = r'leia'
t_MAIS = r'\+'
t_MENOS = r'-'
t_MENOR = r'<'
t_MAIOR = r'>'
t_IGUAL = r'='
t_ENTAO = r'então'
t_REPITA = r'repita'
t_DIVISAO = r'/'
t_VIRGULA = r','
t_NEGACAO = r'!'
t_ESCREVA = r'escreva'
t_RETORNA = r'retorna'
t_INTEIRO = r'inteiro'
t_E_LOGICO = r'&&'
t_FLUTUANTE = r'flutuante'
t_DIFERENTE = r'<>'
t_OU_LOGICO = r'\|\|'
t_ATRIBUICAO = r':='
t_DOIS_PONTOS = r':'
t_MENOR_IGUAL = r'<='
t_MAIOR_IGUAL = r'>='
t_ABRE_COLCHETE = r'\['
t_MULTIPLICACAO = r'\*'
t_FECHA_COLCHETE = r'\]'
t_ABRE_PARENTESE = r'\('
t_FECHA_PARENTESE = r'\)'

def t_NUM_NOTACAO_CIENTIFICA(t):
    r'\d+\^+\d+'
    t.value = t.value    
    return t

def t_NUM_PONTO_FLUTUANTE(t):
    r'\d+\.\d+' 
    t.value = float(t.value)    
    return t

def t_NUM_INTEIRO(t):
    r'\d+'
    t.value = int(t.value)    
    return t

def t_ID(t):
    r'[aA-zZ]+'
    t.value = str(t.value)    
    return t

def t_newline(t):
    r'\n+'
    t.lexer.lineno += len(t.value)

t_ignore  = ' \t'

def t_error(t):
    print("Illegal character '%s'" % t.value[0])
    t.lexer.skip(1)

# Build the lexer
lexer = lex.lex()

def tokenize(data):

    lexer.input(data)

    while True:
        tok = lexer.token()
        if not tok: 
            break      
        print(tok.type, tok.value)

def main():
    
    f = open("input.tpp","r")
    data = str(f.read())

    tokenize(data)

if __name__ == '__main__':
    main()