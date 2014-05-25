import os
import shutil
import tarfile
from reproducible.reproducible import \
        Reproducible, setup_files, compare_steps,\
        create_dir, find_highest_version

def test_initial():
    model = Reproducible("test1")
    model.run()

def test_one_step():
    def do_nothing(model):
        pass
    model = Reproducible("test2")
    model.add_step(do_nothing)
    model.run()

def test_real_step():
    def set_data(data):
        data['data'] = "hello"
    model = Reproducible("test3")
    model.add_step(set_data)
    model.run()
    assert(model.data['data'] == "hello")

def test_compare_steps():
    if os.path.exists('./data/test3'):
        shutil.rmtree('./data/test3')
    def set_data(data):
        data['data'] = "hello"
    model = Reproducible("test3")
    model.add_step(set_data)
    model.run()
    with tarfile.open('./data/test3/v0/set_data.tar', 'r') as f:
        assert(compare_steps(set_data, f))

def test_setup_files():
    if os.path.exists('./data/test3'):
        shutil.rmtree('./data/test3')
    setup_files('test3')
    assert(os.path.exists('./data/test3'))

def test_data_directory():
    if os.path.exists('./data/test3'):
        shutil.rmtree('./data/test3')
    model = Reproducible("test3")
    assert(os.path.exists('./data/test3'))

def test_find_version_init():
    if os.path.exists('./data/test10'):
        shutil.rmtree('./data/test10')
    create_dir('./data/test10')
    assert(find_highest_version('./data/test10') == 0)

def test_find_version():
    if os.path.exists('./data/test10'):
        shutil.rmtree('./data/test10')
    create_dir('./data/test10/v0')
    create_dir('./data/test10/v1')
    assert(find_highest_version('./data/test10') == 1)

def test_saved_step():
    def set_data(data):
        if set_data.idx > 0:
            data['data'] = "uhoh!"
            return
        data['data'] = "hello"
        set_data.idx += 1
    set_data.idx = 0

    model = Reproducible("test3")
    model.add_step(set_data)
    model.run()
    assert(model.data['data'] == "hello")

    model = Reproducible("test3")
    model.add_step(set_data)
    assert(not 'data' in model.data)
    model.run()
    assert(model.data['data'] == "hello")

def test_new_fnc():
    def set_data(data):
        data['data'] = "hello"
    model = Reproducible("test5")
    model.add_step(set_data)
    model.run()
    def set_data(data):
        data['data'] = "goodbye"
    model = Reproducible("test5")
    model.add_step(set_data)
    model.run()
    assert(model.data['data'] == "goodbye")

def test_multiple_steps():
    def set_data(data):
        if set_data.idx > 0:
            data['data'] = "uhoh!"
            return
        data['data'] = "hello"
        set_data.idx += 1
    set_data.idx = 0

    model = Reproducible("test4")
    model.add_step(set_data)
    model.run()
    assert(model.data['data'] == "hello")
    def set_more_data(data):
        data['stuff'] = "additional"
    model = Reproducible("test4")
    model.add_step(set_data)
    model.add_step(set_more_data)
    model.run()
    assert(model.data['data'] == "hello")
    assert(model.data['stuff'] == "additional")

def test_always():
    def set_data(data):
        data['data'] = set_data.idx
        set_data.idx += 1
    set_data.idx = 0
    model = Reproducible("test_always")
    model.add_step(set_data, always = True)
    model.run()
    model.run()
    model.run()
    assert(model.data['data'] == 2)

def test_new_fnc_new_directory():
    if os.path.exists('./data/test5'):
        shutil.rmtree('./data/test5')
    def set_data(data):
        data['data'] = "hello"
    model = Reproducible("test5")
    model.add_step(set_data)
    model.run()
    assert(os.path.exists('data/test5/v0'))
    def set_data(data):
        data['data'] = "goodbye"
    model = Reproducible("test5")
    model.add_step(set_data)
    model.run()
    assert(os.path.exists('data/test5/v1'))
    assert(model.data['data'] == "goodbye")

def test_pip_freeze():
    if os.path.exists('./data/test5'):
        shutil.rmtree('./data/test5')
    def set_data(data):
        data['data'] = "hello"
    model = Reproducible("test5", pipfreeze = True)
    model.add_step(set_data)
    model.run()
    assert(os.path.exists('data/test5/v0/requirements.txt'))
