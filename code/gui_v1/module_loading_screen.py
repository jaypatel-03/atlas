import tkinter

def press_button(button):
    button.configure(bg="red")


root = tkinter.Tk()

buttons = [] # <-- Added list of buttons
for i in range(4):
    quick_button = tkinter.Button(root, text=str(i) ,font=("courier", 30), 
                                  command=lambda i=i: press_button(buttons[i]))
    quick_button.grid(row=i, pady=3, padx=3)
    print(i)
    buttons.append(quick_button)

root.mainloop()