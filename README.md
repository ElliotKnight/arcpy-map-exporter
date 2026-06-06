# ArcGIS Map Exporter

Automatically exports one map per feature layer from an ArcGIS Pro layout, with configurable labels, zoom, filtering, and output options.

# Requirements

- ArcGIS Pro
- Run from the ArcGIS Pro Python console or as a script tool (`arcpy` must be available if not running on ArcGIS Pro)

# Setup

1. Open your ArcGIS Pro project and set up your layout (`Layout1` by default)
2. Copy `map_exporter.py` into your project folder
3. Edit the Configuration block at the top of the script
4. Run from the ArcGIS Pro Python window:
   ```python
   exec(open(r"path\to\map_exporter.py").read())
   ```

# Configuration reference

All settings are in the `CONFIGURATION` section at the top of the script. Nothing below that line needs to be changed.

# Output


 `out_folder` Folder where exports are saved. Created automatically if it doesn't exist.

# Labels


 `zoom_out_factor` ie `1.5` Multiplier applied to the scale after fitting the layer extent. `1.0` = tight fit, `2.0` = double the scale (more context). 

# Layer filtering


`include_layers` | `[]` | If non-empty, only export layers whose names are in this list. 
`exclude_layers` | `[]` | Skip layers whose names are in this list. Ignored if `include_layers` is set. 
`background_layers` | `[]` | Layers that stay permanently visible on every export (e.g. a boundary or coastline). Never exported as their own file. 

# Export format & quality

 `export_formats` | `["PDF"]` | Any combination of `"PDF"`, `"PNG"`, `"TIFF"`. 
 `export_dpi` | `150` | Resolution in DPI. `96` = screen, `150` = general, `300` = print. 

# File management

`overwrite_existing` | `False` | `False` skips a file if it already exists; `True` overwrites. 
`filename_prefix` | `"auto"` | Prepended to every filename. `"auto"` uses today's date (`2026-06-06_`), `""` for none, or any custom string. 

# Combined PDF


`combine_pdf` | `True` | After individual exports, stitch all PDFs into one multi-page document. Requires `"PDF"` in `export_formats`. 
`combined_pdf_name` | `"Combined_All_Layers.pdf"` | Filename for the combined document (prefix is also applied). 


#