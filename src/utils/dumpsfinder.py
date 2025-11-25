from PIL import Image
import imagehash
import shutil
import cv2
import os
import sys
import csv
import platform
import glob
import time
from skimage.metrics import structural_similarity as compare_ssim
from colorama import init, Fore, Style
init()  # initialize colorama for ANSI color codes in Windows


class DumpsFinder:
    def __init__(self):
        self.required_textures_counter = 0
        self.optional_textures_counter = 0

    def run_dumpsfinder(self, callback, dumps_path, uniform_slot_name, uniform_type, team_glove, second_glove, photoshop_pref, pridesticker_pref, helmetnumbers_pref, ssnumbers_pref, only_make_csv):
        

        # Function to get a formatted checkmark or fallback
        def get_checkmark():
            checkmark = f"✔"
            if platform.system() == 'Windows':
                checkmark = f"+"
            return checkmark

        # Example usage with a green checkmark or fallback to a green plus sign
        checkmark = get_checkmark()

        # Use sys._MEIPASS if running as a PyInstaller executable, otherwise use the script's directory
        if getattr(sys, 'frozen', False):
            script_dir = os.path.dirname(sys.executable)
            # print("Running in Pyinstaller EXE")
        else:
            script_dir = os.path.dirname(os.path.abspath(__file__))
            # print("Running native python")

        # Calculate the parent directory
        parent_dir = os.path.dirname(script_dir)

        # define base directory
        if getattr(sys, 'frozen', False):
            base_dir = script_dir
        else:
            base_dir = parent_dir

        # Read the content of the config file
        config_file_path = os.path.join(base_dir, "utils", 'config-image-matching.txt')
        config_content = {}
        with open(config_file_path) as f:
            exec(f.read(), config_content)

      
        # # Output the passed parameters
        # callback(f"Using dumps path: {dumps_path}\n")
        # callback(f"Uniform Slot Name: {uniform_slot_name}\n")
        # callback(f"Uniform Type: {uniform_type}\n")
        # callback(f"Team Glove: {team_glove}\n")
        # callback(f"Second Glove: {second_glove}\n")
        # callback(f"Photoshop Preference: {photoshop_pref}\n")
        # callback(f"Pride Sticker Preference: {pridesticker_pref}\n")
        # callback(f"Helmet Numbers Preference: {helmetnumbers_pref}\n")
        # callback(f"Sleeve/Shoulder Numbers Preference: {ssnumbers_pref}\n")

        only_make_csv = str(only_make_csv.strip().lower())
        # print(f"Only Make CSV preference: {only_make_csv}\n")
        # print(type(only_make_csv))

        # Define the 'put_textures_here' source folder
        source_folder = os.path.join(base_dir, "YOUR_TEXTURES_HERE")

        # Define the 'renamed' folder
        renamed_folder = os.path.join(base_dir, "RENAMED")

        # Define the 'default textures' folder
        default_textures_folder = os.path.join(base_dir, "utils", "default-textures")

        # Define the CSV input folder
        csv_folder = os.path.join(base_dir, "csv-override")

        callback("\n")  # Add a line break 
        callback("\n")  # Add a line break 
        callback("#####################################################################\n")
        callback("#                                                                   #\n")
        callback("#       NCAA NEXT Uniform Expansion Texture Renaming Utility        #\n")
        callback("#                                                                   #\n")
        callback("#                   Mode 2: Dumps Find & Rename                     #\n")        
        callback("#                                                                   #\n")
        callback("#####################################################################\n")

        # Configuration settings stage...

        callback("\n")  # Add a line break 
        callback("\n")  # Add a line break 
        callback(f"+++++++++++++++++++++++ CONFIGURATION SETTINGS +++++++++++++++++++++++\n", "blue") 
        callback("\n")  # Add a line break 

        # Output the value of dumps_path
        callback(f"\n[•] ", "blue")
        callback(f"DUMPS FOLDER is defined and confirmed to exist at: ==============#\n")
        callback(f"\n|     └-----→  ")
        callback(f"{dumps_path}\n", "green")
        callback(f"\n#ˉˉˉˉˉˉˉˉˉˉˉˉˉˉˉˉˉˉˉˉˉˉˉˉˉˉˉˉˉˉˉˉˉˉˉˉˉˉˉˉˉˉˉˉˉˉˉˉˉˉˉˉˉˉˉˉˉˉˉˉˉˉˉˉˉˉˉˉˉ#")
        callback("\n")  # Add a line break 

        # Check if uniform_slot_name is not defined or the folder does not exist
        if not uniform_slot_name:
            callback("\n")  # Add a line break 
            callback(f"{Fore.YELLOW}[!] The UNIFORM SLOT NAME is not defined.\n")
            callback(f"{Style.RESET_ALL} ")
        # Output the value of uniform_slot_name
        callback(f"\n[•] ", "blue")    
        callback(f"UNIFORM SLOT NAME is defined as: ================================#\n")    
        callback(f"\n|     └-----→  ")
        callback(f"{uniform_slot_name}\n", "green")
        callback(f"\n#ˉˉˉˉˉˉˉˉˉˉˉˉˉˉˉˉˉˉˉˉˉˉˉˉˉˉˉˉˉˉˉˉˉˉˉˉˉˉˉˉˉˉˉˉˉˉˉˉˉˉˉˉˉˉˉˉˉˉˉˉˉˉˉˉˉˉˉˉˉ#")
        callback("\n")  # Add a line break 

        # Check if uniform_type is not defined 
        if not uniform_type:
            # Prompt the user to enter a path
            callback("\n")  # Add a line break 
            callback(f"{Fore.YELLOW}[!] The UNIFORM TYPE is not defined in config.txt.{Style.RESET_ALL}\n")
        # Add a condition to check the uniform type and set the appropriate path
        if uniform_type.lower() == 'dark':
            uniform_type_output = "DARK"
            reference_folder = "reference-dark"
        elif uniform_type.lower() == 'light':
            uniform_type_output = "LIGHT"
            reference_folder = "reference-light"
        else:
            uniform_type_output = "Invalid input. Assuming DARK uniform."
            reference_folder = "reference-dark"
        # Output the value of uniform_type
        callback(f"\n[•] ", "blue")  
        callback(f"UNIFORM TYPE is: =================================================#\n")
        callback(f"\n|     └-----→  ")
        callback(f"{uniform_type_output}\n", "green")
        callback(f"\n#ˉˉˉˉˉˉˉˉˉˉˉˉˉˉˉˉˉˉˉˉˉˉˉˉˉˉˉˉˉˉˉˉˉˉˉˉˉˉˉˉˉˉˉˉˉˉˉˉˉˉˉˉˉˉˉˉˉˉˉˉˉˉˉˉˉˉˉˉˉ#\n")
        # Output the selected default textures folder
        callback(f" └→ The reference folder for the {uniform_type} uniform is set to: {reference_folder}. Feel free to put your actual dumped textures in here (or its alts subfolder) if the image matching utility is having trouble finding a match.\n")
        callback("\n")  # Add a line break 

        # Check if second_glove is not defined 
        if not second_glove:
            callback("\n")  # Add a line break 
            callback(f"{Fore.YELLOW}[!] The GLOVE TYPE is not defined. \n{Style.RESET_ALL}\n")
        # Add a condition to check the uniform type and set the appropriate path
        if second_glove.lower() == 'no':
            second_glove_output = "NORMAL (not the second gloves)"
            reference_glove1 = "glove-uni-1"
            reference_glove2 = "glove-uni-2"
        elif second_glove.lower() == 'yes':
            second_glove_output = "SECOND GLOVES (dark uniform as vistor OR light uniform as home team)"
            reference_glove1 = "glove-uni-1-second"
            reference_glove2 = "glove-uni-2-second"
        else:
            second_glove_output = "Invalid input. Assuming normal gloves."
            reference_glove1 = "glove-uni-1"
            reference_glove2 = "glove-uni-2"
        # Output the value of second_glove
        callback(f"\n[•] ", "blue")  
        callback(f"GLOVE TYPE is: =================================================#\n")
        callback(f"\n|     └-----→  ")
        callback(f"{second_glove_output}\n", "green")
        callback(f"\n#ˉˉˉˉˉˉˉˉˉˉˉˉˉˉˉˉˉˉˉˉˉˉˉˉˉˉˉˉˉˉˉˉˉˉˉˉˉˉˉˉˉˉˉˉˉˉˉˉˉˉˉˉˉˉˉˉˉˉˉˉˉˉˉˉˉˉˉˉˉ#\n")
        # Output the selected default textures folder
        callback(f" └→ The dumps finder will look for a dumped match with {reference_glove1}.png and {reference_glove2}.png in the '{reference_folder}' folder. It will rename your glove of the same name.\n")
        if second_glove.lower() == 'yes':
          callback(f" └→ THESE TWO ARE THE ONLY TEXTURES THAT WILL BE PROCESSED. Change this setting to 'yes' to do the rest of the uniform.\n")
        callback("\n")  # Add a line break 



        # Simplify the glove boolean
        glove_normal_or_csv = second_glove.lower() != 'yes'

        # Simplify the team glove boolean
        include_team_glove = team_glove.lower() == 'yes'

        # General Config Settings for both methods
        if glove_normal_or_csv:

            # Photshop or Photopea (must rename files if photopea)
            if not photoshop_pref:
                callback("\n")  # Add a line break 
                callback(f"{Fore.YELLOW}[!] The PHOTOSHOP/PHOTOPEA preference is not defined. Check config.txt and ensure there is a line that reads: 'photoshop_pref = 1'. \n\n")

            # Choose the appropriate mapping
            if photoshop_pref == '1':
                # Use primary names
                photoshop_pref_output = "PhotoSHOP"
            elif photoshop_pref == '2':
                # Use secondary names
                photoshop_pref_output = "PhotoPEA"
            else:
                callback("Assuming Photoshop naming.\n")

            # Output the value of uniform_type
            callback(f"\n[•] ", "blue") 
            callback(f"TEXTURES WERE MADE/NAMED WITH: ==================================#\n")
            callback(f"\n|     └-----→  ")
            callback(f"{photoshop_pref_output}\n", "green")
            if photoshop_pref == '2':
                callback(f"\n|              ")
                callback(f"The files in YOUR_TEXTURES_HERE will be converted to Photoshop names.\n", "green")
            callback(f"\n#ˉˉˉˉˉˉˉˉˉˉˉˉˉˉˉˉˉˉˉˉˉˉˉˉˉˉˉˉˉˉˉˉˉˉˉˉˉˉˉˉˉˉˉˉˉˉˉˉˉˉˉˉˉˉˉˉˉˉˉˉˉˉˉˉˉˉˉˉˉ#")
            callback("\n")


            # Function to rename files to photoshop naming convention if made with photopea
            def rename_photopea_files(source_folder, texture_name_mapping, texture_name_mapping_old):
                # Check if img1.png exists
                img1_path = os.path.join(source_folder, 'img1.png')
                
                if os.path.exists(img1_path):
                    current_mapping = texture_name_mapping_old
                else:
                    current_mapping = texture_name_mapping
                
                for pattern, new_name in current_mapping.items():
                    # Find files matching the pattern
                    matching_files = glob.glob(os.path.join(source_folder, pattern))
                    
                    # Process each matching file
                    for old_path in matching_files:
                        # Extract filename from old_path
                        old_name = os.path.basename(old_path)
                        new_path = os.path.join(source_folder, new_name)
                        
                        # Check if the file exists before attempting to rename
                        if os.path.exists(old_path):
                            # Rename the file
                            os.rename(old_path, new_path)
                            # callback(f'Renamed {old_name} to {new_name}')
                        else:
                            callback(f"WARNING: File not found - {old_name}\n")

            texture_name_mapping = {
                '*_01.png': '01-TC_Wrist.png',
                '*_03.png': '03-TC_QB_Wrist.png',
                '*_04.png': '04-TC_Thin_Band.png',
                '*_06.png': '06-TC_Face_Protector.png',
                '*_07.png': '07-TC_Med_Band--34_sleeve_top.png',
                '*_10.png': '10-Wt_TC_Pad.png',
                '*_11.png': '11-TC_Half_Sleeve.png',
                '*_13.png': '13-Sock.png',
                '*_14.png': '14-Bk_TC_Pad.png',
                '*_15.png': '15-TC_Long_Sleeve.png',
                '*_16.png': '16-Shoe.png',
                '*_17.png': '17-Shoe_w_White_Tape.png',
                '*_18.png': '18-Facemask_Far.png',
                '*_20.png': '20-Facemask_Near.png',
                '*_22.png': '22-Chinstrap.png',
                '*_23.png': '23-Shoe_w_Black_Tape.png',
                '*_24.png': '24-Shoe_w_TC_Tape.png',
                '*_25.png': '25-TC_Face_Protector_Top.png',
            }
            texture_name_mapping_old = {
                'img1.png': '01-TC_Wrist.png',
                'img3.png': '03-TC_QB_Wrist.png',
                'img4.png': '04-TC_Thin_Band.png',
                'img6.png': '06-TC_Face_Protector.png',
                'img7.png': '07-TC_Med_Band--34_sleeve_top.png',
                'img10.png': '10-Wt_TC_Pad.png',
                'img11.png': '11-TC_Half_Sleeve.png',
                'img13.png': '13-Sock.png',
                'img14.png': '14-Bk_TC_Pad.png',
                'img15.png': '15-TC_Long_Sleeve.png',
                'img16.png': '16-Shoe.png',
                'img17.png': '17-Shoe_w_White_Tape.png',
                'img18.png': '18-Facemask_Far.png',
                'img20.png': '20-Facemask_Near.png',
                'img22.png': '22-Chinstrap.png',
                'img23.png': '23-Shoe_w_Black_Tape.png',
                'img24.png': '24-Shoe_w_TC_Tape.png',
                'img25.png': '25-TC_Face_Protector_Top.png',
            }

            # Functions for other configurations and preferences
            def prompt_user(message):
                callback("\n")  # Add a line break
                callback(f"{Fore.YELLOW}[!] {message}{Style.RESET_ALL}\n")
                user_input = input("YES (y) or NO (n/Enter): ").lower()
                return user_input in ["yes", "y"]

            def prompt_preference(pref_name, question, header_text, answer_yes, extra_yes, answer_no, extra_no):
                if pref_name is not None and pref_name != "":
                    pref_value = pref_name
                else:
                    pref_value = prompt_user(question)

                answer = answer_yes if pref_value in ['yes', 'y', True] else answer_no

                output = f"{header_text}==================================#"
                callback(f"\n[•] ", "blue")
                callback(f"{output}\n")
                callback(f"\n|     └-----→  ")
                callback(f"{answer}", "green")
                if pref_value:
                    callback(f"\n|              ")
                    callback(f"{extra_yes if answer == answer_yes else extra_no}", "green")
                else:
                    callback(f"\n|              ")
                    callback(f"{extra_yes if answer == answer_yes else extra_no}", "green")
                callback(f"\n\n#ˉˉˉˉˉˉˉˉˉˉˉˉˉˉˉˉˉˉˉˉˉˉˉˉˉˉˉˉˉˉˉˉˉˉˉˉˉˉˉˉˉˉˉˉˉˉˉˉˉˉˉˉˉˉˉˉˉˉˉˉˉˉˉˉˉˉˉˉˉˉ#")
                callback("\n")

                return pref_value


            # Pride Stickers
            pridesticker_pref = prompt_preference(pridesticker_pref,
                                                  "The helmet PRIDE STICKER preference is not defined in config.txt. \nDoes this uniform use helmet pride stickers? (y / n): ",
                                                  "HELMET PRIDE STICKERS?: ========", "YES, the uniform uses helmet pride stickers.",
                                                  "Be sure to provide a custom pridesticker.png.",
                                                  "NO, the uniform does not use helmet pride stickers.",
                                                  "The tool will automatically disable/transparent them.")

            # Helmet Numbers
            helmetnumbers_pref = prompt_preference(helmetnumbers_pref,
                                                  "The HELMET NUMBERS preference is not defined in config.txt. \nDoes this uniform have numbers on the back or side of the helmet? (y / n): ",
                                                  "HELMET NUMBERS?: ================", "YES, the uniform uses helmet numbers.",
                                                  "Helmet numbers will be copied (or created from the main numbers).",
                                                  "NO, the uniform does not use helmet numbers.",
                                                  "Only the name will be recorded in the CSV. No textures will be copied.")

            # Sleeve/Shoulder Numbers
            ssnumbers_pref = prompt_preference(ssnumbers_pref,
                                                  "The SLEEVE/SHOULDER NUMBERS preference is not defined in config.txt. \nDoes this uniform have numbers on the sleeves or top of the shoulders? (y / n): ",
                                                  "SLEEVE/SHOULDER NUMBERS?: ======", "YES, the uniform uses SLEEVE/SHOULDER numbers.",
                                                  "SLEEVE/SHOULDER numbers will be copied (or created from the main numbers).",
                                                  "NO, the uniform does not use SLEEVE/SHOULDER numbers.",
                                                  "Only the name will be recorded in the CSV. No textures will be copied.")

            # Function to convert config's string values to booleans
            def convert_to_boolean(value):
                if value is not None:
                    return str(value).strip().lower() in ["yes", "true"]
                return False

            # Extract pridesticker_pref from the config
            pridesticker_pref = convert_to_boolean(pridesticker_pref)

            # Extract helmetnumbers_pref from the config
            helmetnumbers_pref = convert_to_boolean(helmetnumbers_pref)

            # Extract ssnumbers_pref from the config
            ssnumbers_pref = convert_to_boolean(ssnumbers_pref)

        ############################################################################
        # IMAGE MATCHING IF NO CSV OVERRIDE PROVIDED

        if glove_normal_or_csv:
            # Pre-run Checklist
            callback("\n")  # Add a line break 
            callback("\n")  # Add a line break 
            callback(f"+++++++++ PRE-RUN CHECKLIST +++++++++++++\n", "blue")
            callback("\n")  # Add a line break 
            callback("Your dumps folder is expected to contain all 30-34 dumped textures\n")
            callback("for your chosen uniform type (light/dark). To dump all of these, you must have: \n")
            callback("\n")  # Add a line break 
            callback(" • Used the dumps ISO not the dev ISO or the normal mod ISO (so all numbers get dumped)\n")
            callback(" • Reset your rosters to that of the ISO default (so all gear gets used)\n")
            callback(" • Set the game weather to cold (so the Face Protector is worn)\n")
            callback(" • Deleted everything in your dumps folder during the game loading screen (after the uniform\n")
            callback("   selection screen and prior to the coin toss)\n")
            callback(" • Dumped during the coin toss (so the Face Protector top piece can dump)\n")
            callback(" • Run at least one play from scrimmage (not just the kickoff)\n")
            callback(" • Either let the the pre-game onfield presentation run its course OR have zoomed in close\n")
            callback("   during an instant replay (so the facemask near textures can dump)\n")
            callback("\n")  # Add a line break 
            callback("If you didn't do all of the things above when dumping the textures, your dumps folder\n")
            callback("probably does not contain all of the required textures, and you should \n")
            callback("delete the contents of the dumps folder, and do the dump again.\n")
        else:
            # Pre-run Checklist
            callback("\n")  # Add a line break 
            callback("\n")  # Add a line break 
            callback(f"+++++++++ PRE-RUN CHECKLIST +++++++++++++\n", "blue")
            callback("\n")  # Add a line break 
            callback("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!! \n")
            callback("!!!!!!!!!  NOTE: YOU HAVE DEFINED the glove type as 'second glove'. !!!!!!!!! \n")
            callback("!!!!!!!!!!!!!!!  ALL OTHER UNIFORM TEXTURES WILL BE SKIPPED.  !!!!!!!!!!!!!!! \n")
            callback("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!! \n\n")
            callback("Careful. If you run this mode incorrectly, the wrong texture will be matched. Are you sure:\n") 
            callback("\n")
            callback("- This is your second game dump for this uniform.\n") 
            callback("- You left the created uniform folder in RENAMED.\n") 
            callback("- You switched the host/visiting uniforms so....\n") 
            callback("\n")
            callback(" • If this is a LIGHT uniform, it is the HOME team\n")
            callback(" OR \n")
            callback(" • If this is a DARK uniform, it is the VISITING team\n")
          

        callback("\n")  # Add a line break 
        callback(f"___\n", "blue")
        callback("\n")  # Add a line break 

        callback("\n")  # Add a line break 
        callback("#----------------------------------------------------------#\n")
        callback("#                                                          #\n")
        callback("#                     RESULTS:                             #\n")
        callback("#                                                          #\n")


        if glove_normal_or_csv:
            # Rename the source files if they were made with photopea
            if photoshop_pref == '2':
                rename_photopea_files(source_folder, texture_name_mapping, texture_name_mapping_old)

        # Extract the first segment of uniform_slot_name
        if '-' in uniform_slot_name:
            teamname = uniform_slot_name.split('-')[0]
        else:
            teamname = uniform_slot_name

        # Extract the second segment of uniform_slot_name
        if '-' in uniform_slot_name:
            slotname = uniform_slot_name.split('-')[1]
        else:
            slotname = uniform_slot_name

        # Open a CSV file for writing
        csv_filename = f"textures-{uniform_slot_name}.csv"

        # Team glove csv filename
        teamgloves_csv_filename = f"textures-{teamname}-team.csv"

        # Extract the second segment of uniform_slot_name for the subfolder
        if '-' in uniform_slot_name:
            renamed_subfolder = uniform_slot_name.split('-')[1]
        else:
            renamed_subfolder = uniform_slot_name
        
        # Define the full path for the renamed folder and the destination CSV folder
        renamed_folder = os.path.join(base_dir, "RENAMED")
            
        if only_make_csv != "yes":
            csv_destination_folder = os.path.join(renamed_folder, teamname, renamed_subfolder, "csv-texture-names")
            teamgloves_destination_folder = os.path.join(renamed_folder, teamname, "_TEAM-ALL-UNIS")
        elif only_make_csv == "yes":
            csv_destination_folder = os.path.join(base_dir, "RENAMED")
            teamgloves_destination_folder = os.path.join(base_dir, "RENAMED")

        # Ensure the destination folder exists
        if glove_normal_or_csv:
            if not os.path.exists(csv_destination_folder):
              os.makedirs(csv_destination_folder)
            if include_team_glove:
              if not os.path.exists(teamgloves_destination_folder):
                  os.makedirs(teamgloves_destination_folder)

        # Define the full path to the CSV file in the destination folder
        csv_file_path = os.path.join(csv_destination_folder, csv_filename)
        teamgloves_csv_file_path = os.path.join(teamgloves_destination_folder, teamgloves_csv_filename)


        # Determine the file mode based on the value of glove_normal_or_csv
        if glove_normal_or_csv:
            # Open the CSV file in write mode ('w')
            file_mode = 'w'
        else:
            # Check if the file exists
            if os.path.isfile(csv_file_path):
                # If the file exists, use append mode ('a')
                file_mode = 'a'
            else:
                # If the file doesn't exist, print an error message and exit
                callback("\n")
                callback(f"###########################################################\n")
                callback(f"!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!\n", "red")
                callback(f"!!! ERROR: ", "red")
                callback(f"The file {csv_filename} does not exist. You must first run this tool with glove_second set to 'no' and keep the folder it makes in RENAMED, and then run again with this option enabled.\n")
                callback(f"!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!\n", "red")
                callback(f"###########################################################\n")
                # Pause for a thousand minutes
                time.sleep(1000 * 60)




        # Open the UNIFORM textures CSV file with the determined mode
        # Open the uniform CSV (always open)
        with open(csv_file_path, mode=file_mode, newline='') as csvfile:
            csv_writer = csv.DictWriter(csvfile, fieldnames=['TEAM NAME', 'SLOT', 'TYPE', 'TEXTURE', 'FILENAME'])
            if file_mode == 'w':
                csv_writer.writeheader()

            # Conditionally open team gloves CSV, or set writer to None
            csvfileteam = None
            csv_writer_team = None
            if include_team_glove:
                csvfileteam = open(teamgloves_csv_file_path, mode=file_mode, newline='')
                csv_writer_team = csv.DictWriter(csvfileteam, fieldnames=['TEAM NAME', 'SLOT', 'TYPE', 'TEXTURE', 'FILENAME'])
                if file_mode == 'w':
                    csv_writer_team.writeheader()

            # Function to calculate hash_tolerance_for_pass
            def calculate_hash_tolerance(reference_hash_phash, compared_hash_phash, reference_hash_dhash, compared_hash_dhash):
                return max(
                    abs(reference_hash_phash - compared_hash_phash),
                    abs(reference_hash_dhash - compared_hash_dhash)
                )

            # function to get all files in a directory
            def get_all_png_files_in_directory(directory):
                return [os.path.join(directory, f) for f in os.listdir(directory) if os.path.isfile(os.path.join(directory, f)) and f.lower().endswith(".png")]

            # Using a few different methods for comparing files to find the matching dumped texture
            def find_similar_images(reference_image_path, dumps_path, file_params=None, context=None):
                                    
                # # Construct the correct path for the reference image
                # if context:
                #   reference_image_path = os.path.join(base_dir, "utils", reference_folder, 'alts', source_image)
                # else:
                #   reference_image_path = os.path.join(base_dir, "utils", reference_folder, source_image)

                # Extract the directory containing the reference image
                reference_directory = os.path.dirname(reference_image_path)

                try:
                    reference_image = Image.open(reference_image_path)
                except FileNotFoundError:
                    # Print error message
                    callback("\n")
                    callback(f"###########################################################\n")
                    callback(f"!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!\n", "red")
                    callback(f"!!! ERROR: ", "red")
                    callback(f"Missing reference file at:\n")
                    callback(f"{reference_image_path}\n\n")
                    callback(f"You should re-install the app if you're not sure why it's missing.\n")
                    callback(f"!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!\n", "red")
                    callback(f"###########################################################\n")
                    # Delete the incomplete folder
                    if os.path.exists(renamed_folder):
                        shutil.rmtree(renamed_folder)
                    # Pause for a thousand minutes
                    time.sleep(1000 * 60)
                    
                reference_hash_phash = imagehash.phash(reference_image)
                reference_hash_dhash = imagehash.dhash(reference_image)
                reference_image_dimensions = reference_image.size
                reference_file_info = os.stat(reference_image_path)
                reference_file_size = reference_file_info.st_size

                similar_images = []

                for filename in os.listdir(dumps_path):
                    if filename.endswith(".png"):
                        file_path = os.path.join(dumps_path, filename)

                        # callback("\n")
                        # callback("\n")
                        # callback(f"Comparing {reference_image_path} and {file_path}") 
                        # callback(f"file is a PNG file.")

                        compared_file_info = os.stat(file_path)
                        compared_file_size = compared_file_info.st_size

                        # Limit to only files of similar size
                        if abs(reference_file_size - compared_file_size) <= 100:  # 1024 = Within 1kb file size difference
                            compared_image = Image.open(file_path)
                            compared_image_dimensions = compared_image.size

                            if reference_image_dimensions == compared_image_dimensions:
                                compared_hash_phash = imagehash.phash(compared_image)
                                compared_hash_dhash = imagehash.dhash(compared_image)

                                # Check if per-item parameters exist and use default values from config.txt if not
                                hash_tolerance_default = config_content.get('hash_tolerance_default', 8)
                                ssim_threshold_default = config_content.get('ssim_threshold_default', 0.93)

                                hash_tolerance = file_params.get('hash_tolerance', None) if file_params is not None else None
                                ssim_threshold = file_params.get('ssim_threshold', None) if file_params is not None else None

                                # Set to default if not provided in file_params
                                hash_tolerance = hash_tolerance if hash_tolerance is not None else hash_tolerance_default
                                ssim_threshold = ssim_threshold if ssim_threshold is not None else ssim_threshold_default

                                if (
                                        abs(reference_hash_phash - compared_hash_phash) <= hash_tolerance
                                        and abs(reference_hash_dhash - compared_hash_dhash) <= hash_tolerance
                                ):
                                  reference_cv_image = cv2.imread(reference_image_path)
                                  compared_cv_image = cv2.imread(file_path)

                                  ssim = compare_ssim(reference_cv_image, compared_cv_image, win_size=5, multichannel=True,
                                                      channel_axis=2)
                                
                                  
                                  # callback(f"Comparing {reference_image_path} and {file_path}")
                                  # callback(f"SSIM: {ssim}")


                                  if ssim >= ssim_threshold:
                                      # Calculate hash_tolerance_for_pass and print the result
                                      hash_tolerance_for_pass = calculate_hash_tolerance(
                                          reference_hash_phash, compared_hash_phash,
                                          reference_hash_dhash, compared_hash_dhash
                                      )
                                      similar_images.append((file_path, ssim, hash_tolerance_for_pass))
                                      # Sort by SSIM value (descending) and hash_tolerance_for_pass (ascending)
                                      similar_images.sort(key=lambda x: (-x[1], x[2]))

                return similar_images







            # Dictionary of files and their corresponding source images in the reference_folder folder
            # you can override the default file match paramaters to tighten or loosen the search
            # Assuming that you have already loaded the config.txt values into config_content dictionary

            # Dictionary of files and their corresponding source images in the reference_folder folder
            # you can override the default file match parameters to tighten or loosen the search
            reference_files = {
                # "glove-second.png": {"source": "glove-second.png", "hash_tolerance": config_content.get('hash_tolerance_glove'), "ssim_threshold": config_content.get('ssim_threshold_glove')},
                "glove-uni-1-second.png": {"source": "glove-uni-1-second.png", "hash_tolerance": config_content.get('hash_tolerance_glove'), "ssim_threshold": config_content.get('ssim_threshold_glove')},
                "glove-uni-2-second.png": {"source": "glove-uni-2-second.png", "hash_tolerance": config_content.get('hash_tolerance_glove'), "ssim_threshold": config_content.get('ssim_threshold_glove')},
                "06-TC_Face_Protector.png": {"source": "06-TC_Face_Protector.png", "hash_tolerance": config_content.get('hash_tolerance_06_TC_Face_Protector'), "ssim_threshold": config_content.get('ssim_threshold_06_TC_Face_Protector')},
                "25-TC_Face_Protector_Top.png": {"source": "25-TC_Face_Protector_Top.png", "hash_tolerance": config_content.get('hash_tolerance_25_TC_Face_Protector_Top'), "ssim_threshold": config_content.get('ssim_threshold_25_TC_Face_Protector_Top')},
                "14-Bk_TC_Pad.png": {"source": "14-Bk_TC_Pad.png", "hash_tolerance": config_content.get('hash_tolerance_14_Bk_TC_Pad'), "ssim_threshold": config_content.get('ssim_threshold_14_Bk_TC_Pad')},
                "10-Wt_TC_Pad.png": {"source": "10-Wt_TC_Pad.png", "hash_tolerance": config_content.get('hash_tolerance_10_Wt_TC_Pad'), "ssim_threshold": config_content.get('ssim_threshold_10_Wt_TC_Pad')},
                "07-TC_Med_Band--34_sleeve_top.png": {"source": "07-TC_Med_Band--34_sleeve_top.png", "hash_tolerance": config_content.get('hash_tolerance_07_TC_Med_Band--34_sleeve_top'), "ssim_threshold": config_content.get('ssim_threshold_07_TC_Med_Band--34_sleeve_top')},
                "04-TC_Thin_Band.png": {"source": "04-TC_Thin_Band.png", "hash_tolerance": config_content.get('hash_tolerance_04_TC_Thin_Band'), "ssim_threshold": config_content.get('ssim_threshold_04_TC_Thin_Band')},
                "15-TC_Long_Sleeve.png": {"source": "15-TC_Long_Sleeve.png", "hash_tolerance": config_content.get('hash_tolerance_15_TC_Long_Sleeve'), "ssim_threshold": config_content.get('ssim_threshold_15_TC_Long_Sleeve')},
                "wrist_QB_Wrist_Bk.png": {"source": "wrist_QB_Wrist_Bk.png", "hash_tolerance": config_content.get('hash_tolerance_wrist_QB_Wrist_Bk'), "ssim_threshold": config_content.get('ssim_threshold_wrist_QB_Wrist_Bk')},
                "wrist_QB_Wrist_Wt.png": {"source": "wrist_QB_Wrist_Wt.png", "hash_tolerance": config_content.get('hash_tolerance_wrist_QB_Wrist_Wt'), "ssim_threshold": config_content.get('ssim_threshold_wrist_QB_Wrist_Wt')},
                "03-TC_QB_Wrist.png": {"source": "03-TC_QB_Wrist.png", "hash_tolerance": config_content.get('hash_tolerance_03_TC_QB_Wrist'), "ssim_threshold": config_content.get('ssim_threshold_03_TC_QB_Wrist')},
                "01-TC_Wrist.png": {"source": "01-TC_Wrist.png", "hash_tolerance": config_content.get('hash_tolerance_01_TC_Wrist'), "ssim_threshold": config_content.get('ssim_threshold_01_TC_Wrist')},
                "wrist_Half_Sleeve_Wt.png": {"source": "wrist_Half_Sleeve_Wt.png", "hash_tolerance": config_content.get('hash_tolerance_wrist_Half_Sleeve_Wt'), "ssim_threshold": config_content.get('ssim_threshold_wrist_Half_Sleeve_Wt')},
                "wrist_Half_Sleeve_Bk.png": {"source": "wrist_Half_Sleeve_Bk.png", "hash_tolerance": config_content.get('hash_tolerance_wrist_Half_Sleeve_Bk'), "ssim_threshold": config_content.get('ssim_threshold_wrist_Half_Sleeve_Bk')},
                "11-TC_Half_Sleeve.png": {"source": "11-TC_Half_Sleeve.png", "hash_tolerance": config_content.get('hash_tolerance_11_TC_Half_Sleeve'), "ssim_threshold": config_content.get('ssim_threshold_11_TC_Half_Sleeve')},
                "16-Shoe.png": {"source": "16-Shoe.png", "hash_tolerance": config_content.get('hash_tolerance_16_Shoe'), "ssim_threshold": config_content.get('ssim_threshold_16_Shoe')},
                "17-Shoe_w_White_Tape.png": {"source": "17-Shoe_w_White_Tape.png", "hash_tolerance": config_content.get('hash_tolerance_17_Shoe_w_White_Tape'), "ssim_threshold": config_content.get('ssim_threshold_17_Shoe_w_White_Tape')},
                "23-Shoe_w_Black_Tape.png": {"source": "23-Shoe_w_Black_Tape.png", "hash_tolerance": config_content.get('hash_tolerance_23_Shoe_w_Black_Tape'), "ssim_threshold": config_content.get('ssim_threshold_23_Shoe_w_Black_Tape')},
                "24-Shoe_w_TC_Tape.png": {"source": "24-Shoe_w_TC_Tape.png", "hash_tolerance": config_content.get('hash_tolerance_24_Shoe_w_TC_Tape'), "ssim_threshold": config_content.get('ssim_threshold_24_Shoe_w_TC_Tape')},
                "13-Sock.png": {"source": "13-Sock.png", "hash_tolerance": config_content.get('hash_tolerance_13_Sock'), "ssim_threshold": config_content.get('ssim_threshold_13_Sock')},
                "helmet.png": {"source": "helmet.png", "hash_tolerance": config_content.get('hash_tolerance_helmet'), "ssim_threshold": config_content.get('ssim_threshold_helmet')},
                "22-Chinstrap.png": {"source": "22-Chinstrap.png", "hash_tolerance": config_content.get('hash_tolerance_22_Chinstrap'), "ssim_threshold": config_content.get('ssim_threshold_22_Chinstrap')},
                "pridesticker.png": {"source": "pridesticker.png", "hash_tolerance": config_content.get('hash_tolerance_pridesticker'), "ssim_threshold": config_content.get('ssim_threshold_pridesticker')},
                "18-Facemask_Far.png": {"source": "18-Facemask_Far.png", "hash_tolerance": config_content.get('hash_tolerance_18_Facemask_Far'), "ssim_threshold": config_content.get('ssim_threshold_18_Facemask_Far')},
                "20-Facemask_Near.png": {"source": "20-Facemask_Near.png", "hash_tolerance": config_content.get('hash_tolerance_20_Facemask_Near'), "ssim_threshold": config_content.get('ssim_threshold_20_Facemask_Near')},
                "pants.png": {"source": "pants.png", "hash_tolerance": config_content.get('hash_tolerance_pants'), "ssim_threshold": config_content.get('ssim_threshold_pants')},
                "jersey.png": {"source": "jersey.png", "hash_tolerance": config_content.get('hash_tolerance_jersey'), "ssim_threshold": config_content.get('ssim_threshold_jersey')},
                "num07.png": {"source": "num07.png", "hash_tolerance": config_content.get('hash_tolerance_num07'), "ssim_threshold": config_content.get('ssim_threshold_num07')},
                "num89.png": {"source": "num89.png", "hash_tolerance": config_content.get('hash_tolerance_num89'), "ssim_threshold": config_content.get('ssim_threshold_num89')},
                "num07shadow.png": {"source": "num07shadow.png", "hash_tolerance": config_content.get('hash_tolerance_num07shadow'), "ssim_threshold": config_content.get('ssim_threshold_num07shadow')},
                "num89shadow.png": {"source": "num89shadow.png", "hash_tolerance": config_content.get('hash_tolerance_num89shadow'), "ssim_threshold": config_content.get('ssim_threshold_num89shadow')},
                "num07helmet.png": {"source": "num07helmet.png", "hash_tolerance": config_content.get('hash_tolerance_num07helmet'), "ssim_threshold": config_content.get('ssim_threshold_num07helmet')},
                "num89helmet.png": {"source": "num89helmet.png", "hash_tolerance": config_content.get('hash_tolerance_num89helmet'), "ssim_threshold": config_content.get('ssim_threshold_num89helmet')},
                "num07ss.png": {"source": "num07ss.png", "hash_tolerance": config_content.get('hash_tolerance_num07ss'), "ssim_threshold": config_content.get('ssim_threshold_num07ss')},
                "num89ss.png": {"source": "num89ss.png", "hash_tolerance": config_content.get('hash_tolerance_num89ss'), "ssim_threshold": config_content.get('ssim_threshold_num89ss')},
                "glove-uni-1.png": {"source": "glove-uni-1.png", "hash_tolerance": config_content.get('hash_tolerance_glove'), "ssim_threshold": config_content.get('ssim_threshold_glove')},
                "glove-uni-2.png": {"source": "glove-uni-2.png", "hash_tolerance": config_content.get('hash_tolerance_glove'), "ssim_threshold": config_content.get('ssim_threshold_glove')},
                "glove-team-1.png": {"source": "glove-team-1.png", "hash_tolerance": config_content.get('hash_tolerance_glove'), "ssim_threshold": config_content.get('ssim_threshold_glove')},
                "glove-team-2.png": {"source": "glove-team-2.png", "hash_tolerance": config_content.get('hash_tolerance_glove'), "ssim_threshold": config_content.get('ssim_threshold_glove')}
            }


            # Track multiple matches for warnings
            multiple_matches_dict = {}

            # Define a list of files to skip the multiple matches warning
            skip_warn_multiple = ["num07shadow.png", "num89shadow.png"]

            # Define variables for the base jersey numbers file names
            base_image_num07 = None
            base_image_num89 = None

            # Find the matching dumps for the base jersey numbers and save the filenames for the number shadows step later
            for file, file_data in reference_files.items():
                source_image = file_data["source"]
                params = file_data if 'hash_tolerance' in file_data and 'ssim_threshold' in file_data else None
                similar_images = find_similar_images(os.path.join(base_dir, "utils", reference_folder, source_image), dumps_path, params)

                if file == "num07.png" and similar_images:
                    base_image_num07 = similar_images[0]  # Taking the first match as the base for num07.png
                elif file == "num89.png" and similar_images:
                    base_image_num89 = similar_images[0]  # Taking the first match as the base for num89.png

                if len(similar_images) > 1:
                    multiple_matches_dict[file] = True  # Track items with multiple matches
            



            # Initialize a counter for successful operations
            self.required_textures_counter = 0
            self.optional_textures_counter = 0

            # Check for gloves and use fallbacks if needed
            def get_glove_path(source_folder, source_image, mode="team1"):
                """
                Determine the correct glove source file path with fallback order.

                Modes:
                  - "team": for team gloves (team 1, team 2)
                  - "uniform": for regular uniform gloves
                  - "second_uni_1": for SECOND uniform 1 gloves
                  - "second_uni_2": for SECOND uniform 2 gloves
                """

                # 1️⃣ Try source_image first (if defined)
                if source_image:
                    path = os.path.join(source_folder, source_image)
                    if os.path.exists(path):
                        return path

                # 2️⃣ Define fallback orders by mode
                if mode == "team_1": # glove-team-1.png
                    fallbacks = [
                        "gloveteam1.png",
                        "glove-team.png",
                        "gloveteam.png",
                        "glove.png"
                    ]
                if mode == "team_2": # glove-team-2.png
                    fallbacks = [
                        "gloveteam2.png",
                        "glove-team.png",
                        "gloveteam.png",
                        "glove.png"
                    ]

                elif mode == "uniform_1": # glove-uni-1.png
                    fallbacks = [
                        "gloveuni1.png",
                        "glove-uni.png",
                        "gloveuni.png",
                        "glove-uni-2.png",
                        "gloveuni2.png",
                        "glove-team-1.png",
                        "gloveteam1.png",
                        "glove-team.png",
                        "gloveteam.png",
                        "glove.png"
                    ]
                elif mode == "uniform_2": # glove-uni-2.png
                    fallbacks = [
                        "gloveuni2.png",
                        "glove-uni.png",
                        "gloveuni.png",
                        "glove-uni-1.png",
                        "gloveuni1.png",
                        "glove-team-2.png",
                        "gloveteam2.png",
                        "glove-team-1.png",
                        "gloveteam1.png",
                        "glove-team.png",
                        "gloveteam.png",
                        "glove.png"
                    ]

                elif mode == "second_uni_1": # glove-uni-1.png (away)
                    fallbacks = [
                        "glove-uni-1.png",
                        "gloveuni1.png",
                        "glove-uni.png",
                        "gloveuni.png",
                        "glove-uni-2.png",
                        "gloveuni2.png",
                        "glove-team-1.png",
                        "gloveteam1.png",
                        "glove-team-2.png",
                        "gloveteam2.png",
                        "glove-team.png",
                        "gloveteam.png",
                        "glove.png"
                    ]

                elif mode == "second_uni_2": # glove-uni-2.png (away)
                    fallbacks = [
                        "glove-uni-2.png",
                        "gloveuni2.png",
                        "glove-uni.png",
                        "gloveuni.png",
                        "glove-uni-1.png",
                        "gloveuni1.png",
                        "glove-team-2.png",
                        "gloveteam2.png",
                        "glove-team-1.png",
                        "gloveteam1.png",
                        "glove-team.png",
                        "gloveteam.png",
                        "glove.png"
                    ]

                else:
                    fallbacks = []

                # 3️⃣ Try each fallback in order
                for filename in fallbacks:
                    path = os.path.join(source_folder, filename)
                    if os.path.exists(path):
                        return path

                # 4️⃣ If nothing found
                return None


            # Function to process each matching texture
            def process_texture(file, file_data, similar_images, csv_writer=None, csv_writer_team=None):
                # callback(f"DEBUG: Running process_texture  #\n")
                # global required_textures_counter  # Declare the counter as a global variable
                # global optional_textures_counter  # Declare the counter as a global variable
                callback("\n")  # Add a line break 
                callback(f"[•] ", "blue")
                callback(f"Dumped texture found for {file}:\n")
                for image_path, similarity, hash_tolerance_for_pass in similar_images:
                    callback(f"{image_path}\n")
                    callback(f"Min hash: {hash_tolerance_for_pass} - Max SSIM: {similarity:.4f}\n")


                    # Extract the filename (without extension) of the found image
                    found_filename = os.path.splitext(os.path.basename(image_path))[0]

                    # Extract the reference file name (without extension)
                    reference_filename = os.path.splitext(source_image)[0]

                    # Extract the first segment of uniform_slot_name
                    if '-' in uniform_slot_name:
                        renamed_subfolder0 = uniform_slot_name.split('-')[0]
                    else:
                        renamed_subfolder0 = uniform_slot_name

                    # Extract the second segment of uniform_slot_name
                    if '-' in uniform_slot_name:
                        renamed_subfolder = uniform_slot_name.split('-')[1]
                    else:
                        renamed_subfolder = uniform_slot_name

                    # Redefine the 'renamed' folder
                    renamed_folder = os.path.join(base_dir, "RENAMED", renamed_subfolder0, renamed_subfolder)

                    
                    # Create 'renamed' folder if it doesn't exist
                    if only_make_csv != "yes":
                        if not os.path.exists(renamed_folder):
                            os.makedirs(renamed_folder)
                        
                    
                    # Transparent the number shadows
                    if file in ["num07shadow.png", "num89shadow.png"]:
                        base_image = None
                        
                        if file == "num07shadow.png" and base_image_num07:
                            base_image = base_image_num07
                            renamed_subfolder = "num07-shadow"
                        elif file == "num89shadow.png" and base_image_num89:
                            base_image = base_image_num89
                            renamed_subfolder = "num89-shadow"

                        if base_image:
                            base_image_name = os.path.splitext(os.path.basename(base_image[0]))[0] 
                            found_filename_base = os.path.splitext(os.path.basename(image_path))[0]
                            
                            # Extract the number part of the filenames to compare
                            base_image_number = base_image_name.split("-")[0]
                            found_number = found_filename_base.split("-")[0]
                            
                            if base_image_number == found_number:
                                # Create subfolder if it doesn't exist
                                if only_make_csv != "yes":
                                    if not os.path.exists(os.path.join(renamed_folder, renamed_subfolder)):
                                        os.makedirs(os.path.join(renamed_folder, renamed_subfolder))
                                # Copy a transparent to the 'renamed' folder and rename 
                                new_file_name = f"{found_filename_base}.png"

                                try:
                                    if only_make_csv != "yes":
                                      # Attempt to copy the file
                                      shutil.copy(os.path.join(default_textures_folder, "transparent.png"), os.path.join(renamed_folder, renamed_subfolder, new_file_name))
                                    callback("NUMBER SHADOW TRANSPARENTED\n")
                                    callback(f"{checkmark} ", "green")
                                    callback(f"SUCCESS. Transparent renamed and filename added to the CSV file.\n")
                                    self.required_textures_counter += 1
                                    # Write to the CSV file
                                    csv_writer.writerow({'TEAM NAME': teamname, 'SLOT': slotname, 'TYPE': uniform_type, 'TEXTURE': file, 'FILENAME': new_file_name})
                                except FileNotFoundError:
                                    # Print error message
                                    callback("\n")
                                    callback(f"###########################################################\n")
                                    callback(f"!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!\n", "red")
                                    callback(f"!!! ERROR: ", "red")
                                    callback(f"The {source_image} default textures is missing from:\n")
                                    callback(f"{default_textures_folder}\n")
                                    callback(f"You should re-install the app if you're not sure why it's missing.\n")
                                    callback(f"!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!\n", "red")
                                    callback(f"###########################################################\n")
                                    # Delete the incomplete folder
                                    if os.path.exists(renamed_folder):
                                        shutil.rmtree(renamed_folder)
                                    # Pause for a thousand minutes
                                    time.sleep(1000 * 60)


                    # Skip team gloves if option not checked
                    elif not include_team_glove and file in ("glove-team-1.png", "glove-team-2.png"):
                        continue

                    # Glove - Team 1
                    elif include_team_glove and file == "glove-team-1.png":
                        new_file_name = f"{found_filename}.png"
                        # Create glove subfolder if it doesn't exist
                        glove_folder = "glove-team-1"
                        glove_path = os.path.join(source_folder, source_image)
                        # Check if source_image exists and use fallbacks if needed
                        glove_path = get_glove_path(source_folder, source_image, mode="team_1")
                        if glove_path:
                            # Copy and rename glove-team-1.png
                            if only_make_csv != "yes":
                                if not os.path.exists(os.path.join(teamgloves_destination_folder, glove_folder)):
                                    os.makedirs(os.path.join(teamgloves_destination_folder, glove_folder))
                                shutil.copy(glove_path, os.path.join(teamgloves_destination_folder, glove_folder, new_file_name))
                            # Write to the CSV file
                            # callback(f"DEBUG: Attempting to write to the CSV file.\n")
                            csv_writer_team.writerow({'TEAM NAME': teamname, 'SLOT': "ALL", 'TYPE': "TEAM", 'TEXTURE': file, 'FILENAME': new_file_name})
                            callback(f"{checkmark} ", "green")
                            callback(f"Texture renamed and filename added to the CSV file.\n")
                            self.optional_textures_counter += 1
                        else:
                            if only_make_csv != "yes":
                              # Print error message
                              callback("\n")
                              callback(f"###########################################################\n")
                              callback(f"!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!\n", "red")
                              callback(f"!!! ERROR: ", "red")
                              callback(f"No file named glove-team-1.png exists in YOUR_TEXTURES. Add the source file and try again.\n")
                              callback(f"!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!\n", "red")
                              callback(f"###########################################################\n")
                              # Pause for a thousand minutes
                              time.sleep(1000 * 60)
                            else:
                              # Write to the CSV file
                              csv_writer_team.writerow({'TEAM NAME': teamname, 'SLOT': slotname, 'TYPE': uniform_type, 'TEXTURE': file, 'FILENAME': new_file_name})
                              callback(f"{checkmark} ", "green")
                              callback(f"SUCCESS. Filename added to the CSV file.\n")
                    
                    # Glove - Team 2
                    elif include_team_glove and file == "glove-team-2.png":
                        new_file_name = f"{found_filename}.png"
                        # Create glove subfolder if it doesn't exist
                        glove_folder = "glove-team-2"
                        # Check if source_image exists and use fallbacks if needed
                        glove_path = get_glove_path(source_folder, source_image, mode="team_2")
                        if glove_path:
                            # Copy and rename glove-team-2.png
                            if only_make_csv != "yes":
                                if not os.path.exists(os.path.join(teamgloves_destination_folder, glove_folder)):
                                    os.makedirs(os.path.join(teamgloves_destination_folder, glove_folder))
                                shutil.copy(glove_path, os.path.join(teamgloves_destination_folder, glove_folder, new_file_name))
                            # Write to the CSV file
                            # callback(f"DEBUG: Attempting to write to the CSV file.\n")
                            csv_writer_team.writerow({'TEAM NAME': teamname, 'SLOT': "ALL", 'TYPE': "TEAM", 'TEXTURE': file, 'FILENAME': new_file_name})
                            callback(f"{checkmark} ", "green")
                            callback(f"Texture renamed and filename added to the CSV file.\n")
                            self.optional_textures_counter += 1
                        else:
                            if only_make_csv != "yes":
                              # Print error message
                              callback("\n")
                              callback(f"###########################################################\n")
                              callback(f"!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!\n", "red")
                              callback(f"!!! ERROR: ", "red")
                              callback(f"No file named glove-team-2.png exists in YOUR_TEXTURES. Add the source file and try again.\n")
                              callback(f"!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!\n", "red")
                              callback(f"###########################################################\n")
                              # Pause for a thousand minutes
                              time.sleep(1000 * 60)
                            else:
                              # Write to the CSV file
                              csv_writer_team.writerow({'TEAM NAME': teamname, 'SLOT': slotname, 'TYPE': uniform_type, 'TEXTURE': file, 'FILENAME': new_file_name})
                              callback(f"{checkmark} ", "green")
                              callback(f"SUCCESS. Filename added to the CSV file.\n")

                    # Glove - Uniform 1
                    elif file == "glove-uni-1.png":
                        new_file_name = f"{found_filename}.png"
                        # Create glove subfolder if it doesn't exist
                        if uniform_type == "dark":
                            glove_folder = "glove-uni-1-home"
                        else:
                            glove_folder = "glove-uni-1-away"
                        # Check if source_image exists and use fallbacks if needed
                        glove_path = get_glove_path(source_folder, source_image, mode="uniform_1")
                        if glove_path:
                            # Copy and rename glove-uni-1.png
                            if only_make_csv != "yes":
                                if not os.path.exists(os.path.join(renamed_folder, glove_folder)):
                                    os.makedirs(os.path.join(renamed_folder, glove_folder))
                                shutil.copy(glove_path, os.path.join(renamed_folder, glove_folder, new_file_name))
                            # Write to the CSV file
                            csv_writer.writerow({'TEAM NAME': teamname, 'SLOT': slotname, 'TYPE': uniform_type, 'TEXTURE': file, 'FILENAME': new_file_name})
                            callback(f"{checkmark} ", "green")
                            callback(f"Texture renamed and filename added to the CSV file.\n")
                            self.required_textures_counter += 1
                        else:
                            if only_make_csv != "yes":
                              # Print error message
                              callback("\n")
                              callback(f"###########################################################\n")
                              callback(f"!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!\n", "red")
                              callback(f"!!! ERROR: ", "red")
                              callback(f"No file named glove-uni-1.png exists in YOUR_TEXTURES. Add the source file and try again.\n")
                              callback(f"!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!\n", "red")
                              callback(f"###########################################################\n")
                              # Pause for a thousand minutes
                              time.sleep(1000 * 60)
                            else:
                              # Write to the CSV file
                              csv_writer.writerow({'TEAM NAME': teamname, 'SLOT': slotname, 'TYPE': uniform_type, 'TEXTURE': file, 'FILENAME': new_file_name})
                              callback(f"{checkmark} ", "green")
                              callback(f"SUCCESS. Filename added to the CSV file.\n")
                              self.required_textures_counter += 1

                    # Glove - Uniform 2
                    elif file == "glove-uni-2.png":
                        new_file_name = f"{found_filename}.png"
                        # Create glove subfolder if it doesn't exist
                        if uniform_type == "dark":
                            glove_folder = "glove-uni-2-home"
                        else:
                            glove_folder = "glove-uni-2-away"
                        # Check if source_image exists and use fallbacks if needed
                        glove_path = get_glove_path(source_folder, source_image, mode="uniform_2")
                        if glove_path:
                            # Copy and rename glove-uni-2.png
                            if only_make_csv != "yes":
                                if not os.path.exists(os.path.join(renamed_folder, glove_folder)):
                                    os.makedirs(os.path.join(renamed_folder, glove_folder))
                                shutil.copy(glove_path, os.path.join(renamed_folder, glove_folder, new_file_name))
                            # Write to the CSV file
                            csv_writer.writerow({'TEAM NAME': teamname, 'SLOT': slotname, 'TYPE': uniform_type, 'TEXTURE': file, 'FILENAME': new_file_name})
                            callback(f"{checkmark} ", "green")
                            callback(f"Texture renamed and filename added to the CSV file.\n")
                            self.required_textures_counter += 1
                        else:
                            if only_make_csv != "yes":
                              # Print error message
                              callback("\n")
                              callback(f"###########################################################\n")
                              callback(f"!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!\n", "red")
                              callback(f"!!! ERROR: ", "red")
                              callback(f"No file named glove-uni-2.png exists in YOUR_TEXTURES. Add the source file and try again.\n")
                              callback(f"!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!\n", "red")
                              callback(f"###########################################################\n")
                              # Pause for a thousand minutes
                              time.sleep(1000 * 60)
                            else:
                              # Write to the CSV file
                              csv_writer.writerow({'TEAM NAME': teamname, 'SLOT': slotname, 'TYPE': uniform_type, 'TEXTURE': file, 'FILENAME': new_file_name})
                              callback(f"{checkmark} ", "green")
                              callback(f"SUCCESS. Filename added to the CSV file.\n")
                              self.required_textures_counter += 1
                    
                    # Second Glove
                    elif glove_normal_or_csv and file in ("glove-uni-1-second.png", "glove-uni-2-second.png"):
                        continue
                      
                    # Second Glove - Uniform 1
                    elif file == "glove-uni-1-second.png":
                        new_file_name = f"{found_filename}.png"
                        # Create glove subfolder if it doesn't exist
                        if uniform_type == "dark":
                            glove_folder = "glove-uni-1-away"
                        else:
                            glove_folder = "glove-uni-1-home"
                        # Check if source_image exists and use fallbacks if needed
                        glove_path = get_glove_path(source_folder, source_image, mode="second_uni_1")
                        if glove_path:
                            if only_make_csv != "yes":
                            # Copy and rename glove-uni-1.png
                                if not os.path.exists(os.path.join(renamed_folder, glove_folder)):
                                    os.makedirs(os.path.join(renamed_folder, glove_folder))
                                shutil.copy(glove_path, os.path.join(renamed_folder, glove_folder, new_file_name))
                            # Write to the CSV file
                            csv_writer.writerow({'TEAM NAME': teamname, 'SLOT': slotname, 'TYPE': uniform_type, 'TEXTURE': file, 'FILENAME': new_file_name})
                            callback(f"{checkmark} ", "green")
                            callback(f"SUCCESS. Texture renamed and filename added to the CSV file.\n")
                            self.required_textures_counter += 1
                        else:
                            if only_make_csv != "yes":
                              # Print error message
                              callback("\n")
                              callback(f"###########################################################\n")
                              callback(f"!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!\n", "red")
                              callback(f"!!! ERROR: ", "red")
                              callback(f"No file named glove-uni-1.png exists in YOUR_TEXTURES. Add the source file and try again.\n")
                              callback(f"!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!\n", "red")
                              callback(f"###########################################################\n")
                              # Pause for a thousand minutes
                              time.sleep(1000 * 60)
                            else:
                              # Write to the CSV file
                              csv_writer.writerow({'TEAM NAME': teamname, 'SLOT': slotname, 'TYPE': uniform_type, 'TEXTURE': file, 'FILENAME': new_file_name})
                              callback(f"{checkmark} ", "green")
                              callback(f"SUCCESS. Filename added to the CSV file.\n")
                              self.required_textures_counter += 1

                            

                    # Second Glove - Uniform 2
                    elif file == "glove-uni-2-second.png":
                        new_file_name = f"{found_filename}.png"
                        # Create glove subfolder if it doesn't exist
                        if uniform_type == "dark":
                            glove_folder = "glove-uni-2-away"
                        else:
                            glove_folder = "glove-uni-2-home"
                        # Check if source_image exists and use fallbacks if needed
                        glove_path = get_glove_path(source_folder, source_image, mode="second_uni_2")
                        if glove_path:
                            if only_make_csv != "yes":
                            # Copy and rename glove.png
                                if not os.path.exists(os.path.join(renamed_folder, glove_folder)):
                                    os.makedirs(os.path.join(renamed_folder, glove_folder))
                                shutil.copy(glove_path, os.path.join(renamed_folder, glove_folder, new_file_name))
                            # Write to the CSV file
                            csv_writer.writerow({'TEAM NAME': teamname, 'SLOT': slotname, 'TYPE': uniform_type, 'TEXTURE': file, 'FILENAME': new_file_name})
                            callback(f"{checkmark} ", "green")
                            callback(f"SUCCESS. Texture renamed and filename added to the CSV file.\n")
                            self.required_textures_counter += 1
                        else:
                          if only_make_csv != "yes":
                            # Print error message
                            callback("\n")
                            callback(f"###########################################################\n")
                            callback(f"!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!\n", "red")
                            callback(f"!!! ERROR: ", "red")
                            callback(f"No file named glove-uni-2.png exists in YOUR_TEXTURES. Add the source file and try again.\n")
                            callback(f"!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!\n", "red")
                            callback(f"###########################################################\n")
                            # Pause for a thousand minutes
                            time.sleep(1000 * 60)
                          else:
                            # Write to the CSV file
                            csv_writer.writerow({'TEAM NAME': teamname, 'SLOT': slotname, 'TYPE': uniform_type, 'TEXTURE': file, 'FILENAME': new_file_name})
                            callback(f"{checkmark} ", "green")
                            callback(f"SUCCESS. Filename added to the CSV file.\n")
                            self.required_textures_counter += 1
                    
                    # If answered yes to transparent pride sticker, copy the transparent image instead of a source image
                    elif file == "pridesticker.png":
                        new_file_name = f"{found_filename}.png"
                        # Create Pride Sticker subfolder if it doesn't exist
                        if only_make_csv != "yes":
                            if not os.path.exists(os.path.join(renamed_folder, "pride-sticker")):
                                os.makedirs(os.path.join(renamed_folder, "pride-sticker"))
                        if pridesticker_pref:
                            pridesticker_path = os.path.join(source_folder, source_image)
                            # Check if source_image exists
                            if os.path.exists(pridesticker_path):
                                # Copy and rename pridesticker.png folder and rename 
                                if only_make_csv != "yes":
                                    shutil.copy(pridesticker_path, os.path.join(renamed_folder, "pride-sticker", new_file_name))
                                # Write to the CSV file
                                csv_writer.writerow({'TEAM NAME': teamname, 'SLOT': slotname, 'TYPE': uniform_type, 'TEXTURE': file, 'FILENAME': new_file_name})
                                callback(f"{checkmark} ", "green")
                                callback(f"SUCCESS. Texture renamed and filename added to the CSV file.\n")
                                self.required_textures_counter += 1
                            else:
                                # Print error message
                                callback("\n")
                                callback(f"###########################################################\n")
                                callback(f"!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!\n", "red")
                                callback(f"!!! ERROR:", "red")
                                callback(f" You want to use a pride sticker but no pridesticker.png source file exists in YOUR_TEXTURES. Add the source file and try again, or uncheck the Pride Sticker preference and re-run.\n")
                                callback(f"!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!\n", "red")
                                callback(f"###########################################################\n")
                                # Delete the incomplete folder
                                if os.path.exists(renamed_folder):
                                    shutil.rmtree(renamed_folder)
                                # Pause for a thousand minutes
                                time.sleep(1000 * 60)
                        else: 
                            try:
                                # Copy a transparent to the 'renamed' folder and rename 
                                if only_make_csv != "yes":
                                    shutil.copy(os.path.join(default_textures_folder, "transparent.png"), os.path.join(renamed_folder, "pride-sticker", new_file_name))
                                callback("PRIDE STICKER TRANSPARENTED\n")
                                # Write to the CSV file
                                csv_writer.writerow({'TEAM NAME': teamname, 'SLOT': slotname, 'TYPE': uniform_type, 'TEXTURE': file, 'FILENAME': new_file_name})
                                callback(f"{checkmark} ", "green")
                                callback(f"SUCCESS. Transparent texture renamed and filename added to the CSV file.\n")
                                self.required_textures_counter += 1
                            except FileNotFoundError:
                                # Print error message
                                callback("\n")
                                callback(f"###########################################################\n")
                                callback(f"!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!\n", "red")
                                callback(f"!!! ERROR: ", "red")
                                callback(f"The {source_image} default textures is missing from:\n")
                                callback(f"{default_textures_folder}\n\n")
                                callback(f"You should re-install the app if you're not sure why it's missing.\n")
                                callback(f"!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!\n", "red")
                                callback(f"###########################################################\n")
                                # Delete the incomplete folder
                                if os.path.exists(renamed_folder):
                                    shutil.rmtree(renamed_folder)
                                # Pause for a thousand minutes
                                time.sleep(1000 * 60)

                    # HELMET AND SLEEVE/SHOULDER NUMBERS
                    secondary_numbers = ["num07helmet.png", "num89helmet.png", "num07ss.png", "num89ss.png"]
                    if os.path.basename(file) in secondary_numbers:
                      numbers_filename = os.path.basename(file)
                      numbers_file = os.path.join(source_folder, os.path.basename(file))
                      
                      # determine if 07 or 89
                      if numbers_filename == "num07helmet.png" or numbers_filename == "num07ss.png":
                          numbers_main = "num07.png"
                      elif numbers_filename == "num89helmet.png" or numbers_filename == "num89ss.png":
                          numbers_main = "num89.png"
                      
                      # determine if helmet or ss
                      if numbers_filename == "num07helmet.png" or numbers_filename == "num89helmet.png":
                          numbers_type = "helmet"
                      elif numbers_filename == "num07ss.png" or numbers_filename == "num89ss.png":
                          numbers_type = "ss"
                      
                      #check if there is a specific texture provided for the helmet numbers
                      if os.path.exists(numbers_file):
                          new_file_name = f"{found_filename}.png"
                          # Put them in subfolders
                          num_folder_helmet = "nums-helmet"
                          num_folder_ss = "nums-shoulder"
                          if helmetnumbers_pref and numbers_type == "helmet":
                              if only_make_csv != "yes":
                                  if not os.path.exists(os.path.join(renamed_folder, num_folder_helmet)):
                                      os.makedirs(os.path.join(renamed_folder, num_folder_helmet))
                                  shutil.copy(numbers_file, os.path.join(renamed_folder, num_folder_helmet, new_file_name))
                              success_msg = "Texture renamed and filename added to the CSV file."
                              self.optional_textures_counter += 1
                          elif ssnumbers_pref and numbers_type == "ss":
                              if only_make_csv != "yes":
                                  if not os.path.exists(os.path.join(renamed_folder, num_folder_ss)):
                                      os.makedirs(os.path.join(renamed_folder, num_folder_ss))
                                  shutil.copy(numbers_file, os.path.join(renamed_folder, num_folder_ss, new_file_name))
                              success_msg = "Texture renamed and filename added to the CSV file."
                              self.optional_textures_counter += 1
                          else:
                              success_msg = "Filename added to the CSV file. No texture used."
                          # Write to the CSV file
                          csv_writer.writerow({'TEAM NAME': teamname, 'SLOT': slotname, 'TYPE': uniform_type, 'TEXTURE': file, 'FILENAME': new_file_name})
                          callback(f"{checkmark} ", "green")
                          callback(f"SUCCESS. {success_msg}\n")
                      
                      # If no helmet or sleeve/shoulder numbers are provided, use the main jersey numbers
                      else:
                          new_file_name = f"{found_filename}.png"
                          # Put them in subfolders
                          num_folder_helmet = "nums-helmet"
                          num_folder_ss = "nums-shoulder"
                          is_success = False
                          if helmetnumbers_pref and numbers_type == "helmet":
                              try:
                                  if only_make_csv != "yes":
                                      if not os.path.exists(os.path.join(renamed_folder, num_folder_helmet)):
                                          os.makedirs(os.path.join(renamed_folder, num_folder_helmet))
                                      shutil.copy(os.path.join(source_folder, numbers_main), os.path.join(renamed_folder, num_folder_helmet, new_file_name))
                                  success_msg = "Texture (used main numbers) renamed and filename added to the CSV file."
                                  self.optional_textures_counter += 1
                                  is_success = True
                              except FileNotFoundError:
                                  # Handle the FileNotFoundError gracefully
                                  callback(f"{Fore.RED}FileNotFoundError: {Style.RESET_ALL}File not found: {os.path.join(source_folder, source_image)}\n")
                                  success_msg = f"{Fore.RED}Message: {Style.RESET_ALL}The source file {source_image} is missing."
                          elif ssnumbers_pref and numbers_type == "ss":
                              try:
                                  if only_make_csv != "yes":
                                      if not os.path.exists(os.path.join(renamed_folder, num_folder_ss)):
                                          os.makedirs(os.path.join(renamed_folder, num_folder_ss))
                                      shutil.copy(os.path.join(source_folder, numbers_main), os.path.join(renamed_folder, num_folder_ss, new_file_name))
                                  success_msg = "Texture (used main numbers) renamed and filename added to the CSV file."
                                  self.optional_textures_counter += 1
                                  is_success = True
                              except FileNotFoundError:
                                  # Handle the FileNotFoundError gracefully
                                  callback(f"{Fore.RED}FileNotFoundError: {Style.RESET_ALL}File not found: {os.path.join(source_folder, source_image)}\n")
                                  success_msg = f"{Fore.RED}Message: {Style.RESET_ALL}The source file {source_image} is missing."
                          else:
                              success_msg = "Filename added to the CSV file. No texture used."
                          # Write to the CSV file
                          csv_writer.writerow({'TEAM NAME': teamname, 'SLOT': slotname, 'TYPE': uniform_type, 'TEXTURE': file, 'FILENAME': new_file_name})
                          if is_success:
                            callback(f"{checkmark} ", "green")
                            callback(f"SUCCESS. {success_msg}\n")
                          else:
                            callback(f"{success_msg}\n")

                    
                    # Everything else
                    elif file not in ["num07shadow.png", "num89shadow.png", "num07helmet.png", "num07ss.png", "num89helmet.png", "num89ss.png", "pridesticker.png", "glove.png", "glove-second.png", "glove-team-1.png", "glove-team-2.png", "glove-uni-1.png", "glove-uni-2.png", "glove-uni-1-second.png", "glove-uni-2-second.png"]:
                      if file in ["wrist_Half_Sleeve_Bk.png", "wrist_Half_Sleeve_Wt.png", "wrist_QB_Wrist_Bk.png", "wrist_QB_Wrist_Wt.png"]:
                          try:
                              # Copy from os.path.join(base_dir, "utils", reference_folder) for specific files
                              new_file_name = f"{found_filename}.png"
                              if only_make_csv != "yes":
                                  shutil.copy(os.path.join(default_textures_folder, source_image), os.path.join(renamed_folder, new_file_name))
                              # Write to the CSV file
                              csv_writer.writerow({'TEAM NAME': teamname, 'SLOT': slotname, 'TYPE': uniform_type, 'TEXTURE': file, 'FILENAME': new_file_name})
                              callback(f"{checkmark} ", "green")
                              callback(f"SUCCESS. Texture renamed and filename added to the CSV file.\n")
                              self.required_textures_counter += 1
                          except FileNotFoundError:
                              # Print error message
                              callback("\n")
                              callback(f"###########################################################\n")
                              callback(f"!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!\n", "red")
                              callback(f"!!! ERROR: ", "red")
                              callback(f"The {source_image} default textures is missing from:\n")
                              callback(f"{default_textures_folder}\n\n")
                              callback(f"You should re-install the app if you're not sure why it's missing.\n")
                              callback(f"!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!\n", "red")
                              callback(f"###########################################################\n")
                              # Delete the incomplete folder
                              if os.path.exists(renamed_folder):
                                  shutil.rmtree(renamed_folder)
                              # Pause for a thousand minutes
                              time.sleep(1000 * 60)
                      else:
                          try:
                              new_file_name = f"{found_filename}.png"
                              # Subfolders
                              if file == "16-Shoe.png":
                                  subfolder = "cleat-primary" 
                              elif file == "17-Shoe_w_White_Tape.png":
                                  subfolder = "cleat-alt1" 
                              elif file == "23-Shoe_w_Black_Tape.png":
                                  subfolder = "cleat-alt2" 
                              elif file == "24-Shoe_w_TC_Tape.png":
                                  subfolder = "cleat-alt3" 
                              else:
                                  subfolder = "" 
                              # Check if copying files or only making CSV
                              if only_make_csv != "yes":
                                  # Copy from source_folder for other files
                                  if not os.path.exists(os.path.join(renamed_folder, subfolder)):
                                      os.makedirs(os.path.join(renamed_folder, subfolder))
                                  shutil.copy(os.path.join(source_folder, source_image), os.path.join(renamed_folder, subfolder, new_file_name))
                              # Write to the CSV file
                              csv_writer.writerow({'TEAM NAME': teamname, 'SLOT': slotname, 'TYPE': uniform_type, 'TEXTURE': file, 'FILENAME': new_file_name})
                              callback(f"{checkmark} ", "green")
                              callback(f"SUCCESS. Texture renamed and filename added to the CSV file.\n")
                              self.required_textures_counter += 1
                          except FileNotFoundError:
                              # Print error message
                              callback("\n")
                              callback(f"###########################################################\n")
                              callback(f"!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!\n", "red")
                              callback(f"!!! ERROR: ", "red")
                              callback(f"The source file {source_image} is missing from YOUR_TEXTURES_HERE. Add the source file and try again.\n")
                              callback(f"!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!\n", "red")
                              callback(f"###########################################################\n")
                              # Delete the incomplete folder
                              if os.path.exists(renamed_folder):
                                  shutil.rmtree(renamed_folder)
                              # Pause for a thousand minutes
                              time.sleep(1000 * 60)


                # Check if there are multiple matches for this file only if it's not in the skip list
                if file not in skip_warn_multiple and file in multiple_matches_dict:
                    # callback("^^^^^ !!!! ERROR: MULTIPLE MATCHES !!!!  Try lowering the hash_tolerance and/or raising the ssim_threshold. Only one match is allowed for this texture. ^^^^^")
                    callback("^^^^^ !! MULTIPLE MATCHES !!  We used the one with the highest SSIM (similarity) value, so all should be okay, but you should keep an eye on this one in your testing. ^^^^^\n")
                elif file in skip_warn_multiple and file in multiple_matches_dict:
                    callback("^^^^^ Don't worry, two matches for this texture is okay. We used the correct one by comparing its filename to the other numbers. ^^^^^\n")
            
            
            def no_texture(file, file_data, similar_images):
                callback("\n")  # Add a line break 
                if file in ["glove-team-1.png", "glove-team-2.png"]:
                  if include_team_glove:
                    callback(f"###########################################################\n")
                    callback(f"!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!\n", "red")
                    callback(f"[•] ", "blue")
                    callback(f"==== NO similar images found for {file}. Are you sure the texture dumped? If so...try raising the hash_tolerance to 2 or more and/or lowering the ssim_threshold for this item in config.txt to broaden the search. Alternatively, you can replace the reference texture with the actual dumped texture for a definite match. ====\n")
                    callback(f"!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!\n", "red")
                    callback(f"###########################################################\n")
                  else:
                    callback(f"")
                elif file in ["17-Shoe_w_White_Tape.png"]:
                  callback(f"###########################################################\n")
                  callback(f"!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!\n", "red")
                  callback(f"[•] ", "blue")
                  callback(f"==== NO similar images found for {file}. Are you sure the texture dumped? If so...try raising the hash_tolerance to 2 or more and/or lowering the ssim_threshold for this item in config.txt to broaden the search. Alternatively, you can replace the reference texture with the actual dumped texture for a definite match. ====\n")
                  callback(f"!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!\n", "red")
                  callback(f"###########################################################\n")
                elif file in ["13-Sock.png"]:
                  callback(f"###########################################################\n")
                  callback(f"!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!\n", "red")
                  callback(f"[•] ", "blue")
                  callback(f"==== NO similar images found for {file}. Are you sure the texture dumped? If so...the light uniform's sock is a particularly troublesome texture. The only solution is go find the actual dumped texture in your dumps folder, and then add it to the ALTS-SOCK folder inside the REFERENCE-LIGHT directory (or, if a dark uniform, in the REFERENCE-DARK directory). You don't need to rename it. Also, please ping @JD637 on Discord with this sock texture attached so he can add it to the tool for others.  ====\n")
                  callback(f"!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!\n", "red")
                  callback(f"###########################################################\n")
                elif file in ["num07helmet.png", "num89helmet.png"]:
                  callback(f"[•] ", "blue")
                  callback(f"==== No similar images found for {file}. This is okay if helmet numbers are disabled in this uniform slot. ====\n")
                elif file in ["num07ss.png", "num89ss.png"]:
                  callback(f"[•] ", "blue")
                  callback(f" ==== No similar images found for {file}. This is okay if sleeve/shoulder numbers are disabled in this uniform slot. ====\n")
                else:
                  callback(f"###########################################################\n")
                  callback(f"!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!\n", "red")
                  callback(f"[•] ", "blue")
                  callback(f"==== NO similar images found for {file}. Are you sure the texture dumped? If so...try raising the hash_tolerance and/or lowering the ssim_threshold for this item in config.txt to broaden the search. Alternatively, you can copy the actual dumped texture into the ALTS folder inside the REFERENENCE-LIGHT/DARK and rename it {file} to ensure a match. ====\n")
                  callback(f"!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!\n", "red")
                  callback(f"###########################################################\n")

            
            
            
            #-----------------------------------------#
            # Iterate over the reference files to find matches in the dumps and perform the actions
            for file, file_data in reference_files.items():
                # If second gloves, only process "glove-uni-1-second.png" and "glove-uni-2-second.png" and skip all others
                if not glove_normal_or_csv:
                    if file not in ("glove-uni-1-second.png", "glove-uni-2-second.png"):
                        continue  # Skip processing any file that is not a second glove
                    # Process second glove
                    source_image = file_data["source"]
                    params = file_data if 'hash_tolerance' in file_data and 'ssim_threshold' in file_data else None
                    original_similar_images = find_similar_images(os.path.join(base_dir, "utils", reference_folder, source_image), dumps_path, params)
                    
                    if original_similar_images:
                        process_texture(file, file_data, original_similar_images, csv_writer=csv_writer, csv_writer_team=csv_writer_team)
                    else:
                        no_texture(file, file_data, original_similar_images)
                    continue  # Continue after processing second glove

                # Regular processing for other cases when glove_normal_or_csv is True
                source_image = file_data["source"]
                params = file_data if 'hash_tolerance' in file_data and 'ssim_threshold' in file_data else None
                original_similar_images = find_similar_images(os.path.join(base_dir, "utils", reference_folder, source_image), dumps_path, params)

                if file in ["num07shadow.png", "num89shadow.png"]:
                    if original_similar_images:
                        process_texture(file, file_data, original_similar_images, csv_writer=csv_writer, csv_writer_team=csv_writer_team)
                    else:
                        no_texture(file, file_data, original_similar_images)
                else:
                    if original_similar_images and len(original_similar_images) > 0:
                        # callback(f"DEBUG: Calling process_texture 01 #\n")
                        process_texture(file, file_data, [original_similar_images[0]], csv_writer=csv_writer, csv_writer_team=csv_writer_team)
                    else:
                        # Check alternates only when there are no similar images in the original check
                        if file in ["13-Sock.png"]:
                            alts_folder = "alts-sock"
                            alternate_source_directory = os.path.join(base_dir, "utils", reference_folder, alts_folder)

                            # Check if the alternate source directory exists
                            if os.path.exists(alternate_source_directory):
                                callback("\n")  # Add a line break
                                callback("\n")  # Add a line break
                                callback(f"↓↓↓↓↓↓↓ No match for {source_image}. Trying again using the reference images in the {alts_folder} folder\n")

                                # Get all PNG files in the alternate source directory
                                alternate_source_files = get_all_png_files_in_directory(alternate_source_directory)

                                for alternate_source_path in alternate_source_files:
                                    callback(f"at: {alternate_source_path}...\n")
                                    alternate_similar_images = find_similar_images(alternate_source_path, dumps_path, params, context=f"{alts_folder}")

                                    if alternate_similar_images:
                                        process_texture(file, file_data, [alternate_similar_images[0]], csv_writer=csv_writer, csv_writer_team=csv_writer_team)
                                        break  # Break out of the loop if a match is found

                                else:
                                    no_texture(file, file_data, alternate_similar_images)
                            else:
                                no_texture(file, file_data, original_similar_images)
                        else:
                            # Continue with the old way for other files
                            alts_folder = "alts"
                            alternate_source_path = os.path.join(base_dir, "utils", reference_folder, alts_folder, source_image)
                            if os.path.exists(alternate_source_path):
                                callback("\n")  # Add a line break 
                                callback("\n")  # Add a line break 
                                callback(f"↓↓↓↓↓↓↓ No match for {source_image}. Trying again using the reference image in the alts folder\n")
                                alternate_similar_images = find_similar_images(alternate_source_path, dumps_path, params, context=f"{alts_folder}")
                                callback(f"at: {alternate_source_path}...\n")
                          
                                if alternate_similar_images:
                                    process_texture(file, file_data, [alternate_similar_images[0]], csv_writer=csv_writer, csv_writer_team=csv_writer_team)
                                else:
                                    no_texture(file, file_data, alternate_similar_images)
                            else:
                                no_texture(file, file_data, original_similar_images)





        # Extract the first segment of uniform_slot_name
        if '-' in uniform_slot_name:
            renamed_subfolder0 = uniform_slot_name.split('-')[0]
        else:
            renamed_subfolder0 = uniform_slot_name

        # Extract the second segment of uniform_slot_name
        if '-' in uniform_slot_name:
            renamed_subfolder = uniform_slot_name.split('-')[1]
        else:
            renamed_subfolder = uniform_slot_name

        # Redefine the 'renamed' folder
        renamed_folder = os.path.join(base_dir, "RENAMED", renamed_subfolder0, renamed_subfolder)

        # Create csv subfolder if it doesn't exist
        if only_make_csv != "yes":
            if not os.path.exists(os.path.join(renamed_folder, "csv-texture-names")):
                os.makedirs(os.path.join(renamed_folder, "csv-texture-names"))
        
        if glove_normal_or_csv:
            # Move the CSV file to the 'renamed' folder
            if only_make_csv != "yes":
                shutil.move(csv_file_path, os.path.join(renamed_folder, "csv-texture-names", csv_filename))
                if include_team_glove:
                  shutil.move(teamgloves_csv_file_path, os.path.join(teamgloves_destination_folder, teamgloves_csv_filename))
            elif only_make_csv == "yes":
                shutil.move(csv_file_path, os.path.join(base_dir, "RENAMED", csv_filename))

            callback("\n")
            callback(f"{checkmark} CSV file copied to subfolder.\n")

            # # Put a copy of the CSV in the gathered-csv folder
            # # Create gathered-csv folder if it doesn't exist
            # if not os.path.exists(os.path.join(parent_dir, "gathered-csv")):
            #     os.makedirs(os.path.join(parent_dir, "gathered-csv"))
            # # Copy the CSV file to the 'gathered' folder
            # shutil.copy(os.path.join(renamed_folder, "csv-texture-names", csv_filename), os.path.join(parent_dir, "gathered-csv", csv_filename))

        callback("\n")  # Add a line break 
        callback("#--------------------------------------------------------------#\n")
        callback("#                                                              #\n")
        callback("#                                                              #\n")
        if glove_normal_or_csv and self.required_textures_counter < 32:
          callback(f"#                 ")
          callback(f"#!!!! DONE WITH ERRORS !!!!", "red")
          callback(f"#                   #\n")
          callback(f"#         Number of textures found and renamed: {self.required_textures_counter + self.optional_textures_counter}             #\n")
          callback(f"#                   Required: ")
          callback(f"{self.required_textures_counter}", "red")
          callback(f" of 32                         #\n")
        if glove_normal_or_csv and self.required_textures_counter > 31:
          callback(f"#                         ")
          callback(f"SUCCESS!", "green")
          callback(f"                             #\n")
          callback(f"#         Number of textures found and renamed: {self.required_textures_counter + self.optional_textures_counter}             #\n")
          if glove_normal_or_csv:
            callback(f"#                   Required:  ")
            callback(f"{self.required_textures_counter}", "green")
            callback(f" of 32                        #\n")
          else:
            callback(f"#                   Required:  \n")
            callback(f"{self.required_textures_counter}", "green")
            callback(f" of 1                         #\n")
        if glove_normal_or_csv:
          callback(f"#                    Optional: {self.optional_textures_counter} of 6                          #\n")
        if glove_normal_or_csv and self.required_textures_counter < 32:
          callback("#                                                              #\n")
          callback(f"#                ")
          callback(f"!!!!  SOMETHING WENT WRONG. !!!", "red")
          callback(f"               #\n")
          callback(f"#     ")
          callback(f"!!!!  {32 - self.required_textures_counter} of the required textures are missing.  !!!", "red")
          callback(f"       #\n")
        if not glove_normal_or_csv and self.required_textures_counter == 2:
          callback(f"#                         ")
          callback(f"SUCCESS!", "green")
          callback(f"                             #\n")
          callback(f"#         Number of textures found and renamed: {self.required_textures_counter + self.optional_textures_counter}              #\n")
          callback(f"#                   Required: ")
          callback(f"{self.required_textures_counter}", "green")
          callback(f" of 2                           #\n")
        if not glove_normal_or_csv and self.required_textures_counter < 2:
          callback("#                                                              #\n")
          callback(f"#                ")
          callback(f"!!!!  SOMETHING WENT WRONG. !!!", "red")
          callback(f"               #\n")
          callback(f"#     ")
          callback(f"!!!!  {1 - self.required_textures_counter} of the required textures are missing.  !!!", "red")
          callback(f"       #\n")
        callback("#                                                              #\n")
        callback("#       READ ALL OF THE OUTPUT ABOVE TO CHECK FOR ISSUES.      #\n")
        callback("#      Your renamed textures are in a subfolder of RENAMED.    #\n")
        callback("# The texture names were written to a CSV file in that folder. #\n")
        callback("#  Be sure to leave the CSV file in the folder and submit it   #\n")
        callback("#    with the uniform for easy future edits of this slot.      #\n")
        callback("#                                                              #\n")
        callback("################################################################\n")
        if glove_normal_or_csv and self.required_textures_counter > 31:
          callback("#                                                              #\n")
          callback(f"# !!   THE UNIFORM IS NOT DONE! DUMP THE OPPOSITE GLOVES.   !! #\n", "yellow")
          callback("#                                                              #\n")
          callback("################################################################\n")

        callback("\n")  # Add a line break 

        ############################################################################


        ############################################################################
        def find_duplicate_png_files(folder):
            png_files = {}
            for root, dirs, files in os.walk(folder):
                for file in files:
                    if file.lower().endswith('.png'):
                        file_path = os.path.join(root, file)
                        if file in png_files:
                            png_files[file].append(file_path)
                        else:
                            png_files[file] = [file_path]
            
            # Filter out files that don't have duplicates
            duplicate_sets = {file: sorted(paths) for file, paths in png_files.items() if len(paths) > 1}

            return duplicate_sets

        folder_to_check = os.path.join(base_dir, "RENAMED")
        duplicate_sets = find_duplicate_png_files(folder_to_check)

        # callback("Checking recursively in the RENAMED folder to ensure all filenames are unique...")
        # callback("\n")

        if duplicate_sets:
            callback("\n")
            callback(f"!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!\n", "red")
            callback("******  ")
            callback("WARNING: ", "red")
            callback("Duplicate texture names found!  *******\n")
            callback("*                                                      *\n")
            callback("*     You may have dumped the same uniform twice.      *\n")
            callback("*    Correct it and redump. No two files can have      *\n")
            callback("*        the same name anywhere in replacements.       *\n")
            callback("*                                                      *\n")
            for idx, (filename, paths) in enumerate(duplicate_sets.items(), start=1):
                callback(f"\nDuplicate Set {idx}:\n")
                for path in paths:
                    # Trim everything before "RENAMED"
                    try:
                        short_path = path[path.index("RENAMED"):]
                    except ValueError:
                        short_path = path
                    callback(f"• {short_path}")
                    callback("\n")  
            callback("\n")
            callback("\n")
            callback(f"!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!\n", "red")
            callback("******  ")
            callback("WARNING: ", "red")
            callback("Duplicate texture names found!  *******\n")
            callback("*                                                      *\n")
            callback("*     You may have dumped the same uniform twice.      *\n")
            callback("*    Correct it and redump. No two files can have      *\n")
            callback("*        the same name anywhere in replacements.       *\n")
            callback("*                                                      *\n")
            callback("********************************************************\n")
            callback(f"!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!\n", "red")
        else:
            # callback("Passed duplicate PNG files check. Ready for next round if no red errors above.\n")
            callback("✅ Passed duplicate PNG files check.\n")
            # callback("\n")
            # callback("REMEMBER TO DELETE YOUR DUMPS PRIOR TO DUMPING THE NEXT GAME.")





        ############################################################################
        def find_duplicate_items_in_csvs(folder):
            """
            Recursively checks all CSV files in `folder` for duplicate FILENAME values.
            Returns a dict mapping each duplicate filename to the list of CSVs where it appears.
            """

            # callback("\nStarting duplicate FILENAME check across all CSV files...\n\n")

            filename_map = {}  # key = FILENAME value, value = list of CSV paths

            for root, dirs, files in os.walk(folder):
                for file in files:
                    if not file.lower().endswith(".csv"):
                        continue

                    file_path = os.path.join(root, file)

                    try:
                        with open(file_path, "r", encoding="utf-8-sig", newline="") as f:
                            reader = csv.reader(f)
                            header = next(reader, None)

                            if not header:
                                continue

                            # Normalize headers
                            header = [h.strip().upper() for h in header]

                            if "FILENAME" not in header:
                                continue

                            filename_index = header.index("FILENAME")

                            # Extract all FILENAME values
                            for row in reader:
                                if len(row) <= filename_index:
                                    continue
                                val = row[filename_index].strip()
                                if val:
                                    filename_map.setdefault(val, []).append(file_path)

                    except Exception as e:
                        print(f"⚠️ Error reading {file_path}: {e}")
                        continue

            # Filter out entries that only occur once
            duplicate_sets = {file: sorted(paths) for file, paths in filename_map.items() if len(paths) > 1}

            return duplicate_sets





        base_dir = os.path.dirname(os.path.abspath(sys.argv[0]))
        folder_to_check = os.path.join(base_dir, "RENAMED")

        duplicate_sets = find_duplicate_items_in_csvs(folder_to_check)

        if duplicate_sets:
            callback("\n")
            callback(f"!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!\n", "red")
            callback("******  ")
            callback("WARNING: ", "red")
            callback("Duplicate FILENAME entries found in CSV files!  *******\n")
            callback("*                                                      *\n")
            callback("*          SEE BELOW FOR DETAILS                       *\n")
            callback("*                                                      *\n")
            callback("*     You may have dumped the same uniform twice.      *\n")
            callback("*    Correct it and redump. No two files can have      *\n")
            callback("*        the same name anywhere in replacements.       *\n")
            callback("*                                                      *\n")
            callback("********************************************************\n")

            for idx, (filename, paths) in enumerate(duplicate_sets.items(), start=1):
                callback(f"\nDuplicate Set {idx}:\n")
                callback(f"Filename: {filename}\n")
                for path in paths:
                    # Trim everything before "RENAMED"
                    try:
                        short_path = path[path.index("RENAMED"):]
                    except ValueError:
                        short_path = path
                    callback(f"• {short_path}")
                    callback("\n")

            callback("\n")
            callback("******  ")
            callback("WARNING: ", "red")
            callback("Duplicate FILENAME entries found in CSV files!  *******\n")
            callback("*                                                      *\n")
            callback("*              SEE ABOVE FOR DETAILS                   *\n")
            callback("*                                                      *\n")
            callback("*     You may have dumped the same uniform twice.      *\n")
            callback("*    Correct it and redump. No two files can have      *\n")
            callback("*        the same name anywhere in replacements.       *\n")
            callback("*                                                      *\n")
            callback("********************************************************\n")
            callback(f"!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!\n", "red")

        else:
            callback("✅ Passed CSV FILENAME duplicate check.\n")
            callback("Ready for next round if no red errors above.\n")
            callback("\n")
            callback("REMEMBER TO DELETE YOUR DUMPS PRIOR TO DUMPING THE NEXT GAME.\n")



# Create an instance of DumpsFinder
dumps_finder = DumpsFinder()