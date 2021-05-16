import math
from sys import argv, exit
from llvmlite import ir
from llvmlite import binding as llvm
import itertools
import semantico

tempNodeName = None

table = []
listOfParents = []
listOfTerminals = []
tempListOfParents = []
tempListOfTerminals = []
parseOfParents = []
parseOfTerminals = []

listVariables = {"global": []}
listaFuncs = {}

llvm.initialize()
llvm.initialize_all_targets()
llvm.initialize_native_target()
llvm.initialize_native_asmprinter()

module = ir.Module('module.bc')
module.triple = "x86_64-pc-linux-gnu" #llvm.get_default_triple()
target = llvm.Target.from_triple(module.triple)
target_machine = target.create_target_machine()
module.data_layout = target_machine.target_data

escrevaInteiro = ir.Function(module,ir.FunctionType(ir.VoidType(), [ir.IntType(32)]),name="escrevaInteiro")
escrevaFlutuante = ir.Function(module,ir.FunctionType(ir.VoidType(),[ir.FloatType()]),name="escrevaFlutuante")
leiaInteiro = ir.Function(module,ir.FunctionType(ir.IntType(32),[]),name="leiaInteiro")
leiaFlutuante = ir.Function(module,ir.FunctionType(ir.FloatType(),[]),name="leiaFlutuante")

def splite_tree(node):
    if len(node.children) >= 1:
        listOfParents.append(node)
        for i in node.children:
            splite_tree(i)
    else:
        listOfTerminals.append(node)

def splite_node_tree(node):
    tempListOfParents.clear()
    tempListOfTerminals.clear()
    spliteNodeTree(node)

def temp_splite_node_tree(node):
    parseOfParents.clear()
    parseOfTerminals.clear()
    tempSpliteNodeTree(node)

def tempSpliteNodeTree(node):
    if len(node.children) >= 1:
        parseOfParents.append(node)
        for i in node.children:
            tempSpliteNodeTree(i)
    else:
        parseOfTerminals.append(node)


def spliteNodeTree(node):
    if len(node.children) >= 1:
        tempListOfParents.append(node)
        for i in node.children:
            spliteNodeTree(i)
    else:
        tempListOfTerminals.append(node)

def returnType(nodeType):
    typeNode = None
    if nodeType == "inteiro":
        typeNode = ir.IntType(32)
    elif nodeType == "flutuante":
        typeNode = ir.FloatType()
    else:
        typeNode = ir.VoidType()
    return typeNode

def returnValueType(nodeType):
    value = 0.0
    if nodeType == "inteiro":
        value = 0
    return value

def getValueVariable(name,scope):
    rangeScope = listVariables[scope] + listVariables["global"]

    for i in rangeScope :
        if i[0].name == name:
            return i

def getValueVariableArgs(func,name):
    for i in func.args:
        if i.name == name:
            return i

def getVaraibleArray(node,scope,builder):
    array = getValueVariable(node.children[0].children[0].name,scope)
    indice = None
    if node.children[1].children[1].name == "numero":
        dimension = int(node.children[1].children[1].children[0].children[0].name)
        indice = [ir.Constant(ir.IntType(int(array[2])), 0), ir.Constant(ir.IntType(array[2]), dimension)]
    elif node.children[1].children[1].name == "var":
        temp = getValueVariable(node.children[1].children[1].children[0].name,scope)
        dimension = builder.load(temp[0])
        indice = [ir.Constant(ir.IntType(int(array[2])), 0), ir.Constant(ir.IntType(array[2]), dimension)]

    elemn = builder.gep(array[0], indice, name='find_elem')
    return [elemn,array[1]]
    
def constructReturnValue(node,scope,builder):
    if node.name == "numero":
        if node.children[0].name == "NUM_INTEIRO":
            return [ir.Constant(ir.IntType(32), int(node.children[0].children[0].name)), "inteiro"]
        elif node.children[0].name == "NUM_PONTO_FLUTUANTE":
            return [ir.Constant(ir.FloatType(), float(node.children[0].children[0].name)), "flutuante"]
        else:
            return [ir.Constant(ir.FloatType(), float(node.children[0].children[0].name)), "flutuante"]
    elif node.name == "var":
        if len(node.children) > 1:
            return getVaraibleArray(node,scope,builder)
        else:
            varName = node.children[0].name
            return getValueVariable(varName,scope)

