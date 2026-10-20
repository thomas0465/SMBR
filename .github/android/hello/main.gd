extends Control
## Engine sanity test for the SMBR Android build.
## If this opens, the Godot engine, the signing and this device are all fine.

func _ready() -> void:
	var label := Label.new()
	label.set_anchors_preset(Control.PRESET_FULL_RECT)
	label.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
	label.add_theme_font_size_override("font_size", 22)
	label.text = "\n".join([
		"SMBR engine test: OK",
		"Godot " + Engine.get_version_info().string,
		"OS: %s %s" % [OS.get_name(), OS.get_version()],
		"Device: %s / %s" % [OS.get_model_name(), OS.get_processor_name()],
		"GPU: %s" % RenderingServer.get_video_adapter_name(),
		"Renderer: %s" % RenderingServer.get_current_rendering_method(),
		"Screen: %s" % str(DisplayServer.screen_get_size()),
		"User dir: %s" % OS.get_user_data_dir(),
		"Gamepads: %s" % str(Input.get_connected_joypads()),
	])
	add_child(label)
