# This file is part of pyrasite.
#
# pyrasite is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# pyrasite is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with pyrasite.  If not, see <http://www.gnu.org/licenses/>.
#
# Copyright (C) 2011-2013 Red Hat, Inc., Luke Macken <lmacken@redhat.com>

import os
import platform
import subprocess


def inject(pid, filename, verbose=False, gdb_prefix=''):
    """Executes a file in a running Python process."""
    filename = os.path.abspath(filename)
    gdb_cmds = [
        'set trace-commands on',
        'set logging on',
        'set scheduler-locking off',
        'call ((int (*)())PyPyGILState_Ensure)()',
        'call ((int (*)(const char *))PyPyRun_SimpleString)("'
            'import sys; sys.path.insert(0, \\"%s\\"); '
            'sys.path.insert(0, \\"%s\\"); '
            'exec(open(\\"%s\\").read())")' %
                (os.path.dirname(filename),
                os.path.abspath(os.path.join(os.path.dirname(__file__), '..')),
                filename),
        'call ((void (*) (int) )PyPyGILState_Release)($1)',
        ]
    gdb_cmds_filename = '/tmp/pyrasite-gdb-commands'
    with open(gdb_cmds_filename, 'w') as f:
        f.write('\n'.join(gdb_cmds))

    cmd = '%sgdb -p %d --batch --command=%s' % (gdb_prefix, pid, gdb_cmds_filename)
    if verbose:
        print('running gdb with cmd ' + cmd)
    
    p = subprocess.Popen(cmd,
        shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    out, err = p.communicate()
    if verbose:
        print("====== gdb stdout: ======")
        print(out.decode("u8"))
        print("====== gdb stderr: ======")
        print(err.decode("u8"))
        print("======")

if platform.system() == 'Windows':
    def inject_win(pid, filename, verbose=False, gdb_prefix=''):
        if gdb_prefix == '':
            gdb_prefix = os.path.join(os.path.dirname(__file__), 'win') + os.sep
        filename = os.path.abspath(filename)
        code = 'import sys; sys.path.insert(0, \\"%s\\"); sys.path.insert(0, \\"%s\\"); exec(open(\\"%s\\").read())' % (os.path.dirname(filename).replace('\\', '/'), os.path.abspath(os.path.join(os.path.dirname(__file__), '..')).replace('\\', '/'), filename.replace('\\', '/'))
        p = subprocess.Popen('%sinject_python_32.exe %d \"%s\"' % (gdb_prefix, pid, code), shell = True, stdout = subprocess.PIPE, stderr = subprocess.PIPE)
        out, err = p.communicate()
        if p.wait() == 25:
            p = subprocess.Popen('%sinject_python_64.exe %d \"%s\"' % (gdb_prefix, pid, code), shell = True, stdout = subprocess.PIPE, stderr = subprocess.PIPE)
            out, err = p.communicate()
        if verbose:
            print(out)
            print(err)

    inject = inject_win
