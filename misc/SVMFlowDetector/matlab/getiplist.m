% Get a list of all IP addresses in the data.
%
% R Taylor Locke
% 5/31/12
clear


% f_all = readfsflows('n0_flow_2.txt');
f_all = readfsflows('n0_flow_5.txt');


% Compile IP list on the fly.
iplist = [];
nip = 0;
for i = 1:numel(f_all)
    % Get integer representation of i-th flow's IP address.
    ipfound = false;
    ipi = ip2int(f_all{i}.client(1:4));

    % Check to see if IP address already found.
    j = 1;
    while j <= nip 
        ipfound = ipi == iplist(j);
        if ipfound
            break
        end
        j = j + 1;
    end
    
    % If the IP address has not already been found, append the list.
    if ~ipfound
        iplist = [iplist; ipi];
        nip = nip + 1;
    end
end

% Display the number of IP addresses found and save the IP list.
disp([num2str(nip) ' IP addresses found'])

save iplist iplist