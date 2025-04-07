import tkinter as tk
from tkinter import filedialog, messagebox
from pdf2docx import Converter
from docx2pdf import convert as docx_to_pdf
import os

# PDF → DOCX
def convert_pdf_to_docx():
    pdf_file = filedialog.askopenfilename(filetypes=[("PDF files", "*.pdf")])
    if not pdf_file:
        return

    save_path = filedialog.asksaveasfilename(defaultextension=".docx", filetypes=[("Word files", "*.docx")])
    if not save_path:
        return

    try:
        cv = Converter(pdf_file)
        cv.convert(save_path)
        cv.close()
        messagebox.showinfo("성공", f"PDF → DOCX 변환 완료:\n{save_path}")
    except Exception as e:
        messagebox.showerror("오류", str(e))


# DOCX → PDF
def convert_docx_to_pdf():
    docx_file = filedialog.askopenfilename(filetypes=[("Word files", "*.docx")])
    if not docx_file:
        return

    save_path = filedialog.asksaveasfilename(defaultextension=".pdf", filetypes=[("PDF files", "*.pdf")])
    if not save_path:
        return

    try:
        docx_to_pdf(docx_file, save_path)
        messagebox.showinfo("성공", f"DOCX → PDF 변환 완료:\n{save_path}")
    except Exception as e:
        messagebox.showerror("오류", str(e))


# GUI 설정
root = tk.Tk()
root.title("PDF <-> DOCX 변환기")
root.geometry("600x300")
root.resizable(False, False)

# 프레임
left_frame = tk.Frame(root, width=300, height=300, bg="#f0f0f0")
right_frame = tk.Frame(root, width=300, height=300, bg="#f9f9f9")
left_frame.pack(side="left", fill="both", expand=True)
right_frame.pack(side="right", fill="both", expand=True)

# 좌측 PDF → DOCX
tk.Label(left_frame, text="PDF → DOCX", font=("Arial", 14), bg="#f0f0f0").pack(pady=20)
tk.Button(left_frame, text="PDF 파일 선택", font=("Arial", 12), command=convert_pdf_to_docx, bg="#4CAF50", fg="white", padx=10, pady=5).pack()

# 우측 DOCX → PDF
tk.Label(right_frame, text="DOCX → PDF", font=("Arial", 14), bg="#f9f9f9").pack(pady=20)
tk.Button(right_frame, text="DOCX 파일 선택", font=("Arial", 12), command=convert_docx_to_pdf, bg="#2196F3", fg="white", padx=10, pady=5).pack()

root.mainloop()
