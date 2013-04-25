#!/usr/bin/python

import random
import os

def bin(x, width):
    if x < 0: x = (~x) + 1
    return ''.join([(x & (1 << i)) and '1' or '0' for i in range(width-1, -1, -1)])

def sra(a, b):
    if b == 0:
        return a
    elif a & (1<<31):
        out = (a >> b) | reduce(lambda a,b: a|b, [1 << x for x in range(31, 31-b, -1)])
        return out
    else:
        out = a >> b
        return out

def sext(a):
    if not a & (1<<15):
        return a
    else:
        return 0xffff0000 | (abs(a)&0xffff)

def bwnot(a):
    return reduce(lambda a,b: a|b, [([1,0][a>>x & 1]) << x for x in range(0,32)])

def flipsign(a):
    if a < 0:
        return bwnot(abs(a)) + 1
    elif a & (1<<31):
        return -(bwnot(a) + 1)
    else:
        return a

def comp(a,b):
    a = flipsign(a)
    b = flipsign(b)
    return a < b

def sub(a,b):
    res = a-b 
    if res < 0:
        return bwnot(abs(res)) + 1
    else:
        return res

# tuple contains (opcode/funct bits, function, limit for a, limit for b)
opcodes = \
{ 
    "RTYPE":   ("000000", lambda a,b: 0, lambda a: a, lambda b: b),
    "LB":      ("100000", lambda a,b: a+b, lambda a: a, lambda b: sext(b&0xffff)),
    "LH":      ("100001", lambda a,b: a+b, lambda a: a, lambda b: sext(b&0xffff)),
    "LW":      ("100011", lambda a,b: a+b, lambda a: a, lambda b: sext(b&0xffff)),
    "LBU":     ("100100", lambda a,b: a+b, lambda a: a, lambda b: sext(b&0xffff)),
    "LHU":     ("100101", lambda a,b: a+b, lambda a: a, lambda b: sext(b&0xffff)),
    "SB":      ("101000", lambda a,b: a+b, lambda a: a, lambda b: sext(b&0xffff)),
    "SH":      ("101001", lambda a,b: a+b, lambda a: a, lambda b: sext(b&0xffff)),
    "SW":      ("101011", lambda a,b: a+b, lambda a: a, lambda b: sext(b&0xffff)),
    "ADDIU":   ("001001", lambda a,b: a+b, lambda a: a, lambda b: sext(b&0xffff)),
    "SLTI":    ("001010", lambda a,b: (lambda:0, lambda:1)[comp(a,b)](), lambda a: a, lambda b: sext(b&0xffff)),
    "SLTIU":   ("001011", lambda a,b: (lambda:0, lambda:1)[a < b](), lambda a: a, lambda b: sext(b&0xfff)),
    "ANDI":    ("001100", lambda a,b: a&b, lambda a: a, lambda b: abs(b)&0xffff),
    "ORI":     ("001101", lambda a,b: a|b, lambda a: a, lambda b: abs(b)&0xffff),
    "XORI":    ("001110", lambda a,b: a^b, lambda a: a, lambda b: abs(b)&0xffff),
    "LUI":     ("001111", lambda a,b: b<<16, lambda a: a, lambda b: abs(b)&0xffff)
}

functs = \
{
    "SLL":     ("000000", lambda a,b: b<<a, lambda a: a&0x1f, lambda b: b),
    "SRL":     ("000010", lambda a,b: b>>a, lambda a: a&0x1f, lambda b: b),
    "SRA":     ("000011", lambda a,b: sra(b,a), lambda a: a&0x1f, lambda b: b|(1<<31)),
    "SLLV":    ("000100", lambda a,b: b<<a, lambda a: a&0x1f, lambda b: b),
    "SRLV":    ("000110", lambda a,b: b>>a, lambda a: a&0x1f, lambda b: b),
    "SRAV":    ("000111", lambda a,b: sra(b,a), lambda a: a&0x1f, lambda b: b|(1<<31)),
    "ADDU":    ("100001", lambda a,b: a+b, lambda a: a, lambda b: b),
    "SUBU":    ("100011", lambda a,b: sub(a,b), lambda a: a, lambda b: b),
    "AND":     ("100100", lambda a,b: a&b, lambda a: a, lambda b: b),
    "OR":      ("100101", lambda a,b: a|b, lambda a: a, lambda b: b),
    "XOR":     ("100110", lambda a,b: a^b, lambda a: a, lambda b: b),
    "NOR":     ("100111", lambda a,b: bwnot(a|b), lambda a: a, lambda b: b),
    "SLT":     ("101010", lambda a,b: (lambda:0, lambda:1)[comp(a,b)](), lambda a: a, lambda b: b),
    "SLTU":    ("101011", lambda a,b: (lambda:0, lambda:1)[a < b](), lambda a: a, lambda b: b)
}               
                
random.seed(os.urandom(32))
file = open('testvectors.input', 'w')

def gen_vector(op, f, a, b, opcode, funct):
    A = a(random.randint(0, 0xffffffff))
    B = b(random.randint(0, 0xffffffff))
    REFout = f(A,B)
    # Uncomment this if you want to see decimal outputs
    # print 'Op: {0}, A: {1}, B: {2}, Out: {3}'.format(op, str(A), str(B), str(REFout))
    # return ''
    return ''.join([opcode, funct, bin(A, 32), bin(B, 32), bin(REFout, 32)])

loops = 20

for i in xrange(loops):
    for opcode, tup in opcodes.iteritems():
        oc, f, a, b = tup
        if opcode == "RTYPE":
            for funct, tup in functs.iteritems():
                fct, f, a, b = tup
                file.write(gen_vector(funct, f, a, b, oc, fct) + '\n')
                # print gen_vector(funct, f, a, b, oc, fct)
        else:
            fct = bin(random.randint(0, 0x3f), 6)
            file.write(gen_vector(fct, f, a, b, oc, fct) + '\n')
            # print gen_vector(opcode, f, a, b, oc, fct)

