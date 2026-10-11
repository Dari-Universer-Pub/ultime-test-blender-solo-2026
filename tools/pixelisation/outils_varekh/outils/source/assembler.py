#!/usr/bin/env python3
"""Assemble le dossier portable outils-varekh (runtime Ubuntu 24.04 + glibc embarquee)."""
import os, re, shutil, subprocess, sys, glob, stat

OUT = sys.argv[1]
STAGE = "/root/build/stage"
RT = f"{OUT}/runtime"
LIB = f"{RT}/lib"
SYS = "/usr/lib/x86_64-linux-gnu"

def sh(*a, check=True):
    return subprocess.run(a, check=check, capture_output=True, text=True).stdout

def is_elf(p):
    try:
        with open(p, "rb") as f:
            return f.read(4) == b"\x7fELF"
    except OSError:
        return False

def ldd(p):
    out = subprocess.run(["ldd", p], capture_output=True, text=True).stdout
    res = []
    for line in out.splitlines():
        m = re.match(r"\s*(\S+) => (\S+)", line)
        if m and m.group(2).startswith("/"):
            res.append((m.group(1), m.group(2)))
        m = re.match(r"\s*(/\S*ld-linux\S*)", line)
        if m:
            res.append(("ld-linux-x86-64.so.2", m.group(1)))
    return res

os.makedirs(f"{LIB}/dri", exist_ok=True)
os.makedirs(f"{LIB}/gbm", exist_ok=True)
os.makedirs(f"{RT}/bin", exist_ok=True)

# --- applications
for d in ("blender", "godot", "aseprite"):
    src = f"{STAGE}/{d}"
    if os.path.isdir(src) and not os.path.exists(f"{OUT}/{d}"):
        shutil.copytree(src, f"{OUT}/{d}", symlinks=True)

# --- programmes du runtime
for b in ("Xvfb", "xkbcomp", "patchelf", "glxinfo", "eglinfo", "xdpyinfo", "xwd"):
    p = shutil.which(b)
    if p:
        shutil.copy2(p, f"{RT}/bin/{b}")

# Xvfb : le dossier de xkbcomp est code en dur (/usr/bin) -> "." (le lanceur fait cd runtime/bin)
xv = f"{RT}/bin/Xvfb"
data = open(xv, "rb").read()
assert data.count(b"/usr/bin\x00") == 1
data = data.replace(b"/usr/bin\x00", b".\x00\x00\x00\x00\x00\x00\x00\x00")
open(xv, "wb").write(data)

# --- mesa (llvmpipe / lavapipe)
for f in glob.glob(f"{SYS}/libgallium-*.so"):
    shutil.copy2(f, LIB)
shutil.copy2(f"{SYS}/dri/libdril_dri.so", f"{LIB}/dri/")
for n in ("swrast_dri.so", "kms_swrast_dri.so"):
    os.symlink("libdril_dri.so", f"{LIB}/dri/{n}")
shutil.copy2(f"{SYS}/gbm/dri_gbm.so", f"{LIB}/gbm/")

# bibliotheques chargees par dlopen (Godot, Blender, Aseprite, glvnd, vulkan)
DLOPEN = """libX11.so.6 libX11-xcb.so.1 libXcursor.so.1 libXinerama.so.1 libXext.so.6 libXrandr.so.2
libXrender.so.1 libXi.so.6 libXfixes.so.3 libXxf86vm.so.1 libSM.so.6 libICE.so.6 libxcb.so.1
libxkbcommon.so.0 libxkbcommon-x11.so.0 libwayland-client.so.0 libwayland-cursor.so.0
libwayland-egl.so.1 libdecor-0.so.0 libdbus-1.so.3 libasound.so.2 libpulse.so.0 libudev.so.1
libvulkan.so.1 libvulkan_lvp.so libGL.so.1 libGLX.so.0 libGLdispatch.so.0 libOpenGL.so.0
libEGL.so.1 libGLESv2.so.2 libGLX_mesa.so.0 libEGL_mesa.so.0 libgbm.so.1 libfontconfig.so.1
libfreetype.so.6 libz.so.1 libstdc++.so.6 libgcc_s.so.1 libc.so.6 libm.so.6 libpthread.so.0
libdl.so.2 librt.so.1 libutil.so.1 libresolv.so.2 libanl.so.1 libuuid.so.1 libexpat.so.1
libnss_dns.so.2 libnss_files.so.2 libcrypt.so.1 libbsd.so.0 libmd.so.0 libXau.so.6 libXdmcp.so.6
libxcb-glx.so.0 libxcb-dri2.so.0 libxcb-dri3.so.0 libxcb-present.so.0 libxcb-sync.so.1
libxcb-xfixes.so.0 libxcb-randr.so.0 libxcb-shm.so.0 libxshmfence.so.1 libdrm.so.2 libX11-xcb.so.1
libxcb-xkb.so.1 libssl.so.3 libcrypto.so.3 libffi.so.8 liblzma.so.5 libbz2.so.1.0""".split()

