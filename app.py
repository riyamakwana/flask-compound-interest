from datetime import datetime
import pandas as pd
from flask import Flask, request, send_file
import os

app = Flask(__name__)

UPLOAD_FOLDER = "uploads"
if not os.path.exists(UPLOAD_FOLDER):
 os.makedirs(UPLOAD_FOLDER)

@app.route("/", methods=["GET", "POST"])
def upload_file():
 if request.method == "POST":
     file = request.files["file"]
     if file.filename == "":
         return "No file selected!"

     filepath = os.path.join(UPLOAD_FOLDER, file.filename)
     file.save(filepath)

     # Process the Excel file
     output_file = calculate_compound_interest(filepath)
     
     return send_file(output_file, as_attachment=True)

 return '''
 <!doctype html>
 <html>
 <body>
     <h2>Upload Excel File</h2>
     <form action="/" method="post" enctype="multipart/form-data">
         <input type="file" name="file">
         <input type="submit" value="Upload and Process">
     </form>
 </body>
 </html>
 '''

def calculate_compound_interest(filepath):
 df = pd.read_excel(filepath)

 expected_columns = {"Principal", "Rate", "StartDate", "MaturityDate", "CompoundsPerYear"}
 if not expected_columns.issubset(df.columns):
     return "Error: Excel must have Principal, Rate, StartDate, MaturityDate, and CompoundsPerYear columns."

 # Convert dates to datetime format
 df["StartDate"] = pd.to_datetime(df["StartDate"])
 df["MaturityDate"] = pd.to_datetime(df["MaturityDate"])

 # Calculate time in years (t)
 df["Time"] = (df["MaturityDate"] - df["StartDate"]).dt.days / 365.25

 # Apply compound interest formula
 df["Amount"] = df.apply(
     lambda row: row["Principal"] * (1 + row["Rate"] / row["CompoundsPerYear"]) ** (row["CompoundsPerYear"] * row["Time"]),
     axis=1
 )

 output_path = os.path.join(UPLOAD_FOLDER, "output_" + os.path.basename(filepath))
 df.to_excel(output_path, index=False)

 return output_path

if __name__ == "__main__":
 app.run(debug=True, use_reloader=False, port=5001)