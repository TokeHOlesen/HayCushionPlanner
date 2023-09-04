# ver. 1.0 01-09-2023

from tkinter import *
from tkinter import ttk
from tkinter import messagebox, scrolledtext
from tkinter.filedialog import asksaveasfile

# Path to the Bartender database file
path_to_bartender_file = "./Hay - Hynder.txt"

# A container for objects of the Box class
boxes = []


# Note: this class contains multiple lists with the properties of all the known items (name, item number,
# color etc.). All those lists have a shared index (so you can look up a property of an item if you know the index of
# another property - e.g. if you know the index of the item number, you can pass that same index to the "description"
# getter method. All getter methods require an index).
class Cushion:
    # Note: list_of_boxes gets passed as reference
    def __init__(self, list_of_boxes, bartender_path):
        self.boxes = list_of_boxes
        self.text_output = ""
        self.bartender_entries = []
        # Reads the BarTender file and adds the contents to the corresponding lists
        try:
            with open(bartender_path) as bartender_file:
                for line in bartender_file:
                    self.bartender_entries.append(line)
            self.bartender_entries.pop(0)
        except FileNotFoundError:
            messagebox.showerror("Fejl", "Kan ikke finde BarTender filen.")
            raise SystemExit
        self.old_number = []
        self.item_name = []
        self.color = []
        self.ean_13 = []
        self.new_number = []
        self.number_to_pack = []
        for i in range(len(self.bartender_entries)):
            if "Set of 2" not in self.bartender_entries[i]:
                this_entry = self.bartender_entries[i].split(";")
                self.old_number.append(this_entry[0])
                self.item_name.append(this_entry[1])
                self.color.append(this_entry[2])
                self.ean_13.append(this_entry[3])
                self.new_number.append(this_entry[4][:-1])
                self.number_to_pack.append(0)

        # How much room a single cushion of a given type takes up in a large box, in percent * 100
        self.required_space = {
            "812094": 133,
            "376191": 133,
            "812095": 185,
            "376193": 185,
            "812096": 200,
            "376195": 200,
            "812097": 500,
            "376197": 500,
            "812098": 500,
            "376199": 500,
            "812099": 300,
            "376210": 300,
            "812100": 200,
            "376211": 200,
            "812221": 100,
            "376201": 100,
            "812223": 185,
            "376203": 185,
            "812225": 434,
            "376205": 434,
            "812227": 133,
            "376207": 133,
            "812229": 357,
            "376209": 357,
            "943219": 500,
            "943238": 500,
            "943220": 500,
            "943239": 500,
            "943232": 333,
            "943241": 333
        }

        # A list containing space requirement of the given item type (index corresponds to other lists)
        self.space_req_by_type = []

        # Fills the empty list with "0" values
        for i in range(len(self.old_number)):
            self.space_req_by_type.append(0)

        # Adjusts the values according to those found in required_space
        for i in range(len(self.old_number)):
            for number in self.required_space:
                if number in self.old_number[i]:
                    self.space_req_by_type[i] = self.required_space[number]

    # Accepts an old item number and returns the index of the corresponding item.
    # This index works for all other lists in this class
    def get_index_by_old_number(self, old_number):
        for i in range(len(self.old_number)):
            if self.old_number[i] == old_number:
                return i

    def get_old_number(self, index):
        return self.old_number[index]

    def get_item_name(self, index):
        return self.item_name[index]

    def get_color(self, index):
        return self.color[index]

    # Updates the number of cushions at the entered index to be packed
    def add_cushions_to_pack(self, index, number):
        self.number_to_pack[index] = number

    def save_text_output(self):
        text_file = asksaveasfile(defaultextension=".txt",
                                  filetypes=[("Tekstdokumenter", "*.txt"), ("Alle filer", "*.*")])
        if text_file is None:
            return
        with open(text_file.name, "w") as t_f:
            t_f.write(self.text_output)

    def calculate_and_distribute(self):
        # Resets the number of all cushion types to 0
        for i in range(len(self.number_to_pack)):
            self.number_to_pack[i] = 0
        # Iterates through all string items in the listbox, splits each string into lists.
        # Index [0] corresponds to old item number, [-2] to number of items.
        # Looks the item up by old number, identifies the index and adds the entered number of cushions to
        # self.number_to_pack at that index
        for cushion_in_listbox in cushions_listbox.get(0, END):
            split_string = cushion_in_listbox.split(" ")
            cushions.add_cushions_to_pack(cushions.get_index_by_old_number(split_string[0]), int(split_string[-2]))
        # Calculates total space required by all items
        total_space_taken = 0
        for i in range(len(self.number_to_pack)):
            for y in range(self.number_to_pack[i]):
                for cushion_type in self.required_space:
                    if cushion_type in self.old_number[i]:
                        total_space_taken += self.required_space[cushion_type]
        # Puts items in boxes.
        # If no boxes exist or if the last box in the list is full, creates a new box
        self.boxes = []
        self.boxes.append(Box(self.boxes))

        if total_space_taken == 0:
            messagebox.showwarning("Fejl", "Ingen varer valgt.")
        elif 0 < total_space_taken <= 10000:
            messagebox.showinfo("HAY Hynder", "Det hele kan være i én kasse.")
        else:
            self.text_output = ""
            for i in range(len(self.old_number)):
                while self.number_to_pack[i] > 0:
                    if self.boxes[-1].room_left() >= self.space_req_by_type[i]:
                        self.boxes[-1].in_this_box[i] += 1
                        self.number_to_pack[i] -= 1
                    else:
                        self.boxes.append(Box(boxes))
            for i, box in enumerate(self.boxes):
                self.text_output += f"Kasse {i + 1} ({box.room_used() // 100}%):\n\n"
                for y in range(len(self.boxes[i].old_number)):
                    if self.boxes[i].in_this_box[y]:
                        self.text_output += (f"{self.boxes[i].old_number[y]} - {self.boxes[i].item_name[y]} - "
                                             f"{self.boxes[i].color[y]} x {self.boxes[i].in_this_box[y]} stk\n")
                self.text_output += "\n\n"
            self.text_output = self.text_output[:-3]

            # Spawns a new window with the final results
            results_window = Toplevel(window)
            results_window.title("Pakningsinstrukser")
            results_window.geometry("660x500")
            results_window.iconbitmap("./box.ico")
            results_window.focus_set()
            results_window.grab_set()
            text_output_area = scrolledtext.ScrolledText(results_window, font=("Segoe UI", "9"))
            text_output_area.pack(padx=4, pady=4, fill=BOTH, expand=TRUE)
            text_output_area.insert("end", self.text_output)
            text_output_area.config(state=DISABLED)
            save_button = Button(results_window, text="Gem", width=12, command=self.save_text_output)
            save_button.pack(anchor="w", padx=4, pady=4)


