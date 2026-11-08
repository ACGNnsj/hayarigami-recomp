import texture2ddecoder as t
d=bytes(1920*1080)  # all-zero bc7 blocks
img=t.decode_bc7(d,1920,1080)
print('len',len(img))
