# From Marianna's chat message
chars="""
Ĩ
ĩ
Ƙ
Ơ
ơ
Ư
ư
Ƴ
ƴ
ɓ
ɗ
ʻ
ʼ
Ỉ
ỉ
Ị
ị
Ớ
ớ
Ờ
ờ
Ở
ở
Ỡ
ỡ
Ợ
ợ
Ứ
ứ
Ừ
ừ
Ử
ử
Ữ
ữ
Ự
ự
ỵ
Ĩ
ĩ
Ɓ
Ɗ
Ə
ə
ʻ
ʼ
Ỉ
ỉ
Ị
ị
Ấ
ấ
Ầ
ầ
Ẩ
ẩ
Ẫ
ẫ
Ắ
ắ
Ằ
ằ
Ẳ
ẳ
Ẵ
ẵ
Ế
ế
Ề
ề
Ể
ể
Ễ
ễ
"""
code_point_to_name = {}
for g in Glyphs.font.glyphs:
	for u in g.unicodes or []:
		code_point_to_name[int(u,16)]=g.name
print(code_point_to_name)
for c in chars.splitlines():
	if not c: continue
	code_point = ord(c[0])
	print(code_point_to_name[code_point])
	
##############
left = "commaturnedmod"  
right = "imacron"
left_g = Glyphs.font[left]
right_g = Glyphs.font[right]

master_values = []
for master in list(Glyphs.font.masters):
    master_values.append([master.id, Glyphs.font.kerningForPair(master.id, "@MMK_L_"+left_g.rightKerningGroup, "@MMK_R_"+right_g.leftKerningGroup) or "None"])
print(Glyphs.font.filepath)
print("\n".join(f"{m} {v}" for m,v in sorted(master_values)))


#################
for g in Glyphs.font.glyphs:
	print(f"{g.name}\t{g.leftKerningGroup}\t{g.rightKerningGroup}")