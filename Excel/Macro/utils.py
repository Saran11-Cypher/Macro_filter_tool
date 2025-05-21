import os, re, traceback, shutil
import pandas as pd
from collections import defaultdict
from datetime import datetime
from openpyxl import load_workbook
from openpyxl.styles import PatternFill
from django.conf import settings
import os

def is_file_locked(excel_path):
    try:
        os.rename(excel_path, excel_path)
        return False
    except OSError:
        return True

def normalize_text(text):
    return re.sub(r'[^a-zA-Z0-9.]', '', str(text)).strip().lower()

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
            if len(parts) >= 3:
                config_name = parts[1]
            else:
                continue
            normalized = normalize_text(config_name)
            if normalized in single_version_files:
                multi_version_files[normalized].append(file)
                multi_version_files[normalized].append(single_version_files.pop(normalized)[0])
            elif normalized in multi_version_files:
                multi_version_files[normalized].append(file)
            else:
                single_version_files[normalized] = [file]
    return single_version_files, multi_version_files

def find_matching_file(config_name, single_version_files, multi_version_files, selected_version):
    if "&" in config_name:
        config_name = config_name.replace("&", "and")
    normalized_key = normalize_text(config_name)

    if normalized_key in single_version_files:
        return [single_version_files[normalized_key][0]]
    elif normalized_key in multi_version_files:
        candidates = multi_version_files[normalized_key]
        dated = [(f, extract_date_from_filename(f)) for f in candidates]
        dated.sort(key=lambda x: (x[1] or datetime.min))
        if selected_version == 'latest':
            return [dated[-1][0]]
        elif selected_version == 'oldest':
            return [dated[0][0]]
        else:
            return [f for f, _ in dated]
    return []

def safe_create_folder(path):
    try:
        print(f"Attempting to create folder: {path}")
        if os.path.exists(path):
            print(f"Folder already exists: {path}")
        else:
            os.makedirs(path, exist_ok=True)
            print(f"Folder created successfully: {path}")
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

