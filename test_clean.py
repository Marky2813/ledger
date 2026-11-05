from clean import strip_html

def test_clean():
    assert strip_html("&lt;div&gt;Hello &amp; Welcome&lt;/div&gt;") == "Hello & Welcome"