extends Control
## Replacement main scene for startup bisect builds. Shows which parts of the game's startup survived.

func _ready() -> void:
	var autoloads: Array[String] = []
	for prop in ProjectSettings.get_property_list():
		var n: String = prop.name
		if n.begins_with("autoload/"):
			autoloads.append(n.trim_prefix("autoload/"))
	var label := Label.new()
	label.set_anchors_preset(Control.PRESET_FULL_RECT)
	label.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
	label.add_theme_font_size_override("font_size", 22)
	label.text = "\n".join([
		"SMBR bisect build: __VARIANT__",
		"STARTUP OK",
		"Autoloads that loaded (%d):" % autoloads.size(),
		", ".join(autoloads) if autoloads.size() > 0 else "(none)",
	])
	add_child(label)
	print("BISECT_OK __VARIANT__ autoloads=", autoloads)
