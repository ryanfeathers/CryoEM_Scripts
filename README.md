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

`rln31downgrade.py` Converts RELION 3.1+ star files for compatibility with Warp/M. See https://www.jiscmail.ac.uk/cgi-bin/webadmin?A2=ind1910&L=CCPEM&P=R321009 for more info.
<pre>python rln31downgrade.py --i particles.star </pre>



## Notes on `star_editor.py`

`star_editor.py` Provides a GUI with a live display for making common modifications to cryo-EM star files such as editing paths, modifying data values, etc. Requires python3 with tkinter. Compatible with X11 forwarding. 
<pre>python star_editor.py</pre>

![image](https://github.com/user-attachments/assets/d9d71ced-1aa3-4bad-b52d-047343b6d32c)

Relion 3.1 format star files should be used, as Relion 3.0 format is not fully supported. Most operations require a selection of the particles table or optics table from the drop-down menu.

### Delete Particles Containing Search Criteria
- Provide a string in the search box and click **Remove Particles**. 
- Wildcards can also be used with caution.
- Search can be limited to a specific column by providing the name in the **Column Name** box.

### Search and Replace Strings
- Provide the search and replace strings in the text box and click the **Search and Replace** button.
- Search and replace can be limited to a specific column by providing a **Column Name**.
- Use wildcards with caution. 
  - If no column name is specified and `*` is used, you may delete more than intended.

### Copy Values from One Column to Another or to a New Column
- Provide the column name to operate on in the specified box and the new value or a column name to copy from in the **New Value** entry.
- If the column specified in **Column Name** does not already exist, it will be created.

### Add a New Column and Fill it with a Specific Value
- Provide a column name that doesn't already exist in the table along with a new value.

### Operate on the Values in a Column
- Provide a function rather than a single value and check the **Function** box.

**Example:**  
If `rlnCoordinateX` needs to be binned by 2, provide the column name and `x/2` in the **New Value** entry. Then, check the **Function** box and click **Update Column Values**.

### Remove UID
- Searches the entire particle entry for 21 consecutive numbers and removes them.

### Split by Column
- Splits a star file into multiple star files based on the shared criteria provided in the **Split Column Name**.
- Checking the **Regroup** box will update the `rlnGroupName` column to have consecutive numbering based on the grouping.
- Checking the **Recombine** box will change the `rlnGroupName` and recombine into a single star file.  
  - **Note:** This functionality may be broken.
