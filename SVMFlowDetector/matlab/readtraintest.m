% Read in a scenario, train a one class SVM, and test its
% performance.
%
% ext - String of file name extension. e.g., ext = '2'
% iplist - List of IPs, as found by getiplist.m.
% deltat - Length of evaluation window, in seconds.
% gamma - Radial basis function parameter, for SVM kernel.
% flowfn - Optional. Name of .mat file containing flows contained
%          in the files referenced by ext, if they've already been read.
%
% R Taylor Locke
% 6/11/12
function readtraintest(ext,iplist,deltat,gamma,flowfn)
    tic;
    nargin
    if nargin == 0
        ext = '5';
        load iplist
        deltat = 30;
        gamma = 0.01;
    end
    
    iplist = sort(iplist);
    nip = numel(iplist);
    
    % If flows have already been read, skip to building the sets.
    if nargin > 4
        load(flowfn)
    else
        allfn = ['n0_flow_' ext '.txt'];
        anomfn = ['abnormal_flow_' ext '.txt'];
    
        % The first flows are the test flows, the last flows are the
        % training flows.
        f_all = readfsflows(allfn);
        f_anom = readfsflows(anomfn);
    
        savefn = ['flowdata_' ext '.mat'];
        save(savefn,'f_all','f_anom')
    end
    
    tteststop = f_anom{end}.t + 2*deltat;
    iteststop = 1;
    while f_all{iteststop}.t < tteststop
        iteststop = iteststop + 1;
    end
    
    itrainstart = iteststop + 1;
    
    % Build training set.
    n = numel(f_all);
    ntrain = n - itrainstart + 1;
    x = zeros(ntrain,nip);
    y = ones(ntrain,1);
    itrain = 1;
    
    % Find the flows that fall within the first time window.
    i0 = itrainstart;
    t0 = f_all{i0}.t;
    i1 = i0 + 1;
    t1 = t0 + deltat;
    while f_all{i1}.t < t1
        i1 = i1 + 1;
    end
    
    % Count occurances of flows within time windows.
    while i1 < n
        xi = zeros(1,nip);
        for j = i0:i1
            k = 1;
            ipj = ip2int(f_all{j}.client(1:4));
            while iplist(k) < ipj
                k = k + 1;
            end
            xi(k) = xi(k) + 1;
        end
        x(itrain,:) = xi;
        itrain = itrain + 1;
        
        % Determine the start and stop of the next time widow.
        t0 = t0 + 1;
        while f_all{i0}.t < t0
            i0 = i0 + 1;
        end
        
        t1 = t0 + deltat;
        if t1 > f_all{end}.t
            break
        end
        
        while f_all{i1}.t < t1
            i1 = i1 + 1;
        end
    end
    ntrain = itrain - 1;
    x = x(1:ntrain,:);
    y = y(1:ntrain);
    sf = max(x(:));
    x = x/sf;
    x = [x zeros(ntrain,nip)];
    
    savefn = ['trainset_' ext '.mat'];
    save(savefn,'x','y','deltat','sf')
    
    trainfn = ['train_' ext '.dat'];
    writeinfile(y,x,trainfn);
    
    % Build test set.
    ntest = iteststop;
    x = zeros(ntest,nip);
    largecount = zeros(ntest,nip);
    y = ones(ntest,1);
    itest = 1;
    
    % Find the flows that fall within the first time window.
    i0 = 1;
    t0 = f_all{i0}.t;
    i1 = i0 + 1;
    t1 = t0 + deltat;
    tanomstart = f_anom{1}.t;
    tanomstop = f_anom{end}.t;
    while f_all{i1}.t < t1
        i1 = i1 + 1;
    end
    
    % Count occurances of flows within time windows.
    while i1 < ntest
        xi = zeros(1,nip);
        for j = i0:i1
            k = 1;
            ipj = ip2int(f_all{j}.client(1:4));
            while iplist(k) < ipj
                k = k + 1;
            end
            xi(k) = xi(k) + 1;
            if f_all{j}.bytes > 5e5
                largecount(k) = largecount(k) + 1;
            end
        end
        x(itest,:) = xi;
        
        % Check for anomaly.
        if (tanomstart < t1 && t1 < tanomstop) || (tanomstart < t0 ...
                                                    && t0 < tanomstop)
            y(itest) = -1;
        end
        itest = itest + 1;
        
        % Determine the start and stop of the next time window.
        t0 = t0 + 1;
        while f_all{i0}.t < t0
            i0 = i0 + 1;
        end
        
        t1 = t0 + deltat; 
        while f_all{i1}.t < t1
            i1 = i1 + 1;
        end
    end
    
    ntest = itest - 1;
    x = x(1:ntest,:);
    largecount = largecount(1:ntest,:);
    y = y(1:ntest);
    x = x/sf;
    x = [x largecount];
    
    savefn = ['testset_' ext '.mat'];
    save(savefn,'x','y','deltat','sf')
    
    testfn = ['test_' ext '.dat'];
    writeinfile(y,x,testfn);
    
    SVM_FOLDER = '/home/wangjing/LocalResearch/CyberSecurity/taylor/svm_detector/libsvm-3.12/'
    % Train the SVM.
    system([SVM_FOLDER, 'svm-train -s 2 -n 0.001 -g ' num2str(gamma) ' train_' ext '.dat ' ...
            'train_' ext '.model'])
    
    % Compute training error.
    system([SVM_FOLDER, 'svm-predict train_' ext '.dat train_' ext ...
            '.model train_' ext '.pred'])
    
    % Test.
    system([SVM_FOLDER, 'svm-predict test_' ext '.dat train_' ext ...
            '.model test_' ext '.pred'])
    toc
