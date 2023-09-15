# CryoEM_Scripts
A collection of crude scripts and workarounds for CryoEM

`rename_image_shift.py` will rename movies based on the image shift position from SerialEM mdoc files. Do this when you collect data with SerialEM multishot and forget to check the box to save files with the position in the name.

The safest way to run this is to make a new directory and symlink all the movies and corresponding mdoc files. <pre>python rename_image_shift.py</pre>


`rsync.py` will rsync with -aP options on a loop and can be stopped remotely by adding a file to the destination directory called "stop". The script
assumes you you have ssh keys set up for access without a password.
<pre>python rsync.py --u username --i 123.123.123.123 --p /full/path/to/data/directory/ --d /full/path/to/destination/directory/ </pre>

To kill the script from the remote machine
<pre>touch /full/path/to/destination/directory/stop </pre>


`replacepaths.py` compares two star files  A and B and replaces the paths for rlnImageName and rlnMicrographName in A from B based on matching X and Y coordinates. Requires the starfile module from alisterburt. This is useful for removing the unnecessary numbers added to the paths by cryosparc v3.3 when working from relion to cryosparc then back to relion.
<pre>python replacepaths.py --i particles.star --p particles_with_correct_paths.star --o output.star </pre>

`repairpaths.py` can remove UIDs with with search and replace or the same functionality as `replacepaths.py`
<pre>python repairpaths.py --i particles.star --o output.star --nouid </pre>

`splitimageshift.py` writes out a star file for 9 imageshift groups by searching the rlnMicrographName column for a list of strings. Edit the list in the script to accommodate different image shift patterns
<pre>python splitimageshift.py --i particles.star </pre>

`contactmap_it.py` will calculate the number of contacts <12Å between two protein chains for each pdb file in the directory where it's run and write out a text file with the scores. This is a work in progress.

`searchandreplace.py` will prompt the user for a file name and text strings for search and replace. Leave the replacement text blank and you will be asked if you want to delete the string or line containing the string. The result is written out as a new file with _mod appended to the name.

`star_editor.py` Can remove UID's,search and replace in text file, or change all values for a rlnName column in a GUI with a live display of the open file. Requires python3 with tkinter.
<pre>python star_editor.py</pre>

`plotfsc.py` Generates FSC plots in EPS format from the RELION XML files. 
<pre>python plotfsc.py --i input.xml --o output.eps </pre>

