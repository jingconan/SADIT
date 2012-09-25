% Translate an IP address to a point on the "IP line".
%
% R Taylor Locke
% 10/26/11
function y = ip2int(x)
y = x*(256.^[3; 2; 1; 0]);