import os, sys
from typing import Type

## @defgroup core object core

## @ingroup core
## **object graph** item
class Object:

    ## @name constructor

    def __init__(self, V):
        ## type/class tag
        self.type = self.__class__.__name__.lower()
        ## scalar: object name, string/number value,...
        self.value = V
        ## associative array = env/namespace = map = AST sttributes
        self.slot = {}
        ## ordered container = vector = stack = queue = AST subtrees
        self.nest = []

    ## wrap Python types
    def box(self, that):
        if isinstance(that, Object): return that
        if callable(that): return Cmd(that)
        raise TypeError(['box', type(that), that])

    ## @name dump/stringify

    def __repr__(self): return self.dump()

    ## full text tree dump
    def dump(self, cycle=[], depth=0, prefix=''):
        # head
        def pad(depth): return '\n' + '\t' * depth
        ret = pad(depth) + self.head(prefix)
        # slot{}s
        for i in self.keys():
            ret += self[i].dump(cycle, depth + 1, f'{i} = ')
        # nest[]ed
        for j, k in enumerate(self):
            ret += k.dump(cycle, depth + 1, f'{j}: ')
        # subtree
        return ret

    ## short `<T:V>` header
    def head(self, prefix=''):
        gid = f' @{id(self):x}'
        return f'{prefix}<{self.tag()}:{self.val()}>{gid}'

    def tag(self): return self.type
    def val(self): return f'{self.value}'

    ## @name operator

    def keys(self): return sorted(self.slot.keys())

    def __getitem__(self, key):
        if isinstance(key, str): return self.slot[key]
        if isinstance(key, int): return self.nest[key]
        raise TypeError(['__getitem__', type(key)])

    def __setitem__(self, key, that):
        if isinstance(key, str): self.slot[key] = self.box(that); return self
        raise TypeError(['__setitem__', type(key)])

    def __rshift__(self, that):
        that = self.box(that)
        self[that.val()] = that

    def __floordiv__(self, that):
        self.nest.append(self.box(that)); return self

## @defgroup prim primitive
## @ingroup core

## @ingroup prim
class Primitive(Object):
    def exec(self, env): return self

## @ingroup prim
class Sym(Primitive):
    def exec(self, env): return env[self.val()]

## @ingroup prim
class Num(Primitive):
    def __init__(self, V): Primitive.__init__(self, float(V))

## @ingroup prim
class Int(Num):
    def __init__(self, V): Primitive.__init__(self, int(V))

## @ingroup prim
class Hex(Int):
    def __init__(self, V): super().__init__(int(V[2:], 0x10))
    def val(self): return f'{self.value:x}'

## @ingroup prim
class Bin(Int):
    def __init__(self, V): super().__init__(int(V[2:], 0x02))
    def val(self): return f'{self.value:b}'

## @defgroup cont container
## @ingroup core

## @ingroup cont
class Container(Object): pass

## @ingroup cont
class Vector(Container): pass

## @ingroup cont
class Map(Container): pass

## @defgroup active active
## @ingroup core
## Executable Data Structures (c)

## @ingroup active
## Executable Data Structures (c)
class Active(Object): pass

## @ingroup active
## FORTH Virtual Machine combines nest:stack and @ref slot :vocabulary
class VM(Active, Container): pass

## @ingroup active
class Cmd(Active):
    def __init__(self, F):
        assert (callable(F))
        super().__init__(F.__name__)
        self.fn = F

## @ingroup active
glob = VM('FORTH')

## @ingroup active
def nop(env=glob): pass
glob >> nop

## @ingroup active
def bye(env=glob): sys.exit(0)
glob >> bye

def q(env=glob): print(env)
glob['?'] = q

def dot(env=glob): glob.dot()
glob['.'] = dot

## @ingroup active
class Seq(Active, Vector): pass

glob >> (Seq('hello') // glob['nop'] // glob['bye'])

## @defgroup parser parser

import ply.lex as lex

tokens = ['sym', 'int', 'num', 'hex', 'bin']

t_ignore = '[ \t\r]+'

def t_comment(t):
    r'\#.*'
    pass

def t_nl(t):
    r'\n+'
    t.lineno += len(t.value)

def t_num_point(t):
    r'[+\-]?[0-9]+\.[0-9]*'
    return Num(t.value)

def t_num_intexp(t):
    r'[+\-]?[0-9]+[eE][+\-]?[0-9]+'
    return Num(t.value)

def t_hex(t):
    r'0x[0-9A-Fa-f]+'
    return Hex(t.value)

def t_bin(t):
    r'0b[01]+'
    return Bin(t.value)

def t_int(t):
    r'[+\-]?[0-9]+'
    return Int(t.value)

def t_sym(t):
    r'[^ \t\r\n]+'
    return Sym(t.value)

def t_error(t): raise SyntaxError(t)

lexer = lex.lex()


import ply.yacc as yacc

def p_repr_none(p):
    ' syntax :'
def p_repr_recur(p):
    ' syntax : syntax ex '
    print(p[2])
    print(p[2].exec(W))
    print(W)
    print('-' * 0x22)

def p_hex(p):
    ' ex : hex '
    p[0] = p[1]
def p_bin(p):
    ' ex : bin '
    p[0] = p[1]
def p_int(p):
    ' ex : int '
    p[0] = p[1]
def p_num(p):
    ' ex : num '
    p[0] = p[1]

def p_sym(p):
    ' ex : sym '
    p[0] = p[1]

def p_error(p): raise SyntaxError(p)

parser = yacc.yacc(debug=False, write_tables=False)

if __name__ == '__main__':
    print(glob)
    for i in sys.argv[1:]:
        print(i)
        with open(i) as src: lexer.input(src.read())
        while True:
            token = lexer.token()
            if not token: break
            print(token.exec(glob))