def declare_variable_global(node):
    if len(node.children[2].children) > 1:
        dimension = int(node.children[2].children[1].children[1].children[0].children[0].name)
        typeVar = ir.ArrayType(ir.IntType(32),dimension)
        var = ir.GlobalVariable(module, typeVar, node.children[2].children[0].children[0].name)
        listVariables["global"].append([var,node.children[0].name,dimension])
    else:
        typeVar = returnType(node.children[0].name)
        var = ir.GlobalVariable(module, typeVar, node.children[2].children[0].name)
        var.initializer = ir.Constant(typeVar, returnValueType(node.children[0].name))
        var.linkage = "common"
        var.align = 4
        listVariables["global"].append([var,node.children[0].name])

def resolveAssignment(node,builder,scope,func):
    typeAssignment = "inteiro"
    termOne = 0
    typeTermOne = "inteiro"
    termTwo = 0
    typeTermTwo = "inteiro"

    if node.children[0].name in ["+","-","/","*"]:
        temp = resolveAssignment(node.children[0],builder,scope,func)
        termOne = temp[0]
        typeTermOne = temp[1]
    else:
        tempAux = None
        temp = constructReturnValue(node.children[0],scope,builder)

        if temp == None and node.children[0].name == "var":
            temp = [None,None]
            varTemp = getValueVariableArgs(func,node.children[0].children[0].name)
            tempAux = varTemp
            if str(varTemp.type) == "i32":
                temp[1] = "inteiro"
            else:
                temp[1] = "flutuante"

        elif node.children[0].name == "var":
            tempAux = builder.load(temp[0])
        else:
            tempAux = temp[0]
        
        termOne = tempAux
        typeTermOne = temp[1]

    if node.children[1].name in ["+","-","/","*"]:
        temp = resolveAssignment(node.children[1],builder,scope,func)
        termTwo = temp[0]
        typeTermTwo = temp[1]
    else:
        tempAux = None
        temp = constructReturnValue(node.children[1],scope,builder)

        if temp == None and node.children[0].name == "var":
            temp = [None,None]
            varTemp = getValueVariableArgs(func,node.children[1].children[0].name)
            tempAux = varTemp
            if str(varTemp.type) == "i32":
                temp[1] = "inteiro"
            else:
                temp[1] = "flutuante"

        elif node.children[1].name == "var":
            tempAux = builder.load(temp[0])
        else:
            tempAux = temp[0]
        
        termTwo = tempAux
        typeTermTwo = temp[1]
    
    operation = node.name

    if typeTermOne == "inteiro" and typeTermTwo == "flutuante":
        termOne = builder.sitofp(termOne, ir.FloatType())
        typeAssignment = "flutuante"
    elif typeTermOne == "flutuante" and typeTermTwo == "inteiro":
        termTwo = builder.sitofp(termTwo, ir.FloatType())
        typeAssignment = "flutuante"
    else:
        typeAssignment = typeTermOne

    if operation == "+":
        if typeAssignment == "inteiro":
            return [builder.add(termOne, termTwo), "inteiro"]
        return [builder.fadd(termOne, termTwo), "flutuante"]

    if operation == "-":
        if typeAssignment == "inteiro":
            return [builder.sub(termOne, termTwo), "inteiro"]
        return [builder.fsub(termOne, termTwo), "flutuante"]

    if operation == "*":
        if typeAssignment == "inteiro":
            return [builder.mul(termOne, termTwo), "inteiro"]
        return [builder.fmul(termOne, termTwo), "flutuante"]
    
    if operation == "/":
        if typeAssignment == "inteiro":
            return [builder.sdiv(termOne, termTwo), "inteiro"]
        return [builder.fdiv(termOne, termTwo), "flutuante"]

