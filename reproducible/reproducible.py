import os
import time
import errno
# import pickle
import shutil
import dill as pickle
import inspect
import tarfile
import tempfile
import StringIO

# Configurations
cfg = dict()
cfg['data_dir'] = 'data'
cfg['fnc_filename'] = 'fnctext.txt'
cfg['data_filename'] = 'saveddata.pkl'

def create_dir(directory):
    try:
        os.makedirs(directory)
    except OSError as exception:
        if exception.errno != errno.EEXIST:
            raise

def setup_files(model_name):
    directory = cfg['data_dir'] + '/' + model_name
    create_dir(directory)
    return directory

def find_highest_version(directory):
    subdirs = os.listdir(directory)
    if 'v0' not in subdirs:
        return 0
    for i in range(len(subdirs)):
        if 'v' + str(i) in subdirs:
            continue
        return i - 1
    return len(subdirs) - 1

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
    def __init__(self, model_name, pipfreeze = False):
        self.pipfreeze = pipfreeze
        self.model_name = model_name
        self.steps = []

        self.directory = setup_files(model_name)
        self.version = find_highest_version(self.directory)
        self.full_save_path = self.directory + '/v' + str(self.version)

        self.data = dict()

        # If this becomes true, no more data loading will be performed.
        self.repeat_all = False
        if not os.path.exists(self.full_save_path):
            self.new_model()

    def add_step(self, step, always = False):
        new_step = dict()
        new_step['fnc'] = step
        new_step['always'] = always
        self.steps.append(new_step)

    def new_model(self):
        """ This handles the initialization case when version = 0 """
        create_dir(self.full_save_path)
        self.no_more_loading()

    def begin_computing(self):
        old_save_path = self.full_save_path
        self.version += 1
        self.full_save_path = self.directory + '/v' + str(self.version)
        shutil.copytree(old_save_path, self.full_save_path)
        self.no_more_loading()

    def no_more_loading(self):
        self.repeat_all = True
        # pip freeze is slow so we make it a config option
        if self.pipfreeze:
            requirements_file = self.full_save_path + '/requirements.txt'
            os.system('pip freeze > ' + requirements_file)

    def run(self):
        prev_step = None
        for step in self.steps:
            always = step['always']
            s = step['fnc']
            if not always and not self.repeat_all and self.pre_step(s):
                pass
            else:
                if not self.repeat_all:
                    self.begin_computing()
                if prev_step:
                    self.load_data(prev_step['fnc'])
                s(self.data)
                self.post_step(s)
            prev_step = step
        if not self.repeat_all:
            self.load_data(prev_step['fnc'])

    def _get_tar_filename(self, step):
        step_name = step.__name__
        return self.full_save_path + '/' + step_name + '.tar'

    def load_data(self, step):
        file_name = self._get_tar_filename(step)
        if not os.path.exists(file_name):
            return
        with tarfile.open(file_name, 'r') as tar_f:
            data_file = tar_f.extractfile(cfg['data_filename']).read()
            self.data = pickle.loads(data_file)

    def pre_step(self, step):
        file_name = self._get_tar_filename(step)
        if not os.path.exists(file_name):
            return False
        with tarfile.open(file_name, 'r') as tar_f:
            same_fnc = compare_steps(step, tar_f)
            if not same_fnc:
                return False
            return True

    def post_step(self, step):
        file_name = self._get_tar_filename(step)
        function_text = inspect.getsourcelines(step)
        data_dump = pickle.dumps(self.data)
        with tarfile.open(file_name, 'w') as f:
            write_string_to_tar(cfg['fnc_filename'], function_text, f)
            write_string_to_tar(cfg['data_filename'], data_dump, f)


