from android.uiautomator import UIHierarchyParser

SAMPLE_XML = """<?xml version='1.0' encoding='UTF-8' standalone='yes' ?>
<hierarchy rotation="0">
  <node index="0" text="" resource-id="" class="android.widget.FrameLayout" package="com.android.settings" bounds="[0,0][1080,2400]">
    <node index="0" text="Settings" resource-id="com.android.settings:id/settings_title" class="android.widget.TextView" package="com.android.settings" bounds="[60,120][300,200]" clickable="false" />
    <node index="1" text="Network &amp; internet" resource-id="android:id/title" class="android.widget.TextView" package="com.android.settings" bounds="[60,300][900,450]" clickable="true" />
  </node>
</hierarchy>
"""

def test_hierarchy_parsing():
    elements = UIHierarchyParser.parse(SAMPLE_XML)
    assert len(elements) == 2
    assert elements[0].text == "Settings"
    assert elements[0].center == (180, 160)
    assert elements[1].text == "Network & internet"
    assert elements[1].is_clickable is True

def test_find_by_text():
    elements = UIHierarchyParser.parse(SAMPLE_XML)
    found = UIHierarchyParser.find_by_text(elements, "Network")
    assert len(found) == 1
    assert found[0].center == (480, 375)