def findFuncInTable(name):
    for i in table:
        if i[4] == name and i[5] == "funcao":
            return i

def resolveCallFunction(node,builder,scope):
    params = []
    called_function = findFuncInTable(node.children[0].name)
    func, typeFunc = listaFuncs[called_function[4]]
    
    if len(node.children) > 3:
        chooseNode = None

        if len(node.children[2].children) > 1:
            chooseNode = node.children[2].children
        else:
            chooseNode = node.children

        for i in chooseNode:
            if i.name == "chamada_funcao":
                par = resolveCallFunction(i,builder,scope)
                params.append(par)

            elif i.name == "var":
                par = constructReturnValue(i,scope,builder)
                params.append(builder.load(par[0]))

            elif i.name == "numero":
                par = constructReturnValue(i,scope,builder)
                params.append(par[0])
        return builder.call(func,params)
    else:
        return builder.call(func,[])

def getRootName(node,name):
    if node.name == name:
        getRootName(node.parent,name)
    else:
        global tempNodeName
        tempNodeName = node.name

def declare_function(node):
    splite_node_tree(node)
    typeFunc = returnType(node.children[0].name)

    if len(node.children) >= 1:
        if node.children[1].children[0].name == "principal":
            scope = "main"
        else:
            scope = node.children[1].children[0].name
    else:
        scope = node.children[0].children[0].name

    listVariables[scope] = []
    typeParam = []

    for i in table:
        if i[4] == node.children[1].children[0].name and i[6] == "parâmetro":
            typeParam.append(returnType(i[0].name))

    generate_func = ir.FunctionType(typeFunc, typeParam)
    func = ir.Function(module, generate_func, name=scope)

    count = 0
    for i in table:
        if i[4] == node.children[1].children[0].name and i[6] == "parâmetro":
            parTemp = i[1].name
            func.args[count].name = parTemp
            count += 1

    listaFuncs[scope] = [func,findFuncInTable(node.children[1].children[0].name)[0].name]

    entryBlock = func.append_basic_block('entry')
    builder = ir.IRBuilder(entryBlock)

    returnFunc = builder.alloca(ir.IntType(32), name='retorno')
    returnFunc.align = 4
    Zero32 = ir.Constant(ir.IntType(32), 0) 
    builder.store(Zero32, returnFunc)
    
    fill_function(node,func,scope,builder,returnFunc)

