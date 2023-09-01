function []=convert_otb_to_mat_files()
%Reads files of type OTB+, extrapolating the information on the signal,
%in turn uses the xml2struct function to read file.xml and allocate them in an easily readable Matlab structure.
% Isn't possible to read OTB files because the internal structure of these
% files is different.

% clear all
close all
fclose all
clc

% Get a directory from the user
directory_path = uigetdir;

% Get a list of all OTB+ files in the specified directory
files = dir(fullfile(directory_path, '*.otb+'));

for idx = 1:length(files)
    FILENAME = files(idx).name;
    PATHNAME = files(idx).folder;
    
    mkdir('tmpopen');
    
    % Debug
    disp(['Processing: ' FILENAME]);
    
    untar([PATHNAME '/' FILENAME],'tmpopen');
    signals=dir(fullfile('tmpopen','*.sig'));
    for nSig=1:length(signals)
        PowerSupply{nSig}=3.3;
        abstracts{nSig}=[signals(nSig).name(1:end-4) '.xml'];
        abs = xml2struct(fullfile('.','tmpopen',abstracts{nSig}));
        for nAtt=1:length(abs.Device.Attributes)
            Fsample{nSig}=str2num(abs.Device.Attributes.SampleFrequency);
            nChannel{nSig}=str2num(abs.Device.Attributes.DeviceTotalChannels);
            nADBit{nSig}=str2num(abs.Device.Attributes.ad_bits);
        end
        vett=zeros(1,nChannel{nSig});
        Gains{nSig}=vett;
        for nChild=1:length(abs.Device.Channels.Adapter)
            localGain{nSig}=str2num(abs.Device.Channels.Adapter{nChild}.Attributes.Gain);
            startIndex{nSig}=str2num(abs.Device.Channels.Adapter{nChild}.Attributes.ChannelStartIndex);
            
            Channel = abs.Device.Channels.Adapter{nChild}.Channel;
            for nChan=1:length(Channel)
                if iscell(Channel)
                    ChannelAtt = Channel{nChan}.Attributes;
                elseif isstruct(Channel)
                    ChannelAtt = Channel(nChan).Attributes;
                end
                idx=str2num(ChannelAtt.Index);
                Gains{nSig}(startIndex{nSig}+idx+1)=localGain{nSig};
                
            end
        end
        
        h=fopen(fullfile('tmpopen',signals(nSig).name),'r');
        data=fread(h,[nChannel{nSig} Inf],'short');
        fclose(h);
        
        % Save all important variables in a .mat file
        output_file_path = fullfile(PATHNAME, [FILENAME(1:end-5) '.mat']);
        save(output_file_path, 'PowerSupply', 'Fsample', 'nChannel', 'nADBit', 'Gains', 'data');
    end
    
    rmdir('tmpopen','s');
    
    % Delete original OTB+ file after conversion
    delete(fullfile(PATHNAME, FILENAME));
end
end
