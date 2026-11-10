from PIL import Image
p = 'D:/consoles/ns/hayarigami-recomp/build/v0/menudump/pass_0000_t0_1920x1080_64_rgb10a2.png'
im = Image.open(p).convert('RGB')
print(im.size)
# panel 0 full cell + logo zone
im.crop((0, 660, 800, 1080)).resize((1600, 840)).save('D:/consoles/ns/hayarigami-recomp/build/v0/menudump/crop_panels.png')
im.crop((900, 380, 1600, 780)).resize((1400, 800)).save('D:/consoles/ns/hayarigami-recomp/build/v0/menudump/crop_logo.png')
print('saved')