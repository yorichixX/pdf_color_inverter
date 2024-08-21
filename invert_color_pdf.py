import fitz  # a module of PyMuPDF
import tkinter as tk
from tkinter import filedialog, messagebox
from tkinter import ttk  # For the progress bar
import threading # to make tasks run in parallel

def invert_pdf_colors(input_path, output_path, resolution=300, progress_callback=None):
    pdf_doc = fitz.open(input_path)
    total_pages = pdf_doc.page_count
    
    for page_num in range(total_pages):
        page = pdf_doc.load_page(page_num)
        
        #resolution for the pixmap
        matrix = fitz.Matrix(resolution / 72, resolution / 72)  # scale factor
        
        pix = page.get_pixmap(matrix=matrix)
        pix.invert_irect(fitz.Rect(0, 0, pix.width, pix.height))
        page.insert_image(page.rect, pixmap=pix)
        
        # Update progress bar
        if progress_callback:
            progress_callback(page_num + 1, total_pages)
    
    pdf_doc.save(output_path)

def select_input_file():
    input_path = filedialog.askopenfilename(filetypes=[("PDF files", "*.pdf")])
    if input_path:
        input_entry.delete(0, tk.END)
        input_entry.insert(0, input_path)

def select_output_path():
    output_path = filedialog.asksaveasfilename(defaultextension=".pdf", filetypes=[("PDF files", "*.pdf")])
    if output_path:
        output_entry.delete(0, tk.END)
        output_entry.insert(0, output_path)

def update_progress(current, total):
    progress_var.set((current / total) * 100)
    root.update_idletasks()

def start_inversion():
    input_path = input_entry.get()
    output_path = output_entry.get()

    if not input_path or not output_path:
        messagebox.showerror("Error", "Please select both input file and path where you want to save your pdf")
        return

    try:
        # Run the inversion in a separate thread
        threading.Thread(target=run_inversion, args=(input_path, output_path)).start()
    except Exception as e:
        messagebox.showerror("Error", f"An error occurred: {e}")

def run_inversion(input_path, output_path):
    try:
        invert_pdf_colors(input_path, output_path, resolution=300, progress_callback=update_progress)
        # Show success message on the main thread
        root.after(0, lambda: messagebox.showinfo("Success", "PDF color inversion completed successfully."))
    except Exception as e:
        root.after(0, lambda: messagebox.showerror("Error", f"An error occurred: {e}"))
    finally:
        # Reset the progress bar
        root.after(0, lambda: progress_var.set(0))

# Set up the GUI
root = tk.Tk()
root.title("PDF Color Inverter")

# for input pdf
input_label = tk.Label(root, text="Select Input PDF:")
input_label.grid(row=0, column=0, padx=10, pady=5, sticky="w")

input_entry = tk.Entry(root, width=50)
input_entry.grid(row=0, column=1, padx=10, pady=5)

input_button = tk.Button(root, text="Browse...", command=select_input_file)
input_button.grid(row=0, column=2, padx=10, pady=5)

# for output pdf
output_label = tk.Label(root, text="Location and Name:")
output_label.grid(row=1, column=0, padx=10, pady=5, sticky="w")

output_entry = tk.Entry(root, width=50)
output_entry.grid(row=1, column=1, padx=10, pady=5)

output_button = tk.Button(root, text="Browse...", command=select_output_path)
output_button.grid(row=1, column=2, padx=10, pady=5)

# Progress label and bar
progress_label = tk.Label(root, text="Progress:")
progress_label.grid(row=2, column=0, padx=10, pady=5, sticky="w")

progress_var = tk.DoubleVar()
progress = ttk.Progressbar(root, variable=progress_var, maximum=100)
progress.grid(row=2, column=1, columnspan=2, padx=10, pady=10, sticky="ew")

# Start button
start_button = tk.Button(root, text="Start Inversion", command=start_inversion)
start_button.grid(row=3, column=0, columnspan=3, pady=20)

# Run the GUI
root.mainloop()
