import os, re, traceback, shutil
import pandas as pd
from collections import defaultdict
from datetime import datetime
from openpyxl import load_workbook
from openpyxl.styles import PatternFill
from django.conf import settings
import os, re, traceback, shutil

def is_file_locked(filepath):
    if not os.path.exists(filepath):
        return False
    try:
        with open(filepath, 'a'):
            return False
    except OSError:
        return True
    
# Helper functions
def normalize_text(text):
    return re.sub(r'[^a-zA-Z0-9]', '', str(text)).strip().lower()

def extract_date_from_filename(filename):
    match = re.search(r'\.(\d{4}-\d{2}-\d{2})\.', filename)
    if match:
        try:
            return datetime.strptime(match.group(1), "%Y-%m-%d")
        except ValueError:
            return None
    return None

def categorize_files(folder_path):
    single_version_files = {}
    multi_version_files = defaultdict(list)

    for root, dirs, files in os.walk(folder_path):
        for file in files:
            parts = file.split('.')

            # Type 1: Exactly 3 parts — configtype.configname.dateformat.hrl
            if len(parts) == 4:
                config_name = parts[1]

            # Type 2: More than 3 parts — configtype.configname.part1.part2...dateformat.hrl
            elif len(parts) > 4:
                config_name = '.'.join(parts[1:-3])  # Join all between config type and date

            else:
                continue  # Skip invalid files

            normalized_config_name = normalize_text(config_name)
            # print(f"🔍 Processing with normalized config name: {normalized_config_name}")

            if normalized_config_name in single_version_files:
                multi_version_files[normalized_config_name].append(file)
                multi_version_files[normalized_config_name].append(single_version_files.pop(normalized_config_name)[0])
            elif normalized_config_name in multi_version_files:
                multi_version_files[normalized_config_name].append(file)
            else:
                single_version_files[normalized_config_name] = [file]

    return single_version_files, multi_version_files

def find_matching_file(config_name, single_version_files, multi_version_files, selected_version):
    if "&" in config_name:
        config_name = config_name.replace("&", "and")
    normalized_key = normalize_text(config_name)
    # print(f"🔍 Looking for matches for: {normalized_key} | Version: {selected_version}")

    if normalized_key in single_version_files:
        #print(f"✅ Single-version match found: {single_version_files[normalized_key][0]}")
        return [single_version_files[normalized_key][0]]

    elif normalized_key in multi_version_files:
        candidates = multi_version_files[normalized_key]
        dated = [(f, extract_date_from_filename(f)) for f in candidates]
        dated.sort(key=lambda x: (x[1] or datetime.min))

        if selected_version == 'latest':
            print(f"✅ Latest version selected: {dated[-1][0]}")
            return [dated[-1][0]]
        elif selected_version == 'oldest':
            print(f"✅ Oldest version selected: {dated[0][0]}")
            return [dated[0][0]]
        else:
            print(f"✅ All versions selected: {[f for f, _ in dated]}")
            return [f for f, _ in dated]
    
    print("❌ No match found.")
    return []


def safe_create_folder(path):
    try:
        # print(f"Checking if file: {os.path.isfile(path)}")
        # print(f"Checking if dir : {os.path.isdir(path)}")
        # print(f"Can write to parent: {os.access(os.path.dirname(path), os.W_OK)}")
        
        if os.path.exists(path):
            if os.path.isfile(path):
                raise PermissionError(f"Expected directory but found file: {path}")
            # print(f"Folder already exists: {path}")
        else:
            os.makedirs(path, exist_ok=True)
            # print(f"Folder created successfully: {path}")
    except PermissionError as e:
        print(f"Permission denied error when creating folder: {path}")
        print(traceback.format_exc())
        raise
    except Exception as e:
        print(f"Unexpected error when creating folder: {path}")
        print(traceback.format_exc())
        raise


def find_column_name(headers, target_name):
    target_norm = target_name.strip().lower()
    for h in headers:
        if h and h.strip().lower() == target_norm:
            return h
    raise ValueError(f"Column '{target_name}' not found")

