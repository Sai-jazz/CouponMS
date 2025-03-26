from PyQt5 import QtWidgets, QtGui, QtCore
import json
from cryptography.fernet import Fernet
import uuid
import webbrowser
import csv
from datetime import datetime, timedelta
from dotenv import load_dotenv
import os

load_dotenv()
COUPON_FILE = "fuffin.json"
PASSWORD = os.getenv("PASSWORD")  # Set your password here
GENERATION_PASSWORD = os.getenv("GEN_PASS")  # Set your password for generating coupons

# Load or initialize coupon data
def load_coupons():
    try:
        with open(COUPON_FILE, "r") as file:
            return json.load(file)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}

def save_coupons(data):
    with open(COUPON_FILE, "w") as file:
        json.dump(data, file, indent=4)

coupons = load_coupons()



class CouponManager(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        if not self.authenticate(PASSWORD, "Authentication"):
            QtWidgets.QMessageBox.critical(self, "Access Denied", "Incorrect password! Exiting...")
            raise SystemExit
        
            
          
        else:
            self.init_ui()
    
    def authenticate(self, required_password, title):
        password, ok = QtWidgets.QInputDialog.getText(self, title, "Enter Password:", QtWidgets.QLineEdit.Password)
        return ok and password == required_password
      
    
    
    def init_ui(self):
        self.setWindowTitle("Coupon Manager")
        self.setGeometry(100, 100, 1000, 800)
        self.layout = QtWidgets.QVBoxLayout()
        
        # Title
        self.title_label = QtWidgets.QLabel("COUP&ON")
        self.title_label.setFont(QtGui.QFont("Berosong", 20, QtGui.QFont.Bold))
        self.title_label.setAlignment(QtCore.Qt.AlignCenter)
        self.layout.addWidget(self.title_label)
        
        # Search Bar
        self.search_layout = QtWidgets.QHBoxLayout()
        self.search_entry = QtWidgets.QLineEdit(self)
        self.search_entry.setPlaceholderText("Search by Code, Status, or Date")
        self.search_entry.textChanged.connect(self.filter_coupons)
        self.search_layout.addWidget(self.search_entry)
        self.layout.addLayout(self.search_layout)
        
        # Coupon Entry and Validation
        self.entry_layout = QtWidgets.QHBoxLayout()
        self.coupon_entry = QtWidgets.QLineEdit(self)
        self.coupon_entry.setPlaceholderText("Enter Coupon Code")
        self.entry_layout.addWidget(self.coupon_entry)
        
        self.validate_btn = QtWidgets.QPushButton("Validate Coupon", self)
        self.validate_btn.clicked.connect(self.validate_coupon)
        self.entry_layout.addWidget(self.validate_btn)
        self.layout.addLayout(self.entry_layout)
        

        self.group_box1 = QtWidgets.QGroupBox("Generate",self) #generate groupbox
       
        # Buttons for Actions
        self.generate_btn = QtWidgets.QPushButton("Generate Coupon", self) 
        self.generate_btn.setFixedSize(150, 40)  # Width: 150px, Height: 40px
        self.generate_btn.clicked.connect(self.generate_coupon)
        
        
        self.generate_10_btn = QtWidgets.QPushButton("Generate 10 Coupons", self)
        self.generate_10_btn.setFixedSize(150, 40)  # Width: 150px, Height: 40px
        self.generate_10_btn.clicked.connect(self.generate_10_coupons)
       

      
        h1_layout = QtWidgets.QHBoxLayout() #create horizontal layout
        h1_layout.addWidget(self.generate_btn)
        h1_layout.addWidget(self.generate_10_btn) 

        self.group_box1.setLayout(h1_layout) #set layout for group box
        self.layout.addWidget(self.group_box1)
        self.setLayout(self.layout)
      

      
        
        self.share_selected_btn = QtWidgets.QPushButton("Share Selected Coupons", self)
        self.share_selected_btn.setFixedSize(150, 40)  # Width: 150px, Height: 40px
        self.share_selected_btn.clicked.connect(self.share_selected_coupons)
        self.layout.addWidget(self.share_selected_btn)
        

        self.group_box2 = QtWidgets.QGroupBox("Remove",self) #generate groupbox


        self.remove_used_btn = QtWidgets.QPushButton("Remove Used and expired ", self)
        self.remove_used_btn.setFixedSize(160, 40)  # Width: 150px, Height: 40px
        self.remove_used_btn.clicked.connect(self.remove_used_coupons)
        
        
        self.remove_unshared_btn = QtWidgets.QPushButton("Remove Unshared Coupons", self)
        self.remove_unshared_btn.setFixedSize(200, 40)  # Width: 150px, Height: 40px
        self.remove_unshared_btn.clicked.connect(self.remove_unshared_coupons)
       

        h2_layout = QtWidgets.QHBoxLayout() #create horizontal layout
        h2_layout.addWidget(self.remove_used_btn)
        h2_layout.addWidget(self.remove_unshared_btn) 

        self.group_box2.setLayout(h2_layout) #set layout for group box
        self.layout.addWidget(self.group_box2) #add goupbox to the main layout
        self.setLayout(self.layout)


        
        self.export_csv_btn = QtWidgets.QPushButton("Export to CSV", self)
        self.export_csv_btn.setFixedSize(150, 40)  # Width: 150px, Height: 40px
        self.export_csv_btn.clicked.connect(self.export_to_csv)
        self.layout.addWidget(self.export_csv_btn)

        #refresh button
        self.refresh_btn = QtWidgets.QPushButton("Refresh", self)
        self.refresh_btn.setFixedSize(150, 40)
        self.refresh_btn.clicked.connect(self.refresh_data)  # Calls refresh method
        self.layout.addWidget(self.refresh_btn)

        
        # Statistics Display
        self.stats_label = QtWidgets.QLabel("Statistics: Valid - 0 | Used - 0 | Expired - 0")
        self.stats_label.setFont(QtGui.QFont("Arial", 12))
        self.layout.addWidget(self.stats_label)
        
        # Coupon List Table
        self.coupon_list = QtWidgets.QTableWidget()
        self.coupon_list.setColumnCount(5)
        self.coupon_list.setHorizontalHeaderLabels(["Code", "Status", "Created At", "Expiry Date", "Shared"])
        self.coupon_list.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)
        self.coupon_list.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)
        self.coupon_list.setColumnWidth(0, 150)
        self.coupon_list.setColumnWidth(1, 100)
        self.coupon_list.setColumnWidth(2, 200)
        self.coupon_list.setColumnWidth(3, 200)
        self.coupon_list.setColumnWidth(4, 100)
        self.layout.addWidget(self.coupon_list)
        
        self.setLayout(self.layout)
        self.update_coupon_list()
        self.update_statistics()
    
    def get_expiry_days(self):
        """Prompt the user to enter the number of days until the coupon expires."""
        days, ok = QtWidgets.QInputDialog.getInt(self, "Set Expiry", "Enter the number of days until the coupon expires:", 30, 1, 365)
        if ok:
            return days
        return None
    
    def generate_coupon(self):
        if not self.authenticate(GENERATION_PASSWORD, "Generate Coupon Authentication"):
            QtWidgets.QMessageBox.warning(self, "Access Denied", "Incorrect password!")
            return

        # Ask for the number of coupons to generate
        num_coupons, ok = QtWidgets.QInputDialog.getInt(self, "Number of Coupons", "Enter the number of coupons to generate:", min=1)
        if not ok or num_coupons < 1:
            return  # User canceled or entered an invalid number

        # Ask for expiry days
        expiry_days = self.get_expiry_days()
        if expiry_days is None:
            return  # User canceled the input
        
        generated_coupons = []
        
        for _ in range(num_coupons):
            coupon_code = str(uuid.uuid4())[:8].upper()
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            expiry_date = (datetime.now() + timedelta(days=expiry_days)).strftime("%Y-%m-%d %H:%M:%S")
            coupons[coupon_code] = {"status": "Valid", "timestamp": timestamp, "expiry": expiry_date, "shared": False}
            generated_coupons.append(coupon_code)

        save_coupons(coupons)
        self.update_coupon_list()
        self.update_statistics()
        
        # Ask to share the generated coupons
        self.ask_to_share(generated_coupons)

    
    def generate_10_coupons(self):
        if not self.authenticate(GENERATION_PASSWORD, "Generate 10 Coupons Authentication"):
            QtWidgets.QMessageBox.warning(self, "Access Denied", "Incorrect password!")
            return
        
        expiry_days = self.get_expiry_days()
        if expiry_days is None:
            return  # User canceled the input
        
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        expiry_date = (datetime.now() + timedelta(days=expiry_days)).strftime("%Y-%m-%d %H:%M:%S")
        new_coupons = []
        for _ in range(10):
            coupon_code = str(uuid.uuid4())[:8].upper()
            coupons[coupon_code] = {"status": "Valid", "timestamp": timestamp, "expiry": expiry_date, "shared": False}
            new_coupons.append(coupon_code)
        save_coupons(coupons)
        self.update_coupon_list()
        self.update_statistics()
        self.ask_to_share(new_coupons)
    
    def ask_to_share(self, coupon_codes):
        """Ask the user if they want to share the generated coupons."""
        reply = QtWidgets.QMessageBox.question(
            self,
            "Share Coupons",
            "Do you want to share the generated coupons via WhatsApp?",
            QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No,
        )
        if reply == QtWidgets.QMessageBox.Yes:
            self.share_coupons(coupon_codes)
    
    def share_coupons(self, coupon_codes):
        """Share the coupons via WhatsApp."""
        message = "Hey! You know there's a restaurant near you with great food. Let me give you a coupon so you can enjoy it with your friends.  \nHurryup! Valid for only few days\n\n" 
        coupon_text = "\n".join(coupon_codes)
        full_text = message + coupon_text
        full_text = full_text.replace(" ", "%20").replace("\n", "%0A")
        url = f"https://api.whatsapp.com/send?text={full_text}"
        webbrowser.open(url)
        
        for code in coupon_codes:
            if code in coupons:
                coupons[code]["shared"] = True
        save_coupons(coupons)
        self.update_coupon_list()
        
    
    def validate_coupon(self):
        code = self.coupon_entry.text().strip().upper()
        if code in coupons:
            if coupons[code]["status"] == "Valid":
                if datetime.now() <= datetime.strptime(coupons[code]["expiry"], "%Y-%m-%d %H:%M:%S"):
                    coupons[code]["status"] = "Used"
                    save_coupons(coupons)
                    self.update_coupon_list()
                    self.update_statistics()
                    QtWidgets.QMessageBox.information(self, "Success", "Coupon is valid and marked as used!")
            elif datetime.now() >= datetime.strptime(coupons[code]["expiry"], "%Y-%m-%d %H:%M:%S") or coupons[code]["status"] == "Expired":
                coupons[code]["status"] = "Expired"
                save_coupons(coupons)
                self.update_coupon_list()
                self.update_statistics()
                QtWidgets.QMessageBox.warning(self, "Error", "Coupon has expired!")
            else:
                QtWidgets.QMessageBox.warning(self, "Error", "Coupon is already used!")
        else:
            QtWidgets.QMessageBox.warning(self, "Error", "Invalid coupon code!")
    
    def remove_used_coupons(self):
        # Show confirmation dialog
        reply = QtWidgets.QMessageBox.question(
            self, 
            "Confirm Deletion", 
            "Want to remove all used and expired coupons?", 
            QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No, 
            QtWidgets.QMessageBox.No
        )

        # Proceed only if the user clicks "Yes"
        if reply == QtWidgets.QMessageBox.Yes:
            global coupons
            coupons = {code: data for code, data in coupons.items() if data["status"] not in ["Used", "Expired"]}
            save_coupons(coupons)
            self.update_coupon_list()
            self.update_statistics()

            QtWidgets.QMessageBox.information(self, "Cleanup", "All used and expired coupons have been removed.")

    
    def remove_unshared_coupons(self):
        selected_coupons = []
        for item in self.coupon_list.selectedItems():
            if item.column() == 0:  # Only add the coupon code (first column)
              selected_coupons.append(item.text())
    
        if not selected_coupons:
            QtWidgets.QMessageBox.warning(self, "No Selection", "Please select coupons to remove.")
            return
    
        global coupons
       

        for code in selected_coupons:
            if code in coupons and not coupons[code]["shared"]:
              del coupons[code]
    
        save_coupons(coupons)
        self.update_coupon_list()
        self.update_statistics()
        QtWidgets.QMessageBox.information(self, "Cleanup", "Selected unshared coupons have been removed.")
    
    def export_to_csv(self):
        filename, _ = QtWidgets.QFileDialog.getSaveFileName(self, "Save CSV", "", "CSV Files (*.csv)")

        if filename:
            try:
                # Ensure the file has the correct extension
                if not filename.endswith(".csv"):
                    filename += ".csv"

                # Update all coupons' shared status to True
                global coupons
                for code in coupons:
                    coupons[code]["shared"] = True  # Mark as shared

                # Save the updated coupons
                save_coupons(coupons)

                with open(filename, "w", newline="", encoding="utf-8") as file:
                    writer = csv.writer(file, delimiter=",", quotechar='"', quoting=csv.QUOTE_MINIMAL)

                    # Write CSV Header
                    writer.writerow(["Code", "Status", "Created At", "Expiry Date", "Shared"])

                    # Write Coupon Data
                    for code, data in coupons.items():
                        writer.writerow([
                            code, 
                            data.get("status", "N/A"), 
                            data.get("timestamp", "N/A"), 
                            data.get("expiry", "N/A"), 
                            "Yes"  # Ensure "Shared" is marked as Yes
                        ])

                QtWidgets.QMessageBox.information(self, "Export Successful", f"Coupons exported successfully to:\n{filename}")

            except Exception as e:
                QtWidgets.QMessageBox.critical(self, "Export Failed", f"An error occurred: {str(e)}")


    def refresh_data(self):
        self.update_coupon_list()
        self.update_statistics()
           
    
    def share_selected_coupons(self):
        selected_coupons = []
        for item in self.coupon_list.selectedItems():
            if item.column() == 0:  # Only add the coupon code (first column)
                selected_coupons.append(item.text())
        if selected_coupons:
            self.share_coupons(selected_coupons)
        else:
            QtWidgets.QMessageBox.warning(self, "No Selection", "Please select coupons to share.")
    
    def filter_coupons(self):
        search_text = self.search_entry.text().strip().lower()
        for row in range(self.coupon_list.rowCount()):
            match = False
            for col in range(self.coupon_list.columnCount()):
                item = self.coupon_list.item(row, col)
                if item and search_text in item.text().lower():
                    match = True
                    break
            self.coupon_list.setRowHidden(row, not match)
    

    def autocheck_expiry(self,code):
        if coupons[code]["status"] == "Valid":
                if datetime.now() <= datetime.strptime(coupons[code]["expiry"], "%Y-%m-%d %H:%M:%S"):
                    coupons[code]["status"] = "Used"
                    save_coupons(coupons)
                    self.update_coupon_list()
                    self.update_statistics()
                      # Recursively check for other valid coupons after one has been used or expired
                elif datetime.now() >= datetime.strptime(coupons[code]["expiry"], "%Y-%m-%d %H:%M:%S"):
                    coupons[code]["status"] = "Expired"
                    save_coupons(coupons)
                    self.update_coupon_list()
                    self.update_statistics()
                      # Recursively check for other valid coupons after one has been used or expired
                   

    def update_coupon_list(self):
        self.coupon_list.setRowCount(len(coupons))
        for row, (code, data) in enumerate(coupons.items()):
            self.coupon_list.setItem(row, 0, QtWidgets.QTableWidgetItem(code))
            self.coupon_list.setItem(row, 1, QtWidgets.QTableWidgetItem(data["status"]))
            self.coupon_list.setItem(row, 2, QtWidgets.QTableWidgetItem(data["timestamp"]))
            self.coupon_list.setItem(row, 3, QtWidgets.QTableWidgetItem(data["expiry"]))
            self.coupon_list.setItem(row, 4, QtWidgets.QTableWidgetItem("Yes" if data["shared"] else "No"))


            # Set row color based on status and expiry
            if data["status"] == "Used":
                self.color_row(row, QtGui.QColor(144, 238, 144))  # Light green for used coupons
            elif datetime.now() > datetime.strptime(data["expiry"], "%Y-%m-%d %H:%M:%S") :
                self.color_row(row, QtGui.QColor(255, 182, 193))  # Light red for expired coupons
                self.autocheck_expiry(code)
                
            else:
                self.color_row(row, QtGui.QColor(255, 255, 153))  # Light yellow for valid coupons
    
    def color_row(self, row, color):
        """Color the entire row with the specified color."""
        for col in range(self.coupon_list.columnCount()):
            item = self.coupon_list.item(row, col)
            if item:
                item.setBackground(color)
    
    def update_statistics(self):
        valid = sum(1 for data in coupons.values() if datetime.now() <= datetime.strptime(data["expiry"], "%Y-%m-%d %H:%M:%S") and data["status"]=="Valid")
        used = sum(1 for data in coupons.values() if data["status"] == "Used")
        expired = sum(1 for data in coupons.values() if datetime.now() > datetime.strptime(data["expiry"], "%Y-%m-%d %H:%M:%S"))
        self.stats_label.setText(f"Statistics: Valid - {valid} | Used - {used} | Expired - {expired}")

if __name__ == "__main__":
    app = QtWidgets.QApplication([])
    window = CouponManager()
    window.show()
    app.exec_()                                                                                                                             