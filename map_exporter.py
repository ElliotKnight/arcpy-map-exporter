import arcpy
import os
import re
from datetime import date

# 1. Configuration

# --- Insert output folder ---
out_folder = # r"C:\Users\Documents\Yourfilepath"
layout_name = "Layout1"

# --- Label toggle ---
# True  = show labels on each export
# False = hide labels on each export
show_labels = True

# --- Zoom ---
# How far to zoom out after fitting the layer's extent.
# 1.0 = tight fit | 1.5 = 50% out | 2.0 = double the scale
zoom_out_factor = 1.5

# --- Layer filter ---
# INCLUDE: export only these layers (leave empty to export all).
include_layers = []
# Example: include_layers = ["Rivers", "Flood Zones"]

# EXCLUDE: skip these layers (only used when include_layers is empty).
exclude_layers = []
# Example: exclude_layers = ["Draft Layer", "Basemap Overlay"]

# --- Background layers ---
# These layers stay permanently visible on every export for geographic context.
# They are never toggled off and are not exported as their own PDF.
background_layers = []
# Example: background_layers = ["Country Boundary", "Coastline"]

# --- Export format ---
# Any combination of "PDF", "PNG", "TIFF"
export_formats = ["PDF"]
# Example: export_formats = ["PDF", "PNG"]

# --- Resolution ---
# 96  = screen | 150 = general purpose | 300 = print quality
export_dpi = 150

# --- Overwrite protection ---
# False = skip a layer if its output file already exists
# True  = overwrite any existing files
overwrite_existing = False

# --- Filename prefix ---
# Text prepended to every output filename.
# "auto" = today's date (e.g. "2026-06-06_Rivers.pdf")
# ""     = no prefix
filename_prefix = "auto"
# Example: filename_prefix = "Eden_Project"

# --- Combined PDF ---
# If True (and "PDF" is in export_formats), all maps are stitched into one
# multi-page PDF after the individual exports complete.
combine_pdf = True
combined_pdf_name = "Combined_All_Layers.pdf"

# -------- SCRIPT -------- Do not edit below this line

if filename_prefix == "auto":
    filename_prefix = date.today().strftime("%Y-%m-%d_")

os.makedirs(out_folder, exist_ok=True)

aprx = arcpy.mp.ArcGISProject("CURRENT")
layouts = aprx.listLayouts(layout_name)

if not layouts:
    print(f"Error: Could not find a layout named '{layout_name}'. Check spelling/.")
else:
    lyt = layouts[0]
    map_frames = lyt.listElements("MAPFRAME_ELEMENT")

    if not map_frames:
        print("Error: Could not find a Map Frame on the layout.")
    else:
        mf = map_frames[0]
        m = mf.map

        all_feature_layers = [lyr for lyr in m.listLayers() if lyr.isFeatureLayer]

        # Split out background layers
        bg_layers = [lyr for lyr in all_feature_layers if lyr.name in background_layers]
        not_found_bg = [n for n in background_layers if n not in {lyr.name for lyr in all_feature_layers}]
        if not_found_bg:
            print(f"Error: These background_layers names were not found in the map: {not_found_bg}")

        # (Candidate layers are everything that isn't a background layer)
        candidate_layers = [lyr for lyr in all_feature_layers if lyr.name not in background_layers]

        # Apply include / exclude filter
        if include_layers:
            export_layers = [lyr for lyr in candidate_layers if lyr.name in include_layers]
            not_found = [n for n in include_layers if n not in {lyr.name for lyr in candidate_layers}]
            if not_found:
                print(f"Error: These include_layers names were not found: {not_found}")
        elif exclude_layers:
            export_layers = [lyr for lyr in candidate_layers if lyr.name not in exclude_layers]
        else:
            export_layers = candidate_layers

        if not export_layers:
            print("No layers matched the current filter settings. Nothing to export.")
        else:
            # Validate formats
            valid_formats = {"PDF", "PNG", "TIFF"}
            export_formats_clean = [f.upper() for f in export_formats if f.upper() in valid_formats]
            invalid_formats = [f for f in export_formats if f.upper() not in valid_formats]
            if invalid_formats:
                print(f"Error: Unrecognised export formats ignored: {invalid_formats}")
            if not export_formats_clean:
                print("Error: No valid export formats specified. Use 'PDF', 'PNG', or 'TIFF'.")
            else:
                # Print run summary
                print(f"Layers to export : {len(export_layers)}")
                print(f"Formats          : {', '.join(export_formats_clean)}")
                print(f"DPI              : {export_dpi}")
                print(f"Labels           : {show_labels}")
                print(f"Zoom out factor  : {zoom_out_factor}")
                print(f"Overwrite        : {overwrite_existing}")
                print(f"Filename prefix  : '{filename_prefix}' (empty = none)")
                if bg_layers:
                    print(f"Background layers: {[lyr.name for lyr in bg_layers]}")
                print()

                # Turns all feature layers off
                print("Turning off all layers...")
                for lyr in all_feature_layers:
                    lyr.visible = False

                # Turn background layers on so they stay on for every export
                for lyr in bg_layers:
                    lyr.visible = True
                    lyr.showLabels = show_labels

                exported_pdfs = []

                print(f"Starting automated export to {out_folder}...\n")

                for i, layer in enumerate(export_layers, 1):
                    layer.visible = True
                    layer.showLabels = show_labels

                    layer_extent = mf.getLayerExtent(layer, False, True)
                    mf.camera.setExtent(layer_extent)
                    mf.camera.scale = mf.camera.scale * zoom_out_factor

                    safe_name = re.sub(r'[\\/*?:"<>|]', "", layer.name).strip()
                    base_name = f"{filename_prefix}{safe_name}"

                    print(f"  [{i}/{len(export_layers)}] {layer.name}")

                    for fmt in export_formats_clean:
                        out_path = os.path.join(out_folder, f"{base_name}.{fmt.lower()}")

                        if not overwrite_existing and os.path.exists(out_path):
                            print(f"    Skipped {fmt} — file already exists")
                            if fmt == "PDF":
                                exported_pdfs.append(out_path)
                            continue

                        if fmt == "PDF":
                            lyt.exportToPDF(out_path, resolution=export_dpi)
                            exported_pdfs.append(out_path)
                        elif fmt == "PNG":
                            lyt.exportToPNG(out_path, resolution=export_dpi)
                        elif fmt == "TIFF":
                            lyt.exportToTIFF(out_path, resolution=export_dpi)

                        print(f"    Saved {fmt}: {base_name}.{fmt.lower()}")

                    layer.visible = False

                # Restore background layers to off
                for lyr in bg_layers:
                    lyr.visible = False

                # Combine all PDFs into one multi-page document
                if combine_pdf and "PDF" in export_formats_clean:
                    if exported_pdfs:
                        combined_path = os.path.join(out_folder, f"{filename_prefix}{combined_pdf_name}")
                        print(f"\nCombining {len(exported_pdfs)} PDFs → {filename_prefix}{combined_pdf_name}...")
                        pdf_doc = arcpy.mp.PDFDocumentCreate(combined_path)
                        for pdf_path in exported_pdfs:
                            pdf_doc.appendPages(pdf_path)
                        pdf_doc.saveAndClose()
                        print(f"Combined PDF saved: {combined_path}")
                    else:
                        print("\nNote: No PDFs were produced — combined PDF skipped.")
                elif combine_pdf and "PDF" not in export_formats_clean:
                    print("\nNote: combine_pdf is True but PDF is not in export_formats — combined PDF skipped.")

                print(f"\nExport complete! {len(export_layers)} layers processed.")
                print(f"Output: {out_folder}")
