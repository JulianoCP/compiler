from sys import argv, exit
import math
from mytree import MyNode
from anytree.exporter import DotExporter, UniqueDotExporter
from anytree import RenderTree, AsciiStyle
import sintatico

listOfParents = []
listOfTerminals = []
listOfTypes = []
listVariableDeclared = []
listFuncDeclared = []
listVariableInitiated = []
listFuncCheckedReturn = []
listCreateResumeTree = []
tempListOfTerminals = []
tempListOfParents = []
tempCabecalhoFunc = None
tempParentGenerateTree = []
tempListLinkParentsInTree = []
tempNewRoot = None
tempOldRoot = None

def runAllRules():
    print("\n                                 - SAIDA DE ERROS -")
    print("=====================================================================================\n")
    r_declared_variable()
    r_main_func()
    r_declared_func()
    r_verify_assignment()
    r_callfunc_num_param()
    r_verify_read()
    print("\n=====================================================================================\n")
    table_generator()

def walkNodeTree(node):
    tempListOfTerminals.clear()
    tempListOfParents.clear()
    walkNode(node)

def walkNode(node):
    if len(node.children) >= 1:
        tempListOfParents.append(node)
        for i in node.children:
            walkNode(i)
    else:
        tempListOfTerminals.append(node)

def walkTree(rootChildren):
    if len(rootChildren.children) >= 1:
        listOfParents.append(rootChildren)
        for i in rootChildren.children:
            walkTree(i)
    else:
        listOfTerminals.append(rootChildren)

def r_main_func():
    for i in listOfTerminals:
        if i.name == "principal":
            temp = [0,0,-1,"global","global","funcao","global"]
            temp[0] = i.parent.parent.parent.children[0].children[0].children[0]
            temp[1] = i
            temp[4] = i.name
            listOfTypes.append(temp)
            r_func_retorn(i.parent.parent,i.name)
            return
    print("Erro: Função principal não declarada")

def r_func_retorn(node,name):
    temp = None
    if node == -1:
        print("Erro: Chamada a função ‘{}’ que não foi declarada".format(name))
        return -1
    for i in listFuncCheckedReturn:
        if i == name:
            return -1
    for i in node.children:
        if i.name == "corpo":
            walkNodeTree(i)
            for j in tempListOfParents:
                if j.name == "retorna":
                    if j.parent.parent.parent.name == "cabecalho":
                        walkNodeTree(j)
                        for k in tempListOfParents:
                            if k.name == "expressao":
                                walkNodeTree(k)
                                for l in tempListOfTerminals:
                                    if l.parent.name == "ID":
                                        temp = r_variable_declared(l,name)
                                        if temp != -1:
                                            if temp[0].name != node.parent.children[0].children[0].children[0].name:
                                                if node.parent.children[0].name != "cabecalho":
                                                    print("Aviso: Função ‘{}’ deveria retornar {}, mas retorna {}".format(name,node.parent.children[0].children[0].children[0].name,temp[0].name))
                                                else:
                                                    print("Erro: Função ‘{}’ do tipo vazio retornando {}".format(name,temp[0].name))
                        listFuncCheckedReturn.append(name)
                        return
    print("Erro: Função ‘{}’ deveria retornar inteiro, mas retorna vazio".format(name))

def r_find_func(name):
    for i in listOfParents:
        if i.name == "declaracao_funcao":
            for j in i.children:
                if j.name == "cabecalho":
                    if j.children[0].children[0].name == name:
                        return j
    return -1

def r_num_param_func(node):
    temp = 0
    for i in node.children:
        if i.name == "lista_parametros":
            walkNodeTree(i)
            for j in tempListOfParents:
                if j.name == "parametro":
                    temp += 1
            return temp
    return temp

def r_num_param_callfunc(node):
    temp = 0
    for i in node.children:
        if i.name == "lista_argumentos":
            walkNodeTree(i)
            for j in tempListOfParents:
                if j.name == "expressao":
                    temp += 1
            return temp
    return temp

def r_find_cabe_func(node):
    global tempCabecalhoFunc
    tempCabecalhoFunc = None
    r_find_cabe_func_walkTree(node)

def r_find_cabe_func_walkTree(node):
    if node.name == "cabecalho":
        global tempCabecalhoFunc
        tempCabecalhoFunc = node
        return
    else:
        if node.parent.name != "programa":
            r_find_cabe_func(node.parent)
        else:
            return

