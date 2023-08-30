from tkinter import *
from tkinter import ttk
from tkinter import messagebox, scrolledtext

# Path to the Bartender database file
path_to_bartender_file = "./Hay - Hynder.txt"

# A list containing objects of the Box class
boxes = []


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

    def get_ean_13(self, index):
        return self.ean_13[index]

    def get_new_number(self, index):
        return self.new_number[index]

    def get_number_of_entries(self):
        return len(self.item_name)

    def get_number_to_pack(self, index):
        return self.number_to_pack[index]

    def add_cushions_to_pack(self, index, number):
        self.number_to_pack[index] = number

    def delete_cushions_to_pack(self, index):
        self.number_to_pack[index] = 0

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
        # If no boxes exist or if the last box in the list is full, adds a new box
        self.boxes = []
        self.boxes.append(Box(self.boxes))

        if total_space_taken <= 10000:
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
                self.text_output += f"Kasse {i + 1} ({int(box.room_used() / 100)}%):\n\n"
                for y in range(len(self.boxes[i].old_number)):
                    if self.boxes[i].in_this_box[y]:
                        self.text_output += (f"{self.boxes[i].old_number[y]} - {self.boxes[i].item_name[y]} - "
                                             f"{self.boxes[i].color[y]} x {self.boxes[i].in_this_box[y]} stk\n")
                self.text_output += "\n\n"
            results_window = Toplevel(window)
            results_window.title("Pakningsinstrukser")
            results_window.geometry("800x500")
            results_window.focus_set()
            results_window.grab_set()
            text_output_area = scrolledtext.ScrolledText(results_window, font=("Segoe UI", "9"))
            text_output_area.pack(padx=12, pady=12, fill=BOTH, expand=TRUE)
            text_output_area.insert("end", self.text_output)
            text_output_area.config(state=DISABLED)


# Objects of the Box class contain items to be packaged together in the same box
# Inherits from the Cushion class
class Box(Cushion):
    def __init__(self, list_of_boxes, bartender_path=path_to_bartender_file):
        super().__init__(list_of_boxes, bartender_path)
        self.in_this_box = []

        for i in range(len(self.bartender_entries)):
            if "Set of 2" not in self.bartender_entries[i]:
                self.in_this_box.append(0)

        # Not currently in use - missing data (the 1s are placeholders)
        self.number_per_label = {
            "812094": 1,
            "376191": 1,
            "812095": 1,
            "376193": 1,
            "812096": 1,
            "376195": 1,
            "812097": 1,
            "376197": 1,
            "812098": 1,
            "376199": 1,
            "812099": 1,
            "376210": 1,
            "812100": 1,
            "376211": 1,
            "812221": 1,
            "376201": 1,
            "812223": 1,
            "376203": 1,
            "812225": 1,
            "376205": 1,
            "812227": 1,
            "376207": 1,
            "812229": 1,
            "376209": 1,
            "943219": 1,
            "943238": 1,
            "943220": 1,
            "943239": 1,
            "943232": 1,
            "943241": 1
        }

    # How much space is currently used
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


# Runs when the "Tilføj" button is pressed.
# Adds the chosen type and amount to the listbox.
# The data isn't added anywhere else yet at this point
def add_cushions():
    if number_entry_box.get().isnumeric() and 1000 >= int(number_entry_box.get()) > 0:
        cushions_listbox.insert(END, f"{cushions_drop_down_list.get()} - {number_entry_box.get()} stk")
        number_entry_box.delete(0, END)
    else:
        number_entry_box.delete(0, END)
        number_entry_box.focus_set()
        messagebox.showwarning("HAY Hynder", "Indtast antal\n(1 - 1000).")


# Runs when the "Slet" button is pressed.
# Deletes the currently selected Listbox item
def delete_cushions():
    cushions_listbox.delete(cushions_listbox.curselection())


# Builds an object of the main "Cushion" class
cushions = Cushion(boxes, path_to_bartender_file)

# Builds elements of the dropdown list
cushions_drop_down_entries = []

for cushion in range(cushions.get_number_of_entries()):
    cushion_entry = ""
    cushion_entry += cushions.get_old_number(cushion) + " - "
    cushion_entry += cushions.get_item_name(cushion) + " - "
    cushion_entry += cushions.get_color(cushion)

    cushion_entry = cushion_entry.replace(" FR", "")
    cushion_entry = cushion_entry.replace("Palissade ", "")
    cushion_entry = cushion_entry.replace(" textile", "")
    cushion_entry = cushion_entry.replace(" foam", "")

    cushions_drop_down_entries.append(cushion_entry)

# GUI

window = Tk()
window.resizable(False, False)
window.geometry(f"658x427+{window.winfo_screenwidth() // 2 - 250}+{window.winfo_screenheight() // 4}")
window.title("Hyndeplanlægger")

cushion_input_frame = Frame(window)

cushions_drop_down_list = ttk.Combobox(cushion_input_frame, values=cushions_drop_down_entries, width=80)
cushions_drop_down_list.set(cushions_drop_down_entries[0])
cushions_drop_down_list["state"] = "readonly"
cushions_drop_down_list.grid(row=0, column=0, padx=10)

number_entry_box = Entry(cushion_input_frame, width=5)
number_entry_box.grid(row=0, column=1, padx=8)

add_button = Button(cushion_input_frame, text="Tilføj", width=6, command=add_cushions)
add_button.grid(row=0, column=2, padx=10)

cushions_listbox = Listbox(window, width=101, height=20)

listbox_scrollbar = Scrollbar(window)

cushions_listbox.config(yscrollcommand=listbox_scrollbar.set)

listbox_scrollbar.config(command=cushions_listbox.yview)

bottom_buttons_frame = Frame(window)

delete_button = Button(bottom_buttons_frame, text="Slet", width=6, command=delete_cushions)
delete_button.grid(row=0, column=0, pady=12)

ghost_label = Label(bottom_buttons_frame, text="")
ghost_label.grid(row=0, column=1, padx=224)

calculate_button = Button(bottom_buttons_frame, text="Udregn", width=16, command=cushions.calculate_and_distribute)
calculate_button.grid(row=0, column=2, pady=8)

cushion_input_frame.pack(pady=12)
cushions_listbox.pack(anchor="w", padx=15)
listbox_scrollbar.place(x=624, y=50, height=322)
bottom_buttons_frame.pack()

window.mainloop()
