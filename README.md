# CryoEM_Scripts
A collection of crude scripts and workarounds for CryoEM

`plotfsc.py` Generates FSC plots in EPS format from the RELION XML files. 
<pre>python plotfsc.py --i input.xml --o output.eps </pre>


`rename_image_shift.py` will rename movies based on the image shift position from SerialEM mdoc files. Do this when you collect data with SerialEM multishot and forget to check the box to save files with the position in the name.

The safest way to run this is to make a new directory and symlink all the movies and corresponding mdoc files. <pre>python rename_image_shift.py</pre>


`rsync.py` will rsync with -aP options on a loop and can be stopped remotely by adding a file to the destination directory called "stop". The script
assumes you you have ssh keys set up for access without a password.
<pre>python rsync.py --u username --i 123.123.123.123 --p /full/path/to/data/directory/ --d /full/path/to/destination/directory/ </pre>

To kill the script from the remote machine
<pre>touch /full/path/to/destination/directory/stop </pre>


`splitimageshift.py` writes out a star file for 9 imageshift groups by searching the rlnMicrographName column for a list of strings. Edit the list in the script to accommodate different image shift patterns
<pre>python splitimageshift.py --i particles.star </pre>


`star_editor.py` Can remove UID's,search and replace in text file, or change all values for a rlnName column in a GUI with a live display of the open file. Requires python3 with tkinter.
<pre>python star_editor.py</pre>

`star_editor_experimental.py` has added functionality for manually editing, modifying column values, and selectin subsets. Please report any bugs or unexpected results. When the function box is checked, provide a function as the new column value where the current column value is represented by x. For example (x+1)/2
