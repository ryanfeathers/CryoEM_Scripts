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

