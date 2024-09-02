from privacera_shield.util import AtomicCounter


def test_atomic_counter():
    counter = AtomicCounter()
    assert counter.increment() == 1
    assert counter.increment() == 2
