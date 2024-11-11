import traceback

def parsing():
    print('starting...')
    lst = [(line.split(',')[0], line.split(',')[1].strip('\n')) for line in open('/opt/files/shas.csv', 'r', encoding='utf-8')]
    nl = []
    for index, item in enumerate(lst):
        try:
            m = item[0].split()
            if len(m) == 3:
                a, d, m = m[-1], m[-2], m[-3]
            else:
                a, d, m = m[-1], m[-2], m[-4] + ' ' + m[-3]
            nl.append( f'{m},{d},{a},{item[1]}\n' )
        except:
            print(item[0])
            print(traceback.format_exc())
            print(f'at line: {index}')
            exit()

    open('/opt/files/shas2.csv', 'w', encoding='utf-8').writelines(nl)
    print('done!')

def get_index1(m, d, a):
    lst = [(line.split(',')[0], line.split(',')[1], line.split(',')[2], line.split(',')[3].strip('\n')) for line in open('/opt/files/shas.csv', 'r', encoding='utf-8')]
    check = False
    for page in lst:
        if m == page[0] and d == page[1] and a == page[2]:
            check = True
            break
    if not check: return check
    else: return page[3]

def get_index(m):
    lst = [(line.split(',')[0], line.split(',')[1].strip('\n')) for line in open('/opt/files/shas.csv', 'r', encoding='utf-8')]
    check = False
    for page in lst:
        if m == page[0]:
            check = True
            break
    if not check: return check
    else: return page[1]

if __name__ == '__main__':
    print(get_index('נדרים לז א'))