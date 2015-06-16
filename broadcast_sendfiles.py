import sys
import pexpect
from Utils import make_mission_file

nArgs = len(sys.argv)-1
if nArgs != 1:
    print "enter parameters : jogNumber"
else:
    files_paths = file("broadcast_sendfiles", 'r').readlines()
    ids = [int(_) for _ in file("broacast_init_config", 'r').readline().split() if _.isdigit()]
    config_file_data = file("jogs.conf", 'r').readlines()  # TODO : fichier jogs.conf

    for stnum in ids:
        ipaddr = "172.20.25.%s" % stnum
        passwd = "root%s" % stnum
        make_mission_file(config_file_data[stnum])
        for file_path in files_paths:
            file_path_sep = file_path.split()
            src = file_path
            dest = "/root/Interceptor"
            if len(file_path_sep) > 1:
                dest = "/".join(["/root/Interceptor", file_path_sep[0:-1:1]])

            cmd = "scp %s root@%s:%s/" % (src, ipaddr, dest)
            child1 = pexpect.spawn(cmd)
            # child1.expect(["password:","pass","word:",":","Password:",pexpect.EOF, pexpect.TIMEOUT])
            child1.expect("password:")  # TODO : May fail here
            # child1.expect(pexpect.EOF)
            child1.sendline(passwd+'\r')  # \r seems not to work without CR
            child1.expect(pexpect.EOF)
            print "jog%s OK" % stnum