def fill_function(node,func,scope,builder,returnFunc):

    if scope == "main":
        tempNameFunc = "principal"
    else:
        tempNameFunc = scope
    for i in table:
        if i[3] == "local" and i[4] == tempNameFunc and i[5] == "variável":
            typeVar = returnType(i[0].name)
            var = builder.alloca(typeVar, name=i[1].name)
            var.align = 4
            listVariables[scope].append([var,i[0].name])

    for i in tempListOfParents:
        if i.name == "leia" and i.parent.name == "corpo":
            if i.children[2].name == "var":
                tempList = listVariables["global"] + listVariables[scope]
                for j in tempList:
                    if j[0].name == i.children[2].children[0].name:
                        if j[1] == "inteiro":
                            ret = builder.call(leiaInteiro, args=[])
                            builder.store(ret,j[0])
                        elif j[1] == "flutuante":
                            ret = builder.call(leiaFlutuante, args=[])
                            builder.store(ret,j[0])
        
        if i.name == "escreva" and i.parent.name == "corpo":
            if i.children[2].name == "var":
                tempList = listVariables["global"] + listVariables[scope]
                for j in tempList:
                    if j[0].name == i.children[2].children[0].name:
                        if j[1] == "inteiro":
                            retVar = builder.load(j[0],name = "escreva_var",align = 4)
                            builder.call(escrevaInteiro, [retVar])
                        elif j[1] == "flutuante":
                            retVar = builder.load(j[0],name = "escreva_var",align = 4)
                            builder.call(escrevaInteiro, [retVar])
            
            elif i.children[2].name == "numero":
                if i.children[2].children[0].name == "NUM_INTEIRO":
                    var = ir.Constant(ir.IntType(32), int(i.children[2].children[0].children[0].name))
                    builder.call(escrevaInteiro, [var])
                elif i.children[2].children[0].name == "NUM_PONTO_FLUTUANTE":
                    var = ir.Constant(ir.FloatType(), float(i.children[2].children[0].children[0].name))
                    builder.call(escrevaFlutuante, [var]) 

        if i.name == "se" and i.parent.name == "corpo":
            hasElse = False

            for j in i.children:
                if j.name == "senão":
                    hasElse = True
            
            iftrue_1 = builder.append_basic_block('iftrue_1')
            iffalse_1 = builder.append_basic_block('iffalse_1')
            ifend_1 = builder.append_basic_block('ifend_1')

            if i.children[1].children[0].name == "var":
                varTemp = getValueVariable(i.children[1].children[0].children[0].name,scope)
                if varTemp == None:
                    varOneComp = getValueVariableArgs(func,i.children[1].children[0].name)
                else:
                    varOneComp = tempLoad = builder.load(varTemp[0])
            elif i.children[1].children[0].name == "numero":
                    temp = constructReturnValue(i.children[1].children[0],scope,builder)
                    varOneComp = temp[0]
            else:
                temp = getValueVariable(i.children[1].children[0].name,scope)
                varOneComp = temp[0]
            
            if i.children[1].children[1].name == "var":
                varTemp = getValueVariable(i.children[1].children[1].children[0].name,scope)
                if varTemp == None:
                    varTwoComp = getValueVariableArgs(func,i.children[1].children[1].name)
                else:
                    varTwoComp = tempLoad = builder.load(varTemp[0])
            elif i.children[1].children[1].name == "numero":
                    temp = constructReturnValue(i.children[1].children[1],scope,builder)
                    varTwoComp = temp[0]
            else:
                temp = getValueVariable(i.children[1].children[1].name,scope)
                varTwoComp = temp[0]
            
            if i.children[1].name in [">","<",">=","<=","==","!="]:
                ifOne = builder.icmp_signed(i.children[1].name, varOneComp, varTwoComp, name='if_test_1')
            elif i.children[1].name == "&&":
                ifOne = builder.and_(i.children[1].name, varOneComp, varTwoComp, name='if_test_1')
            elif i.children[1].name == "||":
                ifOne = builder.or_(i.children[1].name, varOneComp, varTwoComp, name='if_test_1')
 

            builder.cbranch(ifOne, iftrue_1, iffalse_1)

            thenBody = i.children[3]
            builder.position_at_end(iftrue_1)
            subTreeWalk(thenBody, func, scope, builder, returnFunc) 
            builder.branch(ifend_1)

            if hasElse:
                elseBody = i.children[5]
                builder.position_at_end(iffalse_1)
                subTreeWalk(elseBody, func, scope, builder, returnFunc)
                builder.branch(ifend_1)
            else:
                builder.position_at_end(iffalse_1)
                builder.branch(ifend_1)

            builder.position_at_end(ifend_1)
        
        if i.name == "repita" and i.parent.name == "corpo":
            repita = builder.append_basic_block("repita")
            ate = builder.append_basic_block('ate')
            repita_fim = builder.append_basic_block('repita_fim')

            builder.branch(repita)
            builder.position_at_end(repita)
            subTreeWalk(i, func, scope, builder, returnFunc)
            builder.branch(ate)
            builder.position_at_end(ate)

            if i.children[3].children[0].name == "var":
                varTemp = getValueVariable(i.children[3].children[0].children[0].name,scope)
                if varTemp == None:
                    varOneComp = getValueVariableArgs(func,i.children[3].children[0].name)
                else:
                    varOneComp = tempLoad = builder.load(varTemp[0])
            elif i.children[3].children[0].name == "numero":
                    temp = constructReturnValue(i.children[3].children[0],scope,builder)
                    varOneComp = temp[0]
            
            if i.children[3].children[1].name == "var":
                varTemp = getValueVariable(i.children[3].children[1].children[0].name,scope)
                if varTemp == None:
                    varTwoComp = getValueVariableArgs(func,i.children[3].children[1].name)
                else:
                    varTwoComp = tempLoad = builder.load(varTemp[0])
            elif i.children[3].children[1].name == "numero":
                    temp = constructReturnValue(i.children[3].children[1],scope,builder)
                    varTwoComp = temp[0]
            
            comp = builder.icmp_signed("==", varOneComp, varTwoComp, name='expression')
            builder.cbranch(comp, repita_fim, repita)
            builder.position_at_end(repita_fim)

        if i.name == "atribuicao":
            getRootName(i.parent,"corpo")
            if tempNodeName not in ["repita","se"]:
                if i.children[0].children[0].name == "var":
                    temp = constructReturnValue(i.children[0],scope,builder)
                else:
                    temp = getValueVariable(i.children[0].children[0].name,scope)
                varReceive = temp[0]
                typeVarReceive = temp[1]
                
                if i.children[2].name == "chamada_funcao":
                    tempResult = resolveCallFunction(i.children[2],builder,scope)
                    builder.store(tempResult,varReceive)

                elif i.children[2].name == "numero":
                    num = None
                    if i.children[2].children[0].name == "NUM_INTEIRO":
                        num = ir.Constant(ir.IntType(32), int(i.children[2].children[0].children[0].name))
                    elif i.children[2].children[0].name == "NUM_PONTO_FLUTUANTE":
                        num = ir.Constant(ir.IntType(32), float(i.children[2].children[0].children[0].name))
                    builder.store(num, varReceive)

                elif i.children[2].name == "var":
                    varTemp = getValueVariable(i.children[2].children[0].name,scope)
                    if varTemp == None:
                        varTemp = getValueVariableArgs(func,i.children[2].children[0].name)
                        builder.store(varTemp, varReceive)
                    else:
                        tempLoad = builder.load(varTemp[0])
                        builder.store(tempLoad, varReceive)

                elif i.children[2].name in ["+","-","/","*"]:
                    temp = resolveAssignment(i.children[2],builder,scope,func)
                    typeTemp = temp[1]
                    if typeTemp == "inteiro" and typeVarReceive == "flutuante":
                        temp[0] = builder.sitofp(temp[0], ir.FloatType())
                    elif typeTemp == "flutuante" and typeVarReceive == "inteiro":
                        temp[0] = builder.sitofp(temp[0], ir.IntType(32))
                    builder.store(temp[0], varReceive)

        if i.name == "retorna":
            endBasicBlock = func.append_basic_block('exit')
            builder.branch(endBasicBlock)
            builder.position_at_end(endBasicBlock)
            valueReturn = constructReturnValue(i.children[2],scope,builder)

            if i.children[2].name == "numero":
                builder.store(valueReturn[0], returnFunc)
            elif i.children[2].name == "var":
                tempLoad = builder.load(valueReturn[0])
                builder.store(tempLoad, returnFunc)

            returnTemp = builder.load(returnFunc, name='returnTemp', align=4)
            builder.ret(returnTemp)

