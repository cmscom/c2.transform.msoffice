def test_version():
    from c2.transform.msoffice import __version__

    assert __version__ == "2.0.0.dev0"


def test_c2_is_a_pep420_namespace():
    import c2
    import c2.transform

    assert getattr(c2, "__file__", None) is None
    assert getattr(c2.transform, "__file__", None) is None
