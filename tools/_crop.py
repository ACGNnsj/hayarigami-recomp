from PIL import Image
p='build/v0/menudump/pass_0000_t0_1920x1080_64_rgb10a2.png'
im=Image.open(p).convert('RGB')
im.crop((0,660,1920,1080)).resize((1920,840)).save('build/v0/ghost_opts.png')
im.crop((240,0,1680,800)).save('build/v0/ghost_logo.png')
print('saved')