seeds = []
for n in DLOPEN:
    p = f"{SYS}/{n}"
    if os.path.exists(p):
        seeds.append(p)
    else:
        print("absent (ignore):", n)
for root in (RT, OUT + "/godot", OUT + "/aseprite", OUT + "/blender"):
    for dp, dn, fn in os.walk(root):
        if "export_templates" in dp:
            continue
        for f in fn:
            p = os.path.join(dp, f)
            if not os.path.islink(p) and is_elf(p):
                seeds.append(p)

wanted = {}
todo = list(seeds)
seen = set()
while todo:
    p = todo.pop()
    if p in seen:
        continue
    seen.add(p)
    if p.startswith(("/usr/lib", "/lib")):
        wanted[os.path.basename(p)] = p
    for soname, path in ldd(p):
        if path.startswith(OUT):
            continue
        if path.startswith(("/usr/lib", "/lib")):
            wanted[soname] = os.path.realpath(path)
            if os.path.realpath(path) not in seen:
                todo.append(os.path.realpath(path))

for soname, real in sorted(wanted.items()):
    dst = f"{LIB}/{soname}"
    if not os.path.exists(dst):
        shutil.copy2(real, dst)
        os.chmod(dst, 0o755)
print(len(wanted), "bibliotheques copiees")

# --- donnees
shutil.copytree("/usr/share/X11/locale", f"{RT}/share/X11/locale", symlinks=True, dirs_exist_ok=True)
shutil.copytree("/usr/share/X11/xkb", f"{RT}/share/X11/xkb", symlinks=False, dirs_exist_ok=True)
os.makedirs(f"{RT}/share/glvnd/egl_vendor.d", exist_ok=True)
shutil.copy2("/usr/share/glvnd/egl_vendor.d/50_mesa.json", f"{RT}/share/glvnd/egl_vendor.d/")
os.makedirs(f"{RT}/share/vulkan/icd.d", exist_ok=True)
shutil.copy2("/usr/share/vulkan/icd.d/lvp_icd.json", f"{RT}/share/vulkan/icd.d/")
os.makedirs(f"{RT}/share/fonts", exist_ok=True)
for f in glob.glob("/usr/share/fonts/truetype/dejavu/*.ttf"):
    shutil.copy2(f, f"{RT}/share/fonts/")
os.makedirs(f"{RT}/etc/fonts", exist_ok=True)
open(f"{RT}/etc/fonts/fonts.conf", "w").write("""<?xml version="1.0"?>
<!DOCTYPE fontconfig SYSTEM "fonts.dtd">
<fontconfig>
  <dir prefix="relative">../../share/fonts</dir>
  <dir>/usr/share/fonts</dir>
  <cachedir prefix="xdg">fontconfig</cachedir>
</fontconfig>
""")

# --- RUNPATH relatifs ($ORIGIN) sur tous les ELF
def runpath_for(p):
    rel = os.path.relpath(LIB, os.path.dirname(p))
    extra = ""
    if p == f"{OUT}/blender/blender" or os.path.dirname(p) == f"{OUT}/blender":
        extra = "$ORIGIN/lib:"
    return extra + "$ORIGIN" + ("" if rel == "." else "/" + rel)

n = 0
for dp, dn, fn in os.walk(OUT):
    if "export_templates" in dp:
        continue
    for f in fn:
        p = os.path.join(dp, f)
        if os.path.islink(p) or not is_elf(p):
            continue
        if os.path.basename(p).startswith("ld-linux"):
            continue
        cur = subprocess.run(["patchelf", "--print-rpath", p], capture_output=True, text=True)
        if cur.returncode != 0:
            continue
        old = [x for x in cur.stdout.strip().split(":") if x]
        new = runpath_for(p)
        rp = ":".join(old + [x for x in new.split(":") if x not in old])
        r = subprocess.run(["patchelf", "--set-rpath", rp, "--force-rpath", p] if False else
                           ["patchelf", "--set-rpath", rp, p], capture_output=True, text=True)
        if r.returncode == 0:
            n += 1
        else:
            print("rpath KO", p, r.stderr.strip()[:120])
print(n, "RUNPATH poses")
