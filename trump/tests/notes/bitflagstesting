
n = BitFlag(8)
print repr(n)
print n.bools
print n.bin
print n.bin_str
newd = n.asdict()
print newd
print n.val
n = BitFlag(newd)
print repr(n)
print n.bools
print n.bin
print n.bin_str
print n.asdict()
n['raise'] = True
n['raise'] = True
n['email'] = True
n['enabled'] = True
print n.asdict()
print n.val
print repr(n)
print BitFlag(n.val).asdict()
print BitFlag(n.val).val
print BitFlag(BitFlag(n.val).asdict()).val
print repr(BitFlag(BitFlag(n.val).asdict()))

one = BitFlag(1)
print repr(one)
print one
print one()
two = BitFlag(2)
print repr(two)
print two
print two()
print one | two

print one() | two()

print one()
