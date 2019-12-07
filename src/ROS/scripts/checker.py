
f = open("checkerOutput.txt",  "w+")
for j in range(0, 49):
    for i in range(0, 19):
        x = j*0.04
        y = i*0.04
        f.write("<link name='chassis'>\n<pose>" + str(x) + " " + str(y) +" 0 0 0 0</pose>\n<visual name='visual'>\n<geometry>\n<box>\n<size>.02 .02 .0005</size>\n</box>\n</geometry>\n</visual>\n</link>\n")
