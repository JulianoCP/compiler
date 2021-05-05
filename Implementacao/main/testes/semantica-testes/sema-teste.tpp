inteiro: n
flutuante: x, y, z

inteiro fatorial(inteiro: n, flutuante: m)
	m := 5
	
	se n>0 então
		retorna(n)
	senão
		repita 
			flutuante: p
		até n = 0
	fim
	
	z := 1.9
	z := z + 1
	retorna(m)
fim

inteiro principal()
	leia(n)
	escreva(fatorial(1, 1.0))
fim

inteiro: a
flutuante: b

inteiro fatorial2(inteiro: fat, flutuante: fat2, inteiro: fat3)

	a := 1
	escreva(fatorial(fatorial(1, 1.0), 1.0))

	a := fatorial(1, 1.0)
	b := fatorial(1, 1.0)
	fatorial(1, 1.0)
fim