def process_hrl_files(excel_path, upload_folder, version_choice):
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    HRL_PARENT_FOLDER = os.path.join(settings.MEDIA_ROOT, f"HRLS_{timestamp}")
    try:
        safe_create_folder(HRL_PARENT_FOLDER)
    except Exception as e:
        print(f"Failed to create HRL output folder: {str(e)}")
        raise
    wb = load_workbook(excel_path)
    try:
        ws_main = wb["Main"]
        ws_bal = wb["Business Approved List"]
        df_bal = pd.read_excel(excel_path, sheet_name="Business Approved List", dtype=str)
        df_bal["Config Type"] = df_bal["Config Type"].astype(str).apply(normalize_text)
        # 🛠️ Ensure required columns are present
        for col in ["HRL Available?", "File Name is correct in Export Sheet"]:
            if col not in df_bal.columns:
                df_bal[col] = ""
        approved_config_types = set(df_bal["Config Type"].dropna().unique())

        # Find exact column names dynamically
        headers = [cell.value for cell in next(ws_bal.iter_rows(min_row=1, max_row=1))]
        file_name_col = find_column_name(headers, "File Name is correct in Export Sheet")
        hrl_available_col = find_column_name(headers, "HRL Available?")

        # Prepare available folders and filter for approved config types
        available_folders = {
            normalize_text(f): os.path.join(upload_folder, f)
            for f in os.listdir(upload_folder) if os.path.isdir(os.path.join(upload_folder, f))
        }
        selected_folders = {cfg: path for cfg, path in available_folders.items() if cfg in approved_config_types}

        config_load_order = [
            "ValueList", "AttributeType", "UserDefinedTerm", "LineOfBusiness", "Product", "ServiceCategory",
            "BenefitNetwork", "NetworkDefinitionComponent", "BenefitPlanComponent", "WrapAroundBenefitPlan",
            "BenefitPlanRider", "BenefitPlanTemplate", "Account", "BenefitPlan", "AccountPlanSelection"
        ]

        df_bal["Order"] = df_bal["Config Type"].apply(lambda x: config_load_order.index(x) if x in config_load_order else -1)
        df_bal = df_bal.sort_values("Order").drop(columns=["Order"])

        for config_type, folder_path in selected_folders.items():
            uploaded_files = [f for f in os.listdir(folder_path) if os.path.isfile(os.path.join(folder_path, f))]
            ws_main.append([config_type, len(uploaded_files), "Pending", "Pending", "Pending"])

        for config_type, folder_path in selected_folders.items():
            single_version_files, multi_version_files = categorize_files(folder_path)
            config_type_rows = df_bal[df_bal["Config Type"] == config_type]

            for index, row in config_type_rows.iterrows():
                config_name = row["Config Name"]
                if pd.isna(config_name) or not str(config_name).strip():
                    continue

                matches = find_matching_file(config_name, single_version_files, multi_version_files, version_choice)
                if matches:
                    df_bal.at[index, "HRL Available?"] = "HRL Found"
                    for match in matches:
                        src = os.path.join(folder_path, match)
                        tgt_folder = os.path.join(HRL_PARENT_FOLDER, config_type)
                        try:
                            safe_create_folder(tgt_folder)
                        except Exception as e:
                            print(f"Failed to create target folder {tgt_folder}: {str(e)}")
                            raise
                        tgt = os.path.join(tgt_folder, match)
                        print(f"Copying '{src}' to '{tgt}'")
                        try:
                            shutil.copy2(src, tgt)
                        except PermissionError:
                            print(f"Permission denied copying '{src}' to '{tgt}'")
                            raise
                        except Exception as e:
                            print(f"Error copying '{src}' to '{tgt}': {str(e)}")
                            raise

                        current_value = df_bal.at[index, "File Name is correct in Export Sheet"]
                        relative_src = os.path.relpath(src, upload_folder)
                        if pd.isna(current_value) or not current_value:
                            df_bal.at[index, "File Name is correct in Export Sheet"] = relative_src
                        else:
                            df_bal.at[index, "File Name is correct in Export Sheet"] += f", {relative_src}"
                else:
                    df_bal.at[index, "HRL Available?"] = "Not Found"
        # Write df_bal back to workbook
        for r_idx, row in df_bal.iterrows():
            for c_idx, val in enumerate(row):
                ws_bal.cell(row=r_idx + 2, column=c_idx + 1, value=str(val))

        # Apply coloring
        red = PatternFill(start_color='FFC7CE', end_color='FFC7CE', fill_type='solid')
        green = PatternFill(start_color='C6EFCE', end_color='C6EFCE', fill_type='solid')
        blue = PatternFill(start_color='BDD7EE', end_color='BDD7EE', fill_type='solid')

        header = [h.strip().lower() if h else "" for h in headers]
        config_type_col = header.index("config type") + 1
        config_name_col = header.index("config name") + 1

        for row in range(2, ws_bal.max_row + 1):
            raw_cfg_type = ws_bal.cell(row=row, column=config_type_col).value
            raw_cfg_name = ws_bal.cell(row=row, column=config_name_col).value
            cfg_type = normalize_text(raw_cfg_type) if raw_cfg_type else ""
            cfg_name = normalize_text(raw_cfg_name) if raw_cfg_name else ""
    
            if cfg_type in selected_folders:
                single, multi = categorize_files(selected_folders[cfg_type])
                version_files = multi.get(cfg_name, []) + single.get(cfg_name, [])
                versions = len(version_files)
                
                cell = ws_bal.cell(row=row, column=config_name_col)
                if versions == 0:
                    cell.fill = red  # Not found
                elif versions == 1:
                    cell.fill = red  # Only one version
                elif versions == 2:
                    cell.fill = green  # Two versions
                else:
                    cell.fill = blue  # More than two

        print(f"Saving Excel file: {excel_path}")
        
        if is_file_locked(excel_path):
            raise PermissionError(f"Cannot overwrite Excel file: {excel_path} is currently in use.")
        else:
            wb.save(excel_path)
        print(f"Checking path: {HRL_PARENT_FOLDER}")
        print("Is folder:", os.path.isdir(HRL_PARENT_FOLDER))
        print("Is file:", os.path.isfile(HRL_PARENT_FOLDER))
        print("Permissions:", os.access(HRL_PARENT_FOLDER, os.W_OK))
    finally: 
        wb.close()

    return HRL_PARENT_FOLDER