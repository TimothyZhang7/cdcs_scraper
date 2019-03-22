import csv

outfile = open('professor_xref.csv', 'w', encoding='utf-8')
out_handler = csv.writer(outfile, delimiter=',')

def main():
	cdcs = []
	with open('cdcs_fall2019_open.csv', 'r', encoding='utf-8') as f:
		reader = csv.reader(f)
		cdcs = list(reader)	

	professors = []
	with open('cleaned_professor.csv', 'r', encoding='utf-8') as f:
		reader = csv.reader(f)
		professors = list(reader)	

	abbr_name = []
	for row in cdcs:
		if len(row) >= 13:
			abbr_name.append(row[12])	

	full_name = []
	for row in professors:
		if len(row) >= 1:
			full_name.append(row[0])	

	full_name = Remove(full_name)
	abbr_name = Remove(abbr_name)


	pairs = []
	for i in full_name:
		for j in abbr_name: 
			if ';' in j:
				l = j.split(';')
				if match(i, l[0]):
					tup = list()
					tup.append(i)
					tup.append(j)
					out_handler.writerow(tup)
					pairs.append(i+' -> '+l[0])
					print(i+' -> '+l[0])
#				for n in l:
#					n = n.strip()
#					if match(i, n):
#						pairs.append(i+' -> '+j)
#						print(i+' -> '+j)
			else:
				if match(i, j):
					tup = list()
					tup.append(i)
					tup.append(j)
					out_handler.writerow(tup)
					pairs.append(i+' -> '+j)
					print(i+' -> '+j)

	pairs = Remove(pairs)
	print('#Full: '+str(len(full_name)))
	print('#Abbr: '+str(len(abbr_name)))
	print('#Match: '+str(len(pairs)))	

def match(i, j):
	temp_f = i.lower()
	temp_a = j.lower()
	lf = temp_f.split(',')
	if len(lf)>= 2:
		first_f = lf[1].strip()
		last_f = lf[0].strip()
	else:
		first_f = '?'
		last_f = lf[0].strip()
	la = temp_a.split(' ')
	if len(la)>= 2:
		first_a = la[1].strip()
		last_a = la[0].strip()
	else:
		first_a = '?'
		last_a = la[0].strip()
	if last_a == last_f and first_a[0]==first_f[0]:
		return True
	else:
		return False

def Remove(duplicate): 
    final_list = [] 
    for num in duplicate: 
        if num not in final_list: 
            final_list.append(num) 
    return final_list 

main()