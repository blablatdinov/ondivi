import subprocess


def test():
    ps = subprocess.Popen(('echo', 'hello'), stdout=subprocess.PIPE)
    got = subprocess.check_output(('poetry', 'run', 'ondivi'), stdin=ps.stdout).decode().strip()
    ps.wait()

    assert got == 'hello'
