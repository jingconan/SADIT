all:
	python Detector.py
p:
	/usr/bin/python -m cProfile -o OpenGLContext.profile Detector.py 
	runsnake OpenGLContext.profile
share:
	sh manshare.sh

clean:
	rm *.pyc
	rm ./output/*.txt
	rm ./output/*.jpeg
	rm X.txt b.txt A.txt

push:
	./hg-push.sh