def subTreeWalk(node, func, scope, builder, returnFunc):
    temp_splite_node_tree(node)

    for i in parseOfParents:
        if i.name == "leia" and i.parent.name == "corpo":
            if i.children[2].name == "var":
                tempList = listVariables["global"] + listVariables[scope]
                for j in tempList:
                    if j[0].name == i.children[2].children[0].name:
                        if j[1] == "inteiro":
                            ret = builder.call(leiaInteiro, args=[])
                            builder.store(ret,j[0])
                        elif j[1] == "flutuante":
                            ret = builder.call(leiaFlutuante, args=[])
                            builder.store(ret,j[0])
        
        if i.name == "escreva" and i.parent.name == "corpo":
            if i.children[2].name == "var":
                tempList = listVariables["global"] + listVariables[scope]
                for j in tempList:
                    if j[0].name == i.children[2].children[0].name:
                        if j[1] == "inteiro":
                            retVar = builder.load(j[0],name = "escreva_var",align = 4)
                            builder.call(escrevaInteiro, [retVar])
                        elif j[1] == "flutuante":
                            retVar = builder.load(j[0],name = "escreva_var",align = 4)
                            builder.call(escrevaInteiro, [retVar])
            
            elif i.children[2].name == "numero":
                if i.children[2].children[0].name == "NUM_INTEIRO":
                    var = ir.Constant(ir.IntType(32), int(i.children[2].children[0].children[0].name))
                    builder.call(escrevaInteiro, [var])
                elif i.children[2].children[0].name == "NUM_PONTO_FLUTUANTE":
                    var = ir.Constant(ir.FloatType(), float(i.children[2].children[0].children[0].name))
                    builder.call(escrevaFlutuante, [var])
        
        if i.name == "atribuicao":
            getRootName(i.parent,"corpo")
            if tempNodeName in ["repita","se"]:
                if i.children[0].children[0].name == "var":
                    temp = constructReturnValue(i.children[0],scope,builder)
                else:
                    temp = getValueVariable(i.children[0].children[0].name,scope)
                varReceive = temp[0]
                typeVarReceive = temp[1]
                
                if i.children[2].name == "chamada_funcao":
                    tempResult = resolveCallFunction(i.children[2],builder,scope)
                    builder.store(tempResult,varReceive)

                elif i.children[2].name == "numero":
                    num = None
                    if i.children[2].children[0].name == "NUM_INTEIRO":
                        num = ir.Constant(ir.IntType(32), int(i.children[2].children[0].children[0].name))
                    elif i.children[2].children[0].name == "NUM_PONTO_FLUTUANTE":
                        num = ir.Constant(ir.IntType(32), float(i.children[2].children[0].children[0].name))
                    builder.store(num, varReceive)
                
                elif i.children[2].name == "var":
                    varTemp = getValueVariable(i.children[2].children[0].name,scope)
                    if varTemp == None:
                        varTemp = getValueVariableArgs(func,i.children[2].children[0].name)
                        builder.store(varTemp, varReceive)
                    else:
                        tempLoad = builder.load(varTemp[0])
                        builder.store(tempLoad, varReceive)

                elif i.children[2].name in ["+","-","/","*"]:
                    temp = resolveAssignment(i.children[2],builder,scope,func)
                    typeTemp = temp[1]
                    if typeTemp == "inteiro" and typeVarReceive == "flutuante":
                        temp[0] = builder.sitofp(temp[0], ir.FloatType())
                    elif typeTemp == "flutuante" and typeVarReceive == "inteiro":
                        temp[0] = builder.sitofp(temp[0], ir.IntType(32))
                    builder.store(temp[0], varReceive)
        
        if i.name == "se" and i.parent.name == "corpo":
            hasElse = False

            for j in i.children:
                if j.name == "senão":
                    hasElse = True
            
            iftrue_1 = builder.append_basic_block('iftrue_1')
            iffalse_1 = builder.append_basic_block('iffalse_1')
            ifend_1 = builder.append_basic_block('ifend_1')

            if i.children[1].children[0].name == "var":
                varTemp = getValueVariable(i.children[1].children[0].children[0].name,scope)
                if varTemp == None:
                    varOneComp = getValueVariableArgs(func,i.children[1].children[0].name)
                else:
                    varOneComp = tempLoad = builder.load(varTemp[0])
            elif i.children[1].children[0].name == "numero":
                    temp = constructReturnValue(i.children[1].children[0],scope,builder)
                    varOneComp = temp[0]
            else:
                temp = getValueVariable(i.children[1].children[1].name,scope)
                varOneComp = temp[0]
            
            if i.children[1].children[1].name == "var":
                varTemp = getValueVariable(i.children[1].children[1].children[0].name,scope)
                if varTemp == None:
                    varTwoComp = getValueVariableArgs(func,i.children[1].children[1].name)
                else:
                    varTwoComp = tempLoad = builder.load(varTemp[0])
            elif i.children[1].children[1].name == "numero":
                    temp = constructReturnValue(i.children[1].children[1],scope,builder)
                    varTwoComp = temp[0]
            else:
                temp = getValueVariable(i.children[1].children[1].name,scope)
                varTwoComp = temp[0]
                
            if i.children[1].name in [">","<",">=","<=","==","!="]:
                ifOne = builder.icmp_signed(i.children[1].name, varOneComp, varTwoComp, name='if_test_1')
            elif i.children[1].name == "&&":
                ifOne = builder.and_(i.children[1].name, varOneComp, varTwoComp, name='if_test_1')
            elif i.children[1].name == "||":
                ifOne = builder.or_(i.children[1].name, varOneComp, varTwoComp, name='if_test_1')

            builder.cbranch(ifOne, iftrue_1, iffalse_1)

            thenBody = i.children[3]
            builder.position_at_end(iftrue_1)
            subTreeWalk(thenBody, func, scope, builder, returnFunc) 
            builder.branch(ifend_1)

            if hasElse:
                elseBody = i.children[5]
                builder.position_at_end(iffalse_1)
                subTreeWalk(elseBody, func, scope, builder, returnFunc)
                builder.branch(ifend_1)
            else:
                builder.position_at_end(iffalse_1)
                builder.branch(ifend_1)

            builder.position_at_end(ifend_1)
        
        if i.name == "repita" :
            getRootName(i.parent,"corpo")
            if tempNodeName in ["repita","se"]:
                repita = builder.append_basic_block("repita")
                ate = builder.append_basic_block('ate')
                repita_fim = builder.append_basic_block('repita_fim')

                builder.branch(repita)
                builder.position_at_end(repita)
                subTreeWalk(i, func, scope, builder, returnFunc)
                builder.branch(ate)
                builder.position_at_end(ate)

                if i.children[3].children[0].name == "var":
                    varTemp = getValueVariable(i.children[3].children[0].children[0].name,scope)
                    if varTemp == None:
                        varOneComp = getValueVariableArgs(func,i.children[3].children[0].name)
                    else:
                        varOneComp = tempLoad = builder.load(varTemp[0])
                elif i.children[3].children[0].name == "numero":
                        temp = constructReturnValue(i.children[3].children[0],scope,builder)
                        varOneComp = temp[0]
                
                if i.children[3].children[1].name == "var":
                    varTemp = getValueVariable(i.children[3].children[1].children[0].name,scope)
                    if varTemp == None:
                        varTwoComp = getValueVariableArgs(func,i.children[3].children[1].name)
                    else:
                        varTwoComp = tempLoad = builder.load(varTemp[0])
                elif i.children[3].children[1].name == "numero":
                        temp = constructReturnValue(i.children[3].children[1],scope,builder)
                        varTwoComp = temp[0]
                
                comp = builder.icmp_signed("==", varOneComp, varTwoComp, name='expression')
                builder.cbranch(comp, repita_fim, repita)
                builder.position_at_end(repita_fim)
        
        if i.name == "retorna":
            endBasicBlock = func.append_basic_block('exit')
            builder.branch(endBasicBlock)
            builder.position_at_end(endBasicBlock)
            valueReturn = constructReturnValue(i.children[2],scope,builder)

            if i.children[2].name == "numero":
                builder.store(valueReturn[0], returnFunc)
            elif i.children[2].name == "var":
                tempLoad = builder.load(valueReturn[0])
                builder.store(tempLoad, returnFunc)

            returnTemp = builder.load(returnFunc, name='returnTemp', align=4)
            builder.ret(returnTemp)

def generating_code():
    for i in listOfParents:
        if i.name == "declaracao_variaveis" and i.parent.name == "lista_declaracoes":
            try:
                declare_variable_global(i)
            except:
                0
    for i in listOfParents:
        if i.name == "declaracao_funcao":
            try:
                declare_function(i)
            except:
                0

    arquivo = open('module.ll', 'w')
    arquivo.write(str(module))
    arquivo.close()
    print(module)

def main():
    try:
        spliteReturn = semantico.main()
        root = spliteReturn[0]
        global table
        table = spliteReturn[1]
        splite_tree(root)
        generating_code()
    except:
        0

if __name__ == "__main__":
    main()