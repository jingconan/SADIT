all:
	./allinone.py
d:
	cd Detector && ./Detector.py  ../Simulator/n0_flow.txt ''
ms:
	rm ./settings.py
	rm ./settings.pyc
	cp ./settings/multi_srv_targ_one.py ./settings.py
	./main.py
t:
	cd test && ./ConfigureTest.py
