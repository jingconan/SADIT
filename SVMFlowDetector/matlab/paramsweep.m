% Look for ideal parameters.
%
% R Taylor Locke
% 6/12/12
clear

load iplist

deltat = [30 60 90 120 180 240];
gamma = [0.001 0.01 0.1 1 10 100];
ndeltat = numel(deltat);
ngamma = numel(gamma);

ext = {'2','3','4','5'};
next = numel(ext);

pd = cell(next,1);
pfa = cell(next,1);
for i = 1:next
    flowfn = ['flowdata_' ext{i} '.mat'];
    pd{i} = zeros(ndeltat,ngamma);
    pfa{i} = zeros(ndeltat,ngamma);
    for j = 1:ndeltat
        for k = 1:ngamma
            readtraintest(ext{i},iplist,deltat(j),gamma(k),flowfn);
            ypred = dlmread(['test_' ext{i} '.pred']);
            fn = ['testset_' ext{i} '.mat'];
            s = load(fn);
            y = s.y;
            ialarm = y == -1;
            ialarmpred = ypred == -1;
            nalarm = sum(ialarm);
            nrest = sum(~ialarm);
            pd{i}(j,k) = sum(ialarm & ialarmpred)/nalarm;
            pfa{i}(j,k) = sum(~ialarm & ialarmpred)/nrest;
        end
    end
end




save pdpfa pd pfa