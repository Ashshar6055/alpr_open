readme = """
# ALPR Project - OpenALPR + OpenCV + API Dashboard

This project detects number plates using OpenALPR and OpenCV,
supports IP camera feeds, and optionally integrates with a
vehicle management dashboard (add/mark).

## Usage

- Set `USE_VIDEO_FILE` or IP cam URL
- Choose `USE_API = True/False`
- Switch between `"add"` and `"mark"` modes

## API Endpoints

- Add: http://seedoai.mietjmu.in/api/v1/vehicle/add
- Mark: http://seedoai.mietjmu.in/api/v1/vehicle/mark

Built for Indian number plates 🇮🇳
"""
with open("alpr_openalpr_project/README.md", "w") as f:
    f.write(readme)
