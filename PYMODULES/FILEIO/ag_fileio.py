#!/usr/bin/env python

import pdb
import os
import sys
from natsort import natsorted
from pathlib import Path


class FileHandler(object):
    """
    Find files, link them, etc.
    """

    def __init__(self):
        self.files = []

    def find_files(self, path, name_pattern):
        """
        Find files in folders by their ending.

        Paramters
        ---------
        path : str
            name of directory where to find the files in

        name_pattern : str
            name of file ending with '*', e.g. ".pwscf_out"

        Sources
        -------
        https://docs.python.org/2/library/fnmatch.html#fnmatch.filter

        """
        for filename in Path(path).glob("**/*{}".format(name_pattern)):
            self.files.append(filename)

    def files_to_strings(self):
        """
        Convert PosixPath to str.
        """
        str_filenames = []

        for filename in self.files:
            full_path = filename.resolve()
            str_filename = full_path.as_posix()
            str_filenames.append(str_filename)

        self.files = str_filenames

    def link_files(self, directory):
        """Link files to the directory.

        Parameters
        ----------
        directory : str
            name of directory to link to

        """
        for filename in self.files:
            symlink = Path(directory + filename.name)

            try:
                symlink.symlink_to(filename.resolve())
            except OSError:
                pass

    def sort_files(self):
        self.files = natsorted(self.files)


def files_to_xyz(path, file_extension, settings=None, xyz_out="DEFAULT.xyz", xyz_settings=None):
    """Find and read gaussian or pw files from a given path.

    Read gaussian in- and output files and pw in- and output files.
    The files may be in subfolders of 'path'; 'settings' may be omitted, if
    the files shall be read using the standard settings. If non-standard
    settings should be used, read the documentation of the according functions.

    Parameters
    ----------
    path : {str}
        Path to files (may be in subfolders).

    file_extension : {str}
        Extension of file. Currently only '.gau', '.gau.out', '.pwscf_in',
        '.pwscf_out' supported.

    settings : {dict}, optional
        Settings for each file extension when read
        (the default is None, which all arguments are set to False).

    xyz_out : {str}
        Name of output file.

    xyz_settings : {dict}
        Settings that will be used when writing an xyz file.
        The dicitonary may look like this:
        {
        'frame_ids': [int, int, ...],
        'title': "DEFAULT",
        'guess_element': False
        }

    """
    import ag_unify_md as agum

    def read_files():
        for file in flhn.files:
            mdsys_tmp = agum.Unification()

            if file.endswith(".gau"):

                if settings is None:
                    mdsys_tmp.read_gau(file)
                else:
                    mdsys_tmp.read_gau(file, **settings)

            elif file.endswith(".gau.out"):

                if settings is None:
                    mdsys_tmp.read_gau_log(file)
                else:
                    mdsys_tmp.read_gau_log(file, **settings)

            elif file.endswith(".pwscf_in"):
                mdsys_tmp.read_pwin(file)
            elif file.endswith(".pwscf_out"):

                if settings is None:
                    mdsys_tmp.read_pwout(file)
                else:
                    mdsys_tmp.read_pwout(file, **settings)
            else:
                print("Unkown type of file  {},\n skipping.".format(file.endswith()))

    flhn = FileHandler()
    flhn.find_files(path, file_extension)
    flhn.files_to_strings()
    flhn.sort_files()
    mdsys = agum.Unification()
    read_files()
    nframes = range(len(mdsys.ts_coords))
    pdb.set_trace()

    # write the xyz-file
    if xyz_settings is None:
        mdsys.write_xyz(xyz_out, *nframes)
    else:
        mdsys.write_xyz(xyz_out, *nframes, **xyz_settings)

    return md_sys