def r_callfunc_num_param():
    for i in listOfParents:
        if i.name == "chamada_funcao":
            r_find_cabe_func(i)
            if tempCabecalhoFunc.children[0].children[0].name != "principal" and i.children[0].children[0].name == "principal":
                print("Erro: Chamada para a função ‘principal’ não permitida")
            elif tempCabecalhoFunc.children[0].children[0].name == "principal" and i.children[0].children[0].name == "principal":
                print("Aviso: Chamada recursiva para ‘principal’")
            if i.children[0].children[0].name != "principal":
                has_retorn_func = r_func_retorn(r_find_func(i.children[0].children[0].name),i.children[0].children[0].name)
                if has_retorn_func != -1:
                    numParamOriginFunc = r_num_param_func(r_find_func(i.children[0].children[0].name))
                    numParamCallFunc = r_num_param_callfunc(i)
                    if numParamOriginFunc > numParamCallFunc:
                        print("Erro: Chamada à função ‘{}’ com número de parâmetros menor que o declarado".format(i.children[0].children[0].name))
                    elif numParamOriginFunc < numParamCallFunc:
                        print("Erro: Chamada à função ‘{}’ com número de parâmetros maior que o declarado".format(i.children[0].children[0].name))

def r_declared_func():
    for i in listOfParents:
        if i.name == "declaracao_funcao":
            if i.children[0].children[0].name != "ID":
                if i.children[1].children[0].children[0].name != "principal":
                    temp = [0,0,-1,"global","global","funcao","global"]
                    temp[0] = i.children[0].children[0].children[0]
                    temp[1] = i.children[1].children[0].children[0]
                    temp[4] = i.children[1].children[0].children[0].name
                    listOfTypes.append(temp)
                    listFuncDeclared.append(temp[1])
            else:
                if i.children[0].children[0].children[0].name != "principal":
                    temp = [0,0,-1,"global","global","funcao","global"]
                    temp[0] = "vazio"
                    temp[1] = i.children[0].children[0].children[0]
                    temp[4] = i.children[0].children[0].children[0].name
                    listOfTypes.append(temp)
                    listFuncDeclared.append(temp[1])
    r_unused_declared_func()

def r_unused_declared_func():
    for i in listOfTerminals:
        for j in listFuncDeclared:
            if i.name == j.name:
                if i.parent.parent.parent != j.parent.parent.parent:
                    listFuncDeclared.remove(j)
    for i in listFuncDeclared:
        print("Aviso: Função ‘{}’ declarada, mas não utilizada".format(i.name))
        r_func_retorn(i.parent.parent,i.name)

def r_declared_variable():
    for i in listOfParents:
        if i.name == "declaracao_variaveis":
            temp = ["type","variable",-1,"local","global","variável","expressao"]
            if i.parent.name == "declaracao":
                temp[3] = "global"
            else:
                temp[3] = "local"
                temp[4] = r_verify_scope_variable(i)
            for j in i.children:
                if j.name == "lista_variaveis":
                    walkNodeTree(j)
                    temp[0] = i.children[0].children[0].children[0]
                    for k in tempListOfParents:
                        if k.name == "ID":
                            listVariableDeclared.append(k.children[0])
                            temp[1] = k.children[0]
                        if k.name == "indice":
                            temp[2] = r_verify_indice(k,k.parent.children[0].children[0].name)
            r_verify_declared_varible_again(temp)
            listOfTypes.append(temp)
        if i.name == "parametro":
            if i.parent.name == "lista_parametros":
                temp = ["type","variable",-1,"local","global","variável","parâmetro"]
                temp[4] = r_verify_scope_variable(i)
                temp[0] = i.children[0].children[0].children[0]
                temp[1] = i.children[2].children[0]
                r_verify_declared_varible_again(temp)
                listOfTypes.append(temp)
    r_unused_declared_variable()

def r_verify_scope_variable(node):
    r_find_cabe_func(node)
    if tempCabecalhoFunc != None:
        return tempCabecalhoFunc.children[0].children[0].name
    else:
        return "global"

def r_verify_declared_varible_again(obj):
    for i in listOfTypes:
        if i[1].name == obj[1].name:
            if i[3] == obj[3]:
                if i[4] == obj[4]:
                    print("Aviso: Variável ‘{}’ já declarada anteriormente ".format(obj[1].name))

