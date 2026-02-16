a = int(input("Введите число: "))

#
c = 100000000000000000

for i in range(len(str(c))):
    if a // c > 0:
        print(a // c)
        a -= c * (a // c)
    c //= 10



