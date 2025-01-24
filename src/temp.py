from tkinter import messagebox, Tk, simpledialog

root = Tk()
root.withdraw()
response1 = messagebox.askyesno("Youtube", "У меня одного отъебнул ютуб?")
response2 = messagebox.showinfo("Инфа года", "Лепс спел - спел лесп читается одинаково")
response3 = simpledialog.askstring("Бебра", "У бобра")

print("Ответ1:", response1)
print("Ответ2:", response2)
print("Ответ3:", response3)