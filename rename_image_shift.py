
"""
run this command in a directory containing images and corresponding mdoc files
it's probably best to do it on symlinks of the images in case of error. 

tested with python 3.6.5
"""



import os
path ='./'
files = os.listdir(path)
mdoc = []
tif = []

for i in files:
	if 'mdoc' in str(i):
		mdoc.append(i)
	elif '~' in str(i):
		print(str(i) + ' has a tilde') 
	elif 'tif' in i[-4:]:
		tif.append(i)

for i in tif:
	f = open(str(i)+'.mdoc')
	md = f.read()
	multishot = md.find('MultishotHoleAndPosition')
	if multishot == -1:
		print('file '+i+' is missing multishot position')
	else:
		ls = md.splitlines() 
		subs = 'MultishotHoleAndPosition'
		res = [i for i in ls if subs in i]
		if len(res) != 1:
			print('mdoc has more than 1 position '+i)
		pos = str(res[0])[str(res[0]).index('=')+2:]
		os.rename(i, str(i[:i.find('.')]+'_'+pos+'.tif'))
		
print('\n'+'NEXT TIME CHECK THE BOX IN SERIAL EM!!!'+'\n')
