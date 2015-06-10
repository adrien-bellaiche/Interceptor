import sys
import pexpect
import time

# executing remote command cmd on JOGX (X is jog number)
nArgs = len(sys.argv) - 1
if nArgs != 0:
    print "usage : python broadcast_init_config"
else:
    fCmd = file("broacast_init_config", 'r')
    lines = fCmd.readlines()
    ids = [int(_) for _ in lines[0].split() if _.isdigit()]
    cmdLines = lines
    for stnum in ids:
        ipaddr = "172.20.25.%s" % stnum
        cmd = "ssh root@%s" % ipaddr
        passwd = "root%s" % stnum
        print "Beginning on Jog %s" % stnum
        child = pexpect.spawn(cmd)
        child.expect("password:")  # wait for prompt after last command
        child.sendline(passwd)
        time.sleep(0.1)

        # execute the command via the tty on the remote computer
        for cmdLine in cmdLines:
            child.expect("#")
            child.sendline(cmdLine)
            child.expect("#", timeout=300)
            print child.before

        # close the tty
        child.sendline("exit")
        print "jog %s OK" % stnum