function writeinfile(label, feature, name)
    fid = fopen(name, 'w');
    n = length(label);
    fea_num = size(feature, 2);
    for i = 1:n
        line = num2str(label(i));
        for j = 1:fea_num
            line = [line, ' ', num2str(j), ':', num2str(feature(i, j))];
        end
        fprintf(fid, '%s\n', line);
    end
    fclose(fid);
end
