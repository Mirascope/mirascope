from mirascope.llm._response_metaclass import _ResponseMetaclass


def test_response_metaclass():
    class TestClass(metaclass=_ResponseMetaclass):
        def __init__(self):
            self.value_x = 1

        @property
        def value_y(self):
            return 2

    test_instance = TestClass()
    assert test_instance.value_y == 2