def r_verify_indice(node,name):
    walkNodeTree(node)
    for i in tempListOfParents:
        if i.name == "numero":
            if i.children[0].name == "NUM_PONTO_FLUTUANTE":
                print("Erro: índice de array ‘{}’ não inteiro".format(name))
                return i.children[0].children[0]
            else:
                return i.children[0].children[0]
    return -1

def r_unused_declared_variable():
    for i in listOfTerminals:
        for j in listVariableDeclared:
            if i.name == j.name:
                if i.parent.parent.parent != j.parent.parent.parent:
                    listVariableDeclared.remove(j)
    for i in listVariableDeclared:
        print("Aviso: Variável ‘{}’ declarada e não utilizada".format(i.name))

def r_verify_assignment():
    for i in listOfParents:
        if i.name == "atribuicao":
            walkNodeTree(i)
            r_find_cabe_func(i)
            temp = []
            hasFunc = False
            for find in tempListOfParents:
                if find.name == "chamada_funcao":
                    hasFunc = True
                if find.name == "indice":
                    hasFunc = True
                    r_verify_range_index(find.parent)
            for j in tempListOfParents:
                if j.name == "ID":
                    if tempCabecalhoFunc != None:
                        temp.append([j.children[0],tempCabecalhoFunc.children[0].children[0].name])
                    else:
                        temp.append([j.children[0],"global"])
                    listVariableInitiated.append(temp[0])
                elif j.name == "numero" and hasFunc == False:
                        if tempCabecalhoFunc != None:
                            temp.append([j.children[0],tempCabecalhoFunc.children[0].children[0].name])
                        else:
                            temp.append([j.children[0],"global"])
            r_verify_types_variables(temp)

def r_verify_range_index(node):
    for i in listOfTypes:
        if node.children[0].children[0].name == i[1].name:
            walkNodeTree(node)
            for j in tempListOfParents:
                if j.name == "numero":
                    if float(j.children[0].children[0].name) > float(i[2].name):
                        print("Erro: índice de array ‘{}’ fora do intervalo".format(i[1].name))
                    return

def r_verify_types_variables(obj):
    types = r_get_type_varaible(obj)
    count = 0
    if types == -1:
        return
    for i in types:
        if i == False:
            print("Erro: Variável ‘{}’ não declarada".format(obj[count][0].name))
            return
        count += 1
    count = 0
    for i in range(len(types) - 1):
        if types[count] != types[count + 1]:
            if obj[count + 1][0].parent.name != "numero":
                print("Aviso: Atribuição de tipos distintos ‘{}’ {} e ‘{}’ ‘{}’".format(obj[count][0].name,types[count],obj[count + 1][0].name,types[count + 1]))
            elif obj[count][0].parent.name == "numero" and obj[count + 1][0].parent.name == "numero":
                print("Aviso: Atribuição de tipos distintos numero ‘{}’ e numero ‘{}’ ".format(types[count],types[count + 1]))
            else:
                print("Aviso: Atribuição de tipos distintos ‘{}’ {} e {} ‘{}’".format(obj[count][0].name,types[count],obj[count + 1][0].parent.name,types[count + 1]))
        count += 1

def r_get_type_varaible(obj):
    verify = []
    types = []
    count = 0

    if len(obj) <= 1:
        return -1

    for i in range(len(obj)):
        verify.append(False)
        types.append(False)

    for i in obj:
        if i[0].parent.name != "ID":
            if i[0].name == "NUM_INTEIRO":
                typeNumber = "inteiro"
                types[count] = "inteiro"
            elif i[0].name == "NUM_PONTO_FLUTUANTE":
                typeNumber = "flutuante"
                types[count] = "flutuante"
        count += 1
    count = 0

    for i in listOfTypes:
        if i[1].name == obj[0][0].name:
            if i[4] == obj[0][1] and types[0] == False:
                types[0] = i[0].name
                verify[0] = True
        if i[1].name == obj[1][0].name:
            if i[4] == obj[1][1] and types[1] == False:
                types[1] = i[0].name
                verify[1] = True
    for i in verify:
        if i == False:
            for j in listOfTypes:
                if j[1].name == obj[count][0].name:
                    types[count] = j[0].name
        count += 1
    return types

