extends Node2D
var f := 0
func _ready():
	var r := ColorRect.new(); r.color = Color(0.05, 0.35, 0.6); r.size = Vector2(280, 140); r.position = Vector2(20, 20); add_child(r)
	var l := Label.new(); l.text = "Godot OK"; l.position = Vector2(40, 40); add_child(l)
	var c := Polygon2D.new(); c.polygon = PackedVector2Array([Vector2(200,60), Vector2(260,150), Vector2(140,150)]); c.color = Color(1, 0.6, 0.1); add_child(c)
func _process(_d):
	f += 1
	if OS.get_environment("VERIF_ATTENTE") != "":
		if Time.get_ticks_msec() > 7000: get_tree().quit()
		return
	if f == 10:
		var sortie := OS.get_environment("VERIF_SORTIE")
		var e := get_viewport().get_texture().get_image().save_png(sortie)
		print("CAPTURE_GODOT ", e, " ", RenderingServer.get_video_adapter_name())
		get_tree().quit()