# Objects of the Box class contain items to be packaged together in the same box.
# Inherits from the Cushion class
class Box(Cushion):
    def __init__(self, list_of_boxes, bartender_path=path_to_bartender_file):
        super().__init__(list_of_boxes, bartender_path)
        self.in_this_box = []

        for i in range(len(self.bartender_entries)):
            if "Set of 2" not in self.bartender_entries[i]:
                self.in_this_box.append(0)

    # How much space is currently being used
    def room_used(self):
        total_room_in_this_box = 0
        for i in range(len(self.in_this_box)):
            for y in range(self.in_this_box[i]):
                for cushion_type in self.required_space:
                    if cushion_type in self.old_number[i]:
                        total_room_in_this_box += self.required_space[cushion_type]
        return total_room_in_this_box

    # How much room there is left in this box
    def room_left(self):
        return 10000 - self.room_used()


# Adds the chosen type and amount to the listbox.
# The data isn't added anywhere else yet at this point
def add_cushions():
    if number_entry_box.get().isnumeric() and 1000 >= int(number_entry_box.get()) > 0:
        cushions_listbox.insert(END, f"{cushions_drop_down_list.get()} - {number_entry_box.get()} stk")
        number_entry_box.delete(0, END)
    else:
        number_entry_box.delete(0, END)
        number_entry_box.focus_set()
        messagebox.showwarning("Fejl", "Indtast antal\n(1 - 1000).")


# Runs when the "Slet" button is pressed.
# Deletes the currently selected Listbox item
def delete_cushions():
    if cushions_listbox.curselection():
        cushions_listbox.delete(cushions_listbox.curselection())
    else:
        messagebox.showwarning("Fejl", "Ingen varer valgt.")


