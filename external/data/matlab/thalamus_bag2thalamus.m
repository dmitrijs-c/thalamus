function thalamus2mat(path)
  fid = fopen(path);

  try
    for i = 1:10
      record = thalamus_readrecord(fid);
      if isfield(record, 'image')
        'image'
      elseif isfield(record, 'analog')
        'analog'
        record
      end
    end
  catch ME
    rethrow(ME)
  end

  fclose(fid)
end
