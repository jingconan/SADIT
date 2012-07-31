function settings = loadsettings()
    settings_file = './settings.txt';
    [name, val] = textread(settings_file, '%s = %s');
    settings = struct();
    for i = 1:length(name)
        settings = setfield(settings, name{i}, val{i});
    end
    settings