print("🔧 process_hrl_files loaded from utils.py ✅")
def process_hrl_files(excel_path, upload_folder, version_choice, progress_callback=None):
    import traceback
    import time
    import threading
    from openpyxl import load_workbook
    import pandas as pd
    from .utils import normalize_text, categorize_files, find_matching_file
    import os
    from openpyxl.styles import PatternFill

    def smooth_progress(start=0, end=100, duration=30):
        steps = end - start
        interval = duration / steps if steps else 0.3
        def run():
            for i in range(start, end + 1):
                if progress_callback:
                    progress_callback(i)
                time.sleep(interval)
        threading.Thread(target=run, daemon=True).start()

    try:
        print("🔍 ENTERED process_hrl_files")

        from django.conf import settings
        from datetime import datetime

        # Start smooth progress bar
        smooth_progress(0, 100, duration=30)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        HRL_PARENT_FOLDER = os.path.join(settings.MEDIA_ROOT, f"HRLS_{timestamp}")
        os.makedirs(HRL_PARENT_FOLDER, exist_ok=True)

        print("📘 Loading Excel file:", excel_path)
        wb = load_workbook(excel_path)
        print("✅ Workbook loaded")

        ws_main = wb["Main"]
        ws_bal = wb["Business Approved List"]

        df_bal = pd.read_excel(
            excel_path,
            sheet_name="Business Approved List",
            dtype=str,
            keep_default_na=False,
            na_filter=False
        )
        df_bal.columns = df_bal.columns.str.strip()

        print("📄 df_bal shape:", df_bal.shape)
        print("🧾 df_bal columns:", df_bal.columns.tolist())

        col_map = {col.strip().lower(): col for col in df_bal.columns}
        required_keys = {
            "hrl available?": None,
            "file name is correct in export sheet": None
        }

        for key in required_keys:
            actual_col = col_map.get(key.lower())
            if not actual_col:
                raise Exception(f"Missing required column in Excel sheet: {key}")
            required_keys[key] = actual_col

        print("🔑 Mapped required columns:", required_keys)

        hrl_col = required_keys["hrl available?"]
        file_name_col = required_keys["file name is correct in export sheet"]

        df_bal["Config Type"] = df_bal["Config Type"].astype(str).apply(normalize_text)
        approved_config_types = set(df_bal["Config Type"].dropna().unique())

        config_root_path = os.path.join(settings.MEDIA_ROOT, "configs")
        available_folders = {
            normalize_text(f): os.path.join(config_root_path, f)
            for f in os.listdir(config_root_path)
            if os.path.isdir(os.path.join(config_root_path, f))
        }
        selected_folders = {
            k: v for k, v in available_folders.items() if k in approved_config_types
        }

        print("📁 Selected folders:", selected_folders)
        print("🔁 Starting config type loop:", list(selected_folders.keys()))

        ws_main.delete_rows(2, ws_main.max_row)
        for config_type, folder_path in selected_folders.items():
            uploaded_files = [f for f in os.listdir(folder_path) if os.path.isfile(os.path.join(folder_path, f))]
            ws_main.append([config_type, len(uploaded_files), "Pending", "Pending"])

        for config_type, folder_path in selected_folders.items():
            print(f"🔧 Processing config_type: {config_type}")
            single_version_files, multi_version_files = categorize_files(folder_path)
            config_type_rows = df_bal[df_bal["Config Type"] == config_type]

            for index, row in config_type_rows.iterrows():
                config_name = row.get("Config Name")
                if pd.isna(config_name) or not str(config_name).strip():
                    continue

                print(f"🔍 Row {index} - config name: {config_name}")
                matches = find_matching_file(config_name, single_version_files, multi_version_files, version_choice)
                matches = list({os.path.basename(m): m for m in matches}.values())

                try:
                    if matches:
                        df_bal.at[index, hrl_col] = "HRL Found"
                        for match in matches:
                            src = os.path.join(folder_path, match)
                            tgt_folder = os.path.join(HRL_PARENT_FOLDER, config_type)
                            os.makedirs(tgt_folder, exist_ok=True)
                            tgt = os.path.join(tgt_folder, match)
                            shutil.copy2(src, tgt)

                            existing_val = str(df_bal.at[index, file_name_col]) if pd.notna(df_bal.at[index, file_name_col]) else ""
                            new_val = os.path.relpath(src, upload_folder)
                            df_bal.at[index, file_name_col] = (existing_val + f", {new_val}").strip(", ")
                    else:
                        df_bal.at[index, hrl_col] = "Not Found"
                except Exception as e:
                    print(f"❌ Failed HRL update at row {index}: {e}")
                    traceback.print_exc()

        ws_bal.delete_rows(2, ws_bal.max_row)
        for col_idx, col_name in enumerate(df_bal.columns, start=1):
            ws_bal.cell(row=1, column=col_idx, value=col_name)

        for r_idx, row in df_bal.iterrows():
            for c_idx, val in enumerate(row):
                ws_bal.cell(row=r_idx + 2, column=c_idx + 1, value=str(val))

        filtered_excel_path = os.path.join(HRL_PARENT_FOLDER, os.path.basename(excel_path))
        wb.save(filtered_excel_path)
        wb.close()

        print("✅ Returning filtered Excel path:", filtered_excel_path)
        return filtered_excel_path

    except Exception as e:
        print("❌ Exception in process_hrl_files root:", str(e))
        traceback.print_exc()
        if progress_callback:
            progress_callback(-1)
        raise


