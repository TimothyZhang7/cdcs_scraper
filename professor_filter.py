import csv

SCHEMA_ORIGIN = ['name', 'avatar', 'intro', 'email', 'note', 'cv_url', 'website']
NEW_SCHEMA = ['name', 'email', 'website', 'cv_url', 'avatar', 'intro', 'note', 'create_t', 'update_t']

def main():
	indata = []
	with open('professor.csv', 'r', encoding='utf-8') as f:
		reader = csv.reader(f)
		indata = list(reader)
	outfile = open('cleaned_professor.csv', 'w', encoding='utf-8')
	out_handler = csv.writer(outfile, delimiter=',')
	where_o = get_indexer(SCHEMA_ORIGIN)

	for row in indata:
		if len(row) >= 7:
			tupn = []
			for i in range(len(NEW_SCHEMA)):
				tupn.append('NULL')
				if NEW_SCHEMA[i] in SCHEMA_ORIGIN:
					tupn[i] = row[where_o[NEW_SCHEMA[i]]]
				else:
					tupn[i] = 'NULL'
			print(tupn)
			out_handler.writerow(tupn)

	outfile.close()
	print('finish')

def get_indexer(schema):
	indexer = dict()
	i = 0
	for attr in schema:
		indexer[attr] = i
		i = i+1
	return indexer

main()