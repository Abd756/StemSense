import os
import json
import zipfile
from datetime import datetime
from config import EXPORT_DIR

class Packager:
    def __init__(self, output_dir=EXPORT_DIR):
        """
        The Packager handles the final step: bundling stems, metadata, and 
        the original track into a professional ZIP package.
        """
        self.output_dir = output_dir
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)

    def create_package(self, track_name, original_file, stems_dir, analysis_data):
        """
        Bundles everything into a single ZIP file.
        
        Args:
            track_name (str): The name of the track.
            original_file (str): Path to the original audio file.
            stems_dir (str): Path to the folder containing stems.
            analysis_data (dict): Dictionary with BPM, Key, Loudness info.
            
        Returns:
            str: Path to the generated ZIP file.
        """
        # 1. Clean up the track name for use in a filename
        clean_name = track_name.replace(" ", "_").replace("/", "-")
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        zip_filename = f"StemSense_{clean_name}_{timestamp}.zip"
        zip_path = os.path.join(self.output_dir, zip_filename)

        print(f"Creating package: {zip_filename}")

        try:
            with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                # 2. Add the original audio file
                if os.path.exists(original_file):
                    # arcname is how the file appears inside the ZIP
                    zipf.write(original_file, arcname=f"00_Original_{os.path.basename(original_file)}")
                
                # 3. Add all stems found in the stems directory
                if os.path.exists(stems_dir):
                    for stem_file in os.listdir(stems_dir):
                        stem_path = os.path.join(stems_dir, stem_file)
                        if os.path.isfile(stem_path):
                            # We put stems in their own folder inside the ZIP
                            zipf.write(stem_path, arcname=f"Stems/{stem_file}")
                
                # 4. Create and add the metadata.json
                # This makes the results readable by other programs or users
                metadata_path = os.path.join(self.output_dir, f"{clean_name}_metadata.json")
                with open(metadata_path, 'w') as f:
                    json.dump(analysis_data, f, indent=4)
                
                zipf.write(metadata_path, arcname="metadata.json")
                
                # Cleanup the temporary metadata file after zipping
                os.remove(metadata_path)

            print(f"Package created successfully: {zip_path}")
            return zip_path

        except Exception as e:
            print(f"Error during packaging: {e}")
            return None
