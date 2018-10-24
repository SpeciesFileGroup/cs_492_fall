def extract_data():
	with open('journal_data.log') as f:
		content = f.readlines()

	content = [x.strip() for x in content]
	X = content[::2]
	y = content[1::2]

	y = [int(item.split(':')[1]) for item in y]
	return X, y

