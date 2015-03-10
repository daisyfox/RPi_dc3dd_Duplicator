import os

def copyrecursively(src_hdr, cpy_fldr, dest_fldr_list):
    src_fldr = os.path.join(src_hdr, cpy_fldr)
    err = 0
    for root, dirs, files in os.walk(src_hdr):
        for src_d in dirs:
            src_d_full = os.path.join(root, src_d)
            if len(src_d_full) >= len(src_fldr) and src_d_full.find(src_fldr) >= 0: # ie found a cpy_fldr & its subfolders
                for dest_fldr in dest_fldr_list:
                    dest_path = os.path.join(dest_fldr +'/', src_d_full.replace(src_hdr, ""))
                    if not os.path.exists(dest_path):
                        os.mkdir(dest_path)

        for item in files:
            if root.find(src_fldr) >= 0:
                if item.find(" ") >= 0:
                    item_cln = item.replace(" ", "_")
                    os.rename(os.path.join(root, item), os.path.join(root, item_cln))
                else:
                    item_cln = item
                src_file = os.path.join(root, item_cln)
                cmdText = "dc3dd if=" + src_file
                for dest_fldr in dest_fldr_list:
                    dest_file = os.path.join(dest_fldr, src_file.replace(src_hdr, ""))
                    cmdText = cmdText + " of=" + dest_file

                rtn_val = os.system(cmdText)
                if rtn_val == 0:
                    print(src_file + "  --Ok--  ")
                else:
                    print(src_file + "  --Error--  ")
                    err += 1

    print("\n\n  FILE COPY COMPLETE with " + str(err) + " errors")


##  MAIN  ##
#source_header = "/media/JUKEBOX_C/"
#folder_to_copy = "blah"
source_header = "/media/JUKEBOX_C/"
folder_to_copy = "ALL"
destination_folders = ["/media/JUKEBOX_A", "/media/JUKEBOX_B"]

copyrecursively(source_header, folder_to_copy, destination_folders)

