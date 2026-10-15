"""Shared bounded recipient selection for Qt, Tk and controlled reprints."""
def parse_ranges(text,count):
    if type(count) is not int or not 1<=count<=10000:raise ValueError('Recipientes: indique un número entre 1 y 10000.')
    values=[]
    for part in text.replace(' ','').split(','):
        if not part:continue
        if '-' in part:
            bits=part.split('-')
            if len(bits)!=2:raise ValueError('Rango inválido. Ejemplo: 1-3,5.')
            start,end=map(int,bits)
            if start<1 or end<start or end>count:raise ValueError('Rango fuera de los recipientes originales.')
            values.extend(range(start,end+1))
        else:values.append(int(part))
    values=list(dict.fromkeys(values))
    if not values or any(n<1 or n>count for n in values):raise ValueError('Introduzca números válidos dentro de la emisión original.')
    return values
