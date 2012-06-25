% Evaluate the accuracy when atypical download sizes are
% consdiered.
%
% R Taylor Locke
% 1/12/12
clear

load atypicalsizetest
load atypicalsizetrain

% Add some more noise to the data.
ntrain = numel(ytrain);
ntest = numel(ytest);
xtrain(:,3) = xtrain(:,3) + 295*randn(ntrain,1);
xtest(:,3) = xtest(:,3) + 295*randn(ntest,1);
ineg = ytest < 0;
nd = sum(ineg);
nr = sum(~ineg);

% Re-assign the anomalous durations to reflect nominal durations.
mdt = mean(xtest(~ineg,2));
sdt = std(xtest(~ineg,2));
xtest(ineg,2) = mdt + sdt*randn(nd,1);

% Scale the training data and train the detector.
writeinfile(ytrain,xtrain,'atypicalsize_train.dat');
system(['~/libsvm-3.1/svm-scale -s atypicalsize.sf atypicalsize_train.dat ' ...
        '> atypicalsize_train.scaled'])
system(['~/libsvm-3.1/svm-train -s 2 -h 0 -n 0.001 ' ...
        'atypicalsize_train.scaled atypicalsize.model'])

% Scale the test data and evalute the detector's perforance when a
% varying download size is insertd in to the data.
nvals = 20;
dspan = 0.005;
C = mean(xtrain(:,3));
A = C*(1 - dspan);
B = C*(1 + dspan);
vals = linspace(A,B,nvals);
pd = zeros(nvals,1);
pfa = zeros(nvals,1);
d = zeros(nvals,1);
rates = zeros(ntest,1);
rates(~ineg) = xtest(~ineg,3)./xtest(~ineg,2);
rates(ineg) = (xtest(ineg,3)/10)./xtest(ineg,2);
for i = 1:nvals
    x = xtest;
    x(ineg,3) = vals(i);
    
    % Durations must be adjusted as well.
    x(ineg,2) = x(ineg,3)./rates(ineg);

    writeinfile(ytest,x,'atypicalsize_test.dat');
    system(['~/libsvm-3.1/svm-scale -r atypicalsize.sf ' ...
            'atypicalsize_test.dat > atypicalsize_test.scaled'])
    system(['~/libsvm-3.1/svm-predict atypicalsize_test.scaled ' ...
            'atypicalsize.model atypicalsize_test.pred'])
    ypred = dlmread('atypicalsize_test.pred');
    inegpred = ypred < 0;
    pdi = sum(inegpred & ineg)/nd
    pfai = sum(inegpred & ~ineg)/nr
    di = vals(i) - C
    
    pd(i) = pdi;
    pfa(i) = pfai;
    d(i) = di;
end

save rocatypicalsize pd pfa d