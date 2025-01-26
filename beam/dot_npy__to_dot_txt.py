import numpy as np

# Load the .npy file
npy_file_path = "data\confusion_digital_estimate.npy"  # Replace with your .npy file path
data = np.load(npy_file_path)

# print(data)
# Save the data to a .txt file
txt_file_path = "confusion_digital_estimate.txt"  # Replace with your desired .txt file path
np.savetxt(txt_file_path, data, fmt='%s')

print(f"Data from {npy_file_path} has been saved to {txt_file_path}.")