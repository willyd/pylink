
import os
import sys
if sys.platform == 'win32':
    import win32file
from os import path as osp

import click

import uac

def _check_not_exist(link):
    if osp.exists(link):
        raise IOError('Cannot create an already existing link. Link: {}'.format(link))
        
def _check_exist(target, msg=None):
    if not osp.exists(target):
        if msg is None:
            msg = 'Cannot create a link to a non existing target. Target: {}'.format(target)
        raise IOError(msg)
        
def _remove_trailing_seprator(path):
    while path.endswith(osp.sep):
        path = path[:-1]                
    return path
    
def create_hardlink(target, link):
    _check_exist(target)
    _check_not_exist(link)
    target = _remove_trailing_seprator(target)
    link = _remove_trailing_seprator(link)
    if osp.isdir(target):
        # TODO create junction
        # see http://www.flexhex.com/docs/articles/hard-links.phtml
        pass
    else:
        win32file.CreateHardLink(link, target, None)
        
def create_symlink(target, link):
    if sys.platform != 'win32':
        os.symlink(target, link)
    else:
        _check_exist(target)
        _check_not_exist(link)
        target = _remove_trailing_seprator(target)
        link = _remove_trailing_seprator(link)
        if uac.is_user_admin():
            if osp.isdir(target):
                flags = win32file.SYMBOLIC_LINK_FLAG_DIRECTORY
            else:
                flags = 0
            win32file.CreateSymbolicLink(link, target, flags, None)
        else:
            # requestion elevation
            ret = uac.run_as_admin([sys.executable, __file__, '-s', target, link])
            if not osp.exists(link):
                raise IOError('Failed to create symlink. Link {}'.format(link))
        
def delete_symlink(link):            
    if sys.platform != 'win32':
        os.unlink(link)
    else:
        link = _remove_trailing_seprator(link)
        _check_exist(link,
                    msg='Cannot delete a non existing link. Link: {}'.format(link))
        if osp.isdir(link):
            win32file.RemoveDirectory(link, None)
        else:
            win32file.DeleteFile(link)
        
def create_link(target, link):
    _check_exist(target)
    _check_not_exist(link)
    if osp.isdir(target):
        # use symbolic link for directories for now
        create_symlink(target, link)
    else:
       create_hardlink(target, link)    
        
@click.command()
@click.argument('target')
@click.argument('link')
@click.option('-s', is_flag=True, default=False)
def link_cli(target, link, s):    
    if s:        
        create_symlink(target, link)
    else:
        create_hardlink(target, link)
    print('Link created: {} -> {}'.format(link, target))
            
if __name__ == '__main__':
    link_cli()
        
        
                    