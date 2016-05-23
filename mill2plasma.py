#!/usr/bin/python
"USAGE: pycamOpti.py <file>"

import sys,getopt

file_in_name      = ''

G_modal           = 0
G_dest            = 0
X_dest            = 0
Y_dest            = 0
Z_dest            = 1
M_dest            = 0
T_dest            = 0

G_modal_codes     = [0,1,81]
G_codes_probing   = [1,81]

class Coordinate():
    def __init__(self,X,Y,Z):
        self.X = X
        self.Y = Y
        self.Z = Z

class MillTrajectory():
    def __init__(self, first):
        self.first = first
        self.last  = first
        self.lines = []
        self.post  = []

    def connects(self, next):
        if self.last.X == next.first.X and self.last.Y == next.first.Y:
            if self.last.Z != next.first.Z:
                return 1
            else:
                return 2    
        return 0

def get_num(line,char_ptr,num_chars):
    char_ptr=char_ptr+1
    numstr = ''
    good   = '-.0123456789'
    while char_ptr < num_chars:
        digit = line[char_ptr]
        if good.find(digit) != -1:
            numstr = numstr + digit
            char_ptr = char_ptr + 1
        elif numstr == '' and digit ==' ':
            char_ptr = char_ptr + 1
        else: break
    return numstr

if __name__=='__main__':
    if len(sys.argv) < 2:            
        print __doc__
    else:
        cut_height     = 3
        pierce_height  = 0
        pierce_delay   = 2

        file_in_name   = sys.argv[1]
        opts, args = getopt.getopt(sys.argv[2:],"c:p:d:",["cut_height=","pierce_height=","pierce_delay="])

        for opt, arg in opts:
            if opt in ('-c','--cut_height'):
                cut_height = float(arg) 
            if opt in ('-p','--pierce_height'):
                pierce_height  = float(arg)
            elif opt in ('-d','--pierce_delay'):
                pierce_delay = float(arg)
        if pierce_height == 0:
            pierce_height = cut_height*2

        file_in        = []
        file_out       = []
        intro          = []
        trajectories   = []
        numstr         = ''
        char           = ''
        in_trajectory = False

        f = open(file_in_name, 'r')
        for line in f:
            file_in.append(line)
        f.close()

        # parse each line
        line_ptr=0
        num_lines=len(file_in)
        while line_ptr < num_lines:
            line = file_in[line_ptr]
            X_start = X_dest
            Y_start = Y_dest
            Z_start = Z_dest
        
            # parse each character
            char_ptr = 0
            num_chars= len(line)
            coord_count = 0
            G_found     = False
            while char_ptr < num_chars:
                char = line[char_ptr]      
                if '('.find(char) != -1:
                    break
                elif ';'.find(char) != -1:
                    line = line.replace(';','(',1).replace('\n',')\n',1)
                    break
                elif char == 'G' :
                    G_dest = int(get_num(line,char_ptr,num_chars))
                    coord_count = coord_count+1
                    G_found = True
                elif char == 'X' :
                    X_dest = float(get_num(line,char_ptr,num_chars))
                    coord_count = coord_count+1
                elif char == 'Y' :
                    Y_dest = float(get_num(line,char_ptr,num_chars))
                    coord_count = coord_count + 1
                elif char == 'Z' :
                    Z_dest = float(get_num(line,char_ptr,num_chars))
                    coord_count = coord_count + 1
                elif char == 'R' :
                    R_dest = float(get_num(line,char_ptr,num_chars))
                elif char == 'F' :
                    F_dest = float(get_num(line,char_ptr,num_chars))
                elif char == 'M' :
                    M_dest = float(get_num(line,char_ptr,num_chars))
                elif char == 'T' :
                    T_dest = float(get_num(line,char_ptr,num_chars))

                char_ptr = char_ptr + 1

            if G_found:
                if G_dest in G_modal_codes:
                    G_modal = G_dest
            else:
                if coord_count > 0:
                    G_dest = G_modal

            if M_dest == 6 or M_dest == 8 or M_dest == 5:
                line = ''
                M_dest = -1

            if G_dest == 1 and Z_dest < Z_start:
                in_trajectory = True
                coord = Coordinate(X_dest,Y_dest,Z_dest)
                newTray = MillTrajectory(coord)
                newTray.lines.append("(Iniciando nueva trayectoria en: "+ str(X_dest)+","+str(Y_dest)+","+str(Z_dest) +")\n")
                newTray.lines.append("(Plasma probing + pearcing)\n")
                newTray.lines.append("F100\nG38.2 Z-10 (Probe to find the surface)\nF10\nG38.5 (Touch off)\nG92 Z0 (Set Z0)\n")
#G91G21; G38.2Z-30F100; G0Z1; G38.2Z-1F10
                newTray.lines.append("F%d\nG1 Z%.2f (Go to piercing height)\nM3 S10000\nG4 P1 (Wait for torch on)\n;M66 P0 L1 Q5 (TODO: Wait for Arc OK from Torch)\nG4 P%.2f\n" % (F_dest,pierce_height,pierce_delay))
                newTray.lines.append("G1 Z%.2f (Go to cut height)\n" % (cut_height))
                newTray.lines.append("(Start cut)\n")
#                newTray.lines.append(line)
                trajectories.append(newTray)
                G_dest = -1
                line_ptr=line_ptr+1
                continue

            if in_trajectory:
#TODO: mejorar logica de deteccion de ultimo punto de trayectoria
                if Z_dest > Z_start:
                    trajectories[-1].last = Coordinate(X_start,Y_start,Z_start)
                    trajectories[-1].lines.append("(Terminando trayectoria en:"+ str(X_start)+","+str(Y_start)+","+str(Z_start) +")\n")
                    trajectories[-1].lines.append("(End cut)\nM5 ;torch off\nG92.1 ;Clear offsets\n")
                    in_trajectory = False
                    trajectories[-1].post.append(line)
                else:
                    trajectories[-1].lines.append(line)
                G_dest = -1
            else:
                if trajectories != []:
                    trajectories[-1].post.append(line)
                else:
                    file_out.append(line)

            line_ptr=line_ptr+1

        #Ordenar trayectorias
        for i in xrange(0,len(trajectories)-1):
            for j in xrange(i+1,len(trajectories)):
                match = trajectories[i].connects(trajectories[j])
                #TODO: cambiar por case
                if match:
                    print i, ",", j
                    trajectories[i].post=[]
                    trajectories.insert(i+1, trajectories.pop(j))
                    if match == 1:
                        print "Wrong input file\nEnsure to configure your tool for just one pass in dxf2gcode\n"
                        exit()
#                    else:
#                    trajectories[i].post.append()
                    break

        for trajectory in trajectories:
            for line in trajectory.lines:
              file_out.append(line)
            for line in trajectory.post:
              file_out.append(line)

        # OK now output the G code intro
        # (define the variables, set up the probe subroutine, the etch subroutine and the code to probe the grid)
        from time import localtime, strftime
        line = "(mill2plasma:) \n"
        intro.append(line)
        line = "(Imported from:  " + file_in_name + " at " + strftime("%I:%M %p on %d %b %Y", localtime())+ ")\n"
        intro.append(line)

        # Finally, create and then save the output file
        file_out = intro + file_out

        file_name_suffix = "_plasma.ngc"
        n = file_in_name.rfind(".")
        if n != -1:
            file_out_name = file_in_name[0:n] + file_name_suffix
        else: file_out_name = file_in_name + file_name_suffix

        f = open(file_out_name, 'w')
        for line in file_out:
            f.write(line)
        f.close()

