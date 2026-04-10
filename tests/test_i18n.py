from b2t.i18n import normalize_language, tr


def test_normalize_language_accepts_short_codes() -> None:
    assert normalize_language("zh") == "zh-CN"
    assert normalize_language("en") == "en-US"


def test_translate_falls_back_to_default_language() -> None:
    assert tr("unknown", "web_submit") == "开始转写"
