import os
import time
import errno
import pickle
import inspect
import tarfile
import tempfile
import StringIO

# Configurations
cfg = dict()
cfg['data_dir'] = 'data'
cfg['fnc_filename'] = 'fnctext.txt'
cfg['data_filename'] = 'saveddata.pkl'

def setup_files(model_name):
    directory = cfg['data_dir'] + '/' + model_name
    try:
        os.makedirs(directory)
    except OSError as exception:
        if exception.errno != errno.EEXIST:
            raise
    return directory

def write_string_to_tar(filename, s, tar_f):
    string = StringIO.StringIO()
    string.write(s)
    string.seek(0)
    info = tarfile.TarInfo(name = filename)
    info.size = len(string.buf)
    info.mtime = time.time()
    tar_f.addfile(tarinfo = info, fileobj = string)

def compare_steps(s, tar_f):
    saved = tar_f.extractfile(cfg['fnc_filename']).read()
    new = inspect.getsourcelines(s)
    # StringIO does some funky escaping when we write to it
    # so in order to compare we must write to it again
    string = StringIO.StringIO()
    string.write(new)
    return string.getvalue() == saved


"""
A class for organizing repeatable, reproducible model runs.
"""
class Reproducible(object):
    def __init__(self, model_name):
        self.model_name = model_name
        self.steps = []
        self.directory = setup_files(model_name)
        self.data = dict()
        # If this becomes true, no more data loading will be performed.
        self.repeat_all = False

    def add_step(self, step, always = False):
        self.steps.append((step, always))

    def run(self):
        for (s, always) in self.steps:
            if not always and not self.repeat_all and self.pre_step(s):
                continue
            self.repeat_all = True
            s(self.data)
            self.post_step(s)

    def _get_tar_filename(self, step):
        step_name = step.__name__
        return self.directory + '/' + step_name + '.tar'

    def pre_step(self, step):
        file_name = self._get_tar_filename(step)
        if not os.path.exists(file_name):
            return False
        with tarfile.open(file_name, 'r') as tar_f:
            same_fnc = compare_steps(step, tar_f)
            if not same_fnc:
                return False
            data_file = tar_f.extractfile(cfg['data_filename']).read()
            self.data = pickle.loads(data_file)
            return True

    def post_step(self, step):
        file_name = self._get_tar_filename(step)
        function_text = inspect.getsourcelines(step)
        data_dump = pickle.dumps(self.data)
        with tarfile.open(file_name, 'w') as f:
            write_string_to_tar(cfg['fnc_filename'], function_text, f)
            write_string_to_tar(cfg['data_filename'], data_dump, f)


