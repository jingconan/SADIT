all:
	./allinone.py
s:
	cd Simulator && ./fs.py ../test/conf.dot -t 3000
d:
	cd Detector && ./AnomalyDetector.py  ../Simulator/n0_flow.txt
ms:
	rm ./settings.py
	rm ./settings.pyc
	cp ./settings/multi_srv_targ_one.py ./settings.py
	./main.py
t:
	cd test && ./ConfigureTest.py
clean:
	./clean.sh
