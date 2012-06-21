% Read the flows from a FS output file.
%
%   f = readfsflows(fname)
%   ... = readfsflows(...,reverseit,sortit)
%
%   fname - String of the name of the FS output file.
%
%   reverseit - If supplied as 1, the flows in f are
%                       reversed after being read.
%   sortit    - If supplied as 1, the flows in f are sorted in
%               chronological order.
%
% 
%   f     - Cell array of n elements. f{i} is a structure associated with
%           the i-th flow. f{i} has the following fields:
%           t       - Time of the start of the flow.
%           deltat  - Length of time of the flow.
%           client  - Vector of length 5. Elements represent the client's
%                     IP address and port.
%           loc     - Vector of length 2. Elements are the lat/long pair of
%                     the client's location.
%           bytes   - Size of the flow, in bytes.           
%
%           
% R Taylor Locke
% 10/13/11
function f = readfsflows(fname,reverseit,sortit)
fid = fopen(fname);

if nargin < 2
    reverseit = false;
    sortit = false;
end

if nargin < 3
    sortit = false;
end

% Pre-allocate f for sake of speed.
Nflows = 1000;
nflows = 0;
f = cell(Nflows,1);

% Skip ahead to the first flow.
tline = fgetl(fid);
while ~strcmpi(tline(1),'t')
    tline = fgetl(fid);
end

% Read all flows.
while ischar(tline)
    % Determine if f needs to be re-allocated.
    nflows = nflows + 1;
    if nflows > Nflows
        disp(['nflows = ' num2str(nflows)])
        temp = f;
        Nflows = Nflows + 1000;
        f = cell(Nflows,1);
        for i = 1:numel(temp)
            f{i} = temp{i};
        end
        clear temp
    end
    
    % Important information is space-delimited.
    ispace = strfind(tline,' ');
    f{nflows}.t = str2double(tline((ispace(3) + 1):(ispace(4) - ...
                                                    1)));
    f{nflows}.deltat = str2double(tline((ispace(4) + 1):(ispace(5) ...
                                                      - 1))) - ...
        f{nflows}.t;
    
    ipstr = tline((ispace(5) + 1):(ispace(6) - 1));
    idot = strfind(ipstr,'.');
    icolon = strfind(ipstr,':');
    idash = strfind(ipstr,'-');
    if numel(idot) < 3
        error(['Not enough IP data. nflows = ' num2str(nflows)])
    end
    if numel(icolon) < 1
        error(['No port information. nflows = ' num2str(nflows)])
    end
    if numel(idash) < 1
        error(['No direction information. nflows = ' num2str(nflows) ...
              '. ipstr = ' ipstr '. idash = ' idash])
    end
    f{nflows}.client = [str2double(ipstr(1:(idot(1) - 1))) ...
        str2double(ipstr((idot(1) + 1):(idot(2) - 1))) ...
        str2double(ipstr((idot(2) + 1):(idot(3) - 1))) ...
        str2double(ipstr((idot(3) + 1):(icolon(1) - 1))) ...
        str2double(ipstr((icolon(1) + 1):(idash - 1)))];

    % -------revision by J.C.W -------------
    % [lat,lon] = locbyip(f{nflows}.client(1:4));
    % f{nflows}.loc = [lat lon];
    f{nflows}.loc = [0, 0];
    % -------end revision by J.C.W -------------
    
    f{nflows}.bytes = str2double(tline((ispace(10) + 1):(ispace(11) - 1)));
    
    % Prepare for next iteration.
    tline = fgetl(fid);
    if ~strcmp(tline(1),'t')
       break
    end
end

fclose(fid);

% Re-size the pre-allocated f.

temp = cell(nflows,1);
for i = 1:nflows
    if reverseit
        temp{nflows - i + 1} = f{i};
    else
        temp{i} = f{i};
    end
end

if sortit
    t = zeros(nflows,1);

    for i = 1:nflows
        t(i) = temp{i}.t;
    end

    [t,j] = sort(t);
    f = cell(nflows,1);
    for i = 1:nflows
        f{i} = temp{j(i)};
    end
else
    f = temp;
end