# Builds an object of the main Cushion class
cushions = Cushion(boxes, path_to_bartender_file)

# Builds elements of the dropdown list
cushions_drop_down_entries = []

for cushion in range(len(cushions.old_number)):
    cushion_entry = ""
    cushion_entry += cushions.get_old_number(cushion) + " - "
    cushion_entry += cushions.get_item_name(cushion) + " - "
    cushion_entry += cushions.get_color(cushion)

    cushion_entry = cushion_entry.replace(" FR", "")
    cushion_entry = cushion_entry.replace("Palissade ", "")
    cushion_entry = cushion_entry.replace(" textile", "")
    cushion_entry = cushion_entry.replace(" foam", "")

    cushions_drop_down_entries.append(cushion_entry)


# Adds chosen items to the listbox and moves focus back to the dropdown list
def add_and_return_focus():
    add_cushions()
    cushions_drop_down_list.focus_set()


# GUI

# Main window properties
window = Tk()
window.resizable(False, False)
window.geometry(f"658x427+{window.winfo_screenwidth() // 2 - 250}+{window.winfo_screenheight() // 4}")
window.title("Planlæg pakning af hynder")
window.iconbitmap("./box.ico")

# A container for the elements used to input data - cushion selection dropdown menu, number entry box and the
# "add" button
cushion_input_frame = Frame(window)

# A dropdown list containing all known cushion types
cushions_drop_down_list = ttk.Combobox(cushion_input_frame, values=cushions_drop_down_entries, width=80)
cushions_drop_down_list.set(cushions_drop_down_entries[0])
cushions_drop_down_list["state"] = "readonly"
cushions_drop_down_list.bind("<Return>", lambda event: number_entry_box.focus_set())
cushions_drop_down_list.bind("<Right>", lambda event: number_entry_box.focus_set())
cushions_drop_down_list.grid(row=0, column=0, padx=10)
cushions_drop_down_list.focus_set()

# An entry box for entering the required number of a given type of cushion
number_entry_box = Entry(cushion_input_frame, width=5)
number_entry_box.bind("<Return>", lambda event: add_and_return_focus())
number_entry_box.bind("<Left>", lambda event: cushions_drop_down_list.focus_set())
number_entry_box.bind("<Right>", lambda event: add_button.focus_set())
number_entry_box.grid(row=0, column=1, padx=8)

# When pressed, adds the entered amount of the chosen type of cushions to the listbox (and litbox only)
add_button = Button(cushion_input_frame, text="Tilføj", width=6, command=add_cushions)
add_button.bind("<Return>", lambda event: add_and_return_focus())
add_button.bind("<Left>", lambda event: number_entry_box.focus_set())
add_button.grid(row=0, column=2, padx=10)

# The listbox is a view of all the selected items
cushions_listbox = Listbox(window, width=101, height=20)

# Adds a scrollbar to the listbox view
listbox_scrollbar = Scrollbar(window)
cushions_listbox.config(yscrollcommand=listbox_scrollbar.set, takefocus=False)
listbox_scrollbar.config(command=cushions_listbox.yview)

# A container for the "Udregn" and "Slet" buttons at the bottom of the window
bottom_buttons_frame = Frame(window)

# When pressed, runs the main method of the Cushions class and builds a list of Box class objects, one for each box
calculate_button = Button(bottom_buttons_frame, text="Udregn", width=16, command=cushions.calculate_and_distribute)
calculate_button.bind("<Return>", lambda event: cushions.calculate_and_distribute())
calculate_button.grid(row=0, column=2, pady=8)

# An invisible label inserted between the "Udregn" and "Slet" buttons, for layout purposes only
ghost_label = Label(bottom_buttons_frame, text="")
ghost_label.grid(row=0, column=1, padx=224)

# When pressed, removes the selected line from the listbox
delete_button = Button(bottom_buttons_frame, text="Slet", width=6, command=delete_cushions)
delete_button.bind("<Return>", lambda event: delete_cushions())
delete_button.grid(row=0, column=0, pady=12)

# Placement of UI element containers
cushion_input_frame.pack(pady=12)
cushions_listbox.pack(anchor="w", padx=15)
listbox_scrollbar.place(x=624, y=50, height=322)
bottom_buttons_frame.pack()

window.mainloop()
