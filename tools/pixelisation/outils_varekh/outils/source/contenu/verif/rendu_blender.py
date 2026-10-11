import bpy, sys
out, moteur = sys.argv[-2], sys.argv[-1]
bpy.ops.wm.read_factory_settings(use_empty=False)
s = bpy.context.scene
s.render.engine = moteur
s.render.resolution_x = s.render.resolution_y = 128
s.render.filepath = out
bpy.ops.render.render(write_still=True)
print("RENDU_OK", moteur, bpy.app.version_string)
