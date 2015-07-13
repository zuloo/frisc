import os
import stat
import pwd
import grp
from datetime import datetime


def sizeof_fmt(num, suffix='B'):
    for unit in ['', 'Ki', 'Mi', 'Gi', 'Ti', 'Pi', 'Ei', 'Zi']:
        if abs(num) < 1024.0:
            return "{:3.1f} {}{}".format(num, unit, suffix)
        num /= 1024.0
    return "{:.1f} %s%s".format(num, 'Yi', suffix)


def parse(path):
    meta_data = {}

    st = os.stat(path)

    meta_data['filesystem_absolute_path'] = os.path.abspath(path)

    meta_data['filesystem_user_id'] = st.st_uid
    meta_data['filesystem_user_name'] = pwd.getpwuid(st.st_uid)[0]
    meta_data['filesystem_group_id'] = st.st_gid
    meta_data['filesystem_group_name'] = grp.getgrgid(st.st_gid)[0]
    meta_data['filesystem_readability'] = []

    if bool(st.st_mode & stat.S_IRUSR):
        meta_data['filesystem_readability'].append("U:{}".format(
            meta_data['filesystem_user_name']))

    if bool(st.st_mode & stat.S_IRGRP):
        meta_data['filesystem_readability'].append("G:{}".format(
            meta_data['filesystem_group_name']))

    if bool(st.st_mode & stat.S_IROTH):
        meta_data['filesystem_readability'].append("O:world")

    meta_data['filesystem_access_mode'] = st.st_mode

    meta_data['filesystem_modification_date'] = datetime.utcfromtimestamp(
        st.st_mtime).strftime('%Y-%m-%dT%H:%M:%SZ')

    meta_data['filesystem_creation_data'] = datetime.utcfromtimestamp(
        st.st_ctime).strftime('%Y-%m-%dT%H:%M:%SZ')

    meta_data['filesystem_size'] = sizeof_fmt(st.st_size)

    return ([], meta_data)
