# -*- coding: utf-8 -*-

import gc

from nose.tools import assert_raises, assert_equal, assert_not_equal
from vispy.testing import assert_in, run_tests_if_main

from vispy import gloo
from vispy.gloo import (GLContext, get_default_config,
                        get_current_context, get_a_context)


class DummyCanvasBackend(object):
    
    def __init__(self):
        self.set_current = False
    
    def _vispy_set_current(self):
        self.set_current = True


def test_context_getting():
    """ Test getting a context object """
    
    # Reset
    GLContext._current_context = None
    GLContext._default_context = None 
    
    c1 = get_a_context()
    c2 = get_a_context()
    assert c1 is c2
    
    c3 = gloo.context.get_new_context()
    c3.take('test', DummyCanvasBackend())
    c4 = gloo.context.get_new_context()
    c4.take('test', DummyCanvasBackend())
    assert c3 is c1
    assert c4 is not c3
    
    c5 = get_a_context()
    c6 = get_a_context()
    assert c5 is c6
    assert c5 is c4
    
    c3.set_current(False)
    assert get_a_context() is c3
    
    
def test_context_config():
    """ Test GLContext handling of config dict
    """
    default_config = get_default_config()
    
    # Pass default config unchanged
    c = GLContext(default_config)
    assert_equal(c.config, default_config)
    # Must be deep copy
    c.config['double_buffer'] = False
    assert_not_equal(c.config, default_config)
    
    # Passing nothing should yield default config
    c = GLContext()
    assert_equal(c.config, default_config)
    # Must be deep copy
    c.config['double_buffer'] = False
    assert_not_equal(c.config, default_config)
    
    # This should work
    c = GLContext({'red_size': 4, 'double_buffer': False})
    assert_equal(c.config.keys(), default_config.keys())
    
    # Passing crap should raise
    assert_raises(KeyError, GLContext, {'foo': 3})
    assert_raises(TypeError, GLContext, {'double_buffer': 'not_bool'})
    

def test_context_taking():
    """ Test GLContext ownership and taking
    """
    def get_canvas(c):
        return c.backend_canvas
    
    cb = DummyCanvasBackend()
    c = GLContext()
    
    # Context is not taken and cannot get backend_canvas
    assert not c.istaken
    assert_raises(RuntimeError, get_canvas, c)
    assert_in('no backend', repr(c))
    
    # Take it
    c.take('test-foo', cb)
    assert c.backend_canvas is cb
    assert_in('test-foo backend', repr(c))
    
    # Now we cannot take it again
    assert_raises(RuntimeError, c.take, 'test', cb)
    
    # Canvas backend can delete (we use a weak ref)
    cb = DummyCanvasBackend()  # overwrite old object
    gc.collect()
    
    # Still cannot take it, but backend is invalid
    assert_raises(RuntimeError, c.take, 'test', cb)
    assert_raises(RuntimeError, get_canvas, c)


def test_context_activating():
    """ Test GLContext activation and obtaining current context
    """
    
    # Reset
    GLContext._current_context = None
    
    c1 = GLContext()
    c2 = GLContext()
    
    assert get_current_context() is None
    
    # Need backend to make current
    assert_raises(RuntimeError, c1.set_current)
    
    # Unless we do this
    c1.set_current(False)
    assert get_current_context() is c1
    assert c1.iscurrent
    
    # Switch
    c2.set_current(False)
    assert get_current_context() is c2
    assert c2.iscurrent
    
    # Now try with backend
    cb1 = DummyCanvasBackend()
    c1.take('test', cb1)
    assert cb1.set_current is False
    assert get_current_context() is c2
    c1.set_current()
    assert get_current_context() is c1
    assert cb1.set_current is True


run_tests_if_main()
