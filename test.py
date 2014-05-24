import os
import shutil
import tarfile
from reproducible.reproducible import \
        Reproducible, setup_files, compare_steps

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
    def set_data(data):
        data['data'] = "hello"
    model = Reproducible("test3")
    model.add_step(set_data)
    model.run()
    with tarfile.open('./data/test3/set_data.tar', 'r') as f:
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
    def set_more_data(data):
        data['stuff'] = "additional"
    model = Reproducible("test4")
    model.add_step(set_data)
    model.add_step(set_more_data)
    model.run()
    assert(model.data['data'] == "hello")
    assert(model.data['stuff'] == "additional")
