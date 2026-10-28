@tool
extends SceneTree

func _init():
	print("TESTING FONT LOADING IN GODOT 4.3")
	var font = FontFile.new()
	var err = font.load_dynamic_font("res://fonts/simhei.ttf")
	print("load_dynamic_font result: %d" % err)
	if err == OK:
		var theme = Theme.new()
		theme.default_font = font
		var label = Label.new()
		label.theme = theme
		label.text = "素纸 · 1. 原野 · 晨曦微光"
		print("Label created with Chinese text: %s" % label.text)
	quit(0)
