# Change Window
./run.py -e DetectExper -d ../demo_test_data/flow_size_mean_2x_t_5000s_anomaly_1000s_to_1300s/n0_flow.txt --data_type=fs --hoeff_far=0.001 --win_size=10 --pic_name=./Share/win_10_flow_size_mean.eps
./run.py -e DetectExper -d ../demo_test_data/flow_size_mean_2x_t_5000s_anomaly_1000s_to_1300s/n0_flow.txt --data_type=fs --hoeff_far=0.001 --win_size=50 --pic_name=./Share/win_50_flow_size_mean.eps
./run.py -e DetectExper -d ../demo_test_data/flow_size_mean_2x_t_5000s_anomaly_1000s_to_1300s/n0_flow.txt --data_type=fs --hoeff_far=0.001 --win_size=200 --pic_name=./Share/win_200_flow_size_mean.eps


# Change hoeffding rule
./run.py -e DetectExper -d ../demo_test_data/flow_size_mean_2x_t_5000s_anomaly_1000s_to_1300s/n0_flow.txt --data_type=fs --hoeff_far=0.001 --win_size=200 --pic_name=./Share/win_200_flow_size_mean.eps

./run.py -e DetectExper -d ../demo_test_data/flow_size_mean_2x_t_5000s_anomaly_1000s_to_1300s/n0_flow.txt --data_type=fs --hoeff_far=0.001 --win_size=200 --pic_name=./Share/win_200_flow_size_mean.eps