def r_variable_declared(variable,scope):
    for i in listOfTypes:
        if i[1].name == variable.name:
            if i[4] == scope:
                return i
    for i in listOfTypes:
        if i[1].name == variable.name:
            if i[4] == "global":
                return i
    print("Erro: Variável ‘{}’ não declarada".format(variable.name))
    return -1

def r_verify_read():
    for i in listOfParents:
        if i.name == "escreva":
            r_find_cabe_func(i)
            for j in i.children:
                if j.name == "expressao":
                    walkNodeTree(j)
                    for k in tempListOfTerminals:
                        if k.parent.name == "ID":
                            if tempCabecalhoFunc == None:
                                r_verify_has_assignment(k,"global")
                            else:
                                r_verify_has_assignment(k,tempCabecalhoFunc.children[0].children[0].name)

def r_verify_has_assignment(variable,scope):
    for i in listVariableInitiated:
        if i[0].name == variable.name:
            if scope == i[1]:
                return 0
    for i in listVariableInitiated:
        if i[0].name == variable.name:
            if i[1] == "global":
                return 0
    for i in listOfTypes:
        if i[1].name == variable.name:
            if i[5] == "funcao":
                return 0
    print("Aviso: Variável ‘{}’ declarada e não inicializada".format(variable.name))
    return -1

def table_generator():#|SCOPE| -> |DECLARACAO| -> |TAG| -> |LOCAL| -> |NOME| -> |TIPO| -> |INDICE| -> |TAM|
    print("\n                                    - TABELA -")
    print("=====================================================================================\n")
    for i in listOfTypes:
        if i[0] == "vazio":
            print("|{}| -> |{}| -> |{}| -> |{}| -> |{}| -> |{}| -> |{}| -> |{}|".format(i[3],i[6],i[5],i[4],i[1].name,i[0],"False",0))
        elif i[2] == -1:
            print("|{}| -> |{}| -> |{}| -> |{}| -> |{}| -> |{}| -> |{}| -> |{}|".format(i[3],i[6],i[5],i[4],i[1].name,i[0].name,"False",0))
        else:
            print("|{}| -> |{}| -> |{}| -> |{}| -> |{}| -> |{}| -> |{}| -> |{}|".format(i[3],i[6],i[5],i[4],i[1].name,i[0].name,"True",i[2].name))
    print("\n=====================================================================================\n")


def getLastChildren(node):
    if len(node.children) >= 1:
        getLastChildren(node.children[0])
    else:
        addParentInTreeGenerate(node)
        return 

def addParentInTreeGenerate(node):
    tempParentGenerateTree.clear()
    tempParentGenerateTree.append(node)

def walkTreeToLinkParents(rootChildren,parent):
    if len(rootChildren.children) > 1:
        conta = 0
        select = math.ceil(len(rootChildren.children)/2) - 1
        if parent == None:
            getLastChildren(rootChildren.children[select])
            global tempNewRoot
            tempNewRoot = tempParentGenerateTree[0]
        elif parent != None:
            global tempOldRoot
            tempOldRoot = tempParentGenerateTree[0]
            getLastChildren(rootChildren.children[select])
        for i in rootChildren.children:
            if conta == select:
                walkTreeToLinkParents(i, tempOldRoot)
            else:
                walkTreeToLinkParents(i,tempParentGenerateTree[0])
            conta += 1
    elif len(rootChildren.children) == 1:
        walkTreeToLinkParents(rootChildren.children[0], parent)
    else:
        if parent != None and rootChildren != None:
            tempListLinkParentsInTree.append([rootChildren,parent])
            #print(rootChildren.name,parent.name)#Descobrir o porque não funciona quando precisa linka varias coisas

def tree_generator(root, parent):
    walkTreeToLinkParents(root, parent)
    for i in tempListLinkParentsInTree:
        try:
            i[0].parent = i[1]
        except:
            0
    try:
        UniqueDotExporter(tempNewRoot).to_picture(argv[1] + ".resume.unique.ast.png")
    except:
        print("Error, unable to generate Semantics Tree")

def main():
    try:
        root = sintatico.main()
        walkTree(root)
        runAllRules()
        tree_generator(root, None)
    except:
        print("Error, unable to generate Semantics Rules")

if __name__ == "__main__":
    main()