"""Test that the mirascope package can be imported without circular import issues."""


def test_can_import_mirascope():
    """Test that the main mirascope package can be imported."""
    import mirascope

    assert mirascope is not None
