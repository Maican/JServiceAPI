import requests
import requests.exceptions
import tkinter as tk
from tkinter import messagebox
from tkinter import *


class Error(Exception):
    """Base class for other exceptions"""
    pass


class NoIDProvidedError:
    """Raised when id is not passed."""
    pass


def api_get_random_clues(amount=1):
    query_params = {"count": amount}
    return get_api_response("http://jservice.io/api/random", query_params)


def api_get_categories(amount=1, offset=0):
    query_params = {"count": amount, "offset": offset}
    return get_api_response("http://jservice.io/api/categories", query_params)


def api_get_clues(value=None, category=None, min_date=None, max_date=None, offset=None):
    query_params = {}
    if value is not None:
        query_params["value"] = value
    if category is not None:
        query_params["category"] = category
    if min_date is not None:
        query_params["min_date"] = min_date
    if max_date is not None:
        query_params["max_date"] = max_date
    if offset is not None:
        query_params["offset"] = offset

    return get_api_response("http://jservice.io/api/clues", query_params)


def api_get_category_by_id(category_id):
    if not isinstance(category_id, int):
        raise NoIDProvidedError("Invalid id was provided to retrieve a category.")
    query_params = {"id": category_id}
    return get_api_response("http://jservice.io/api/category", query_params)


def api_mark_clue_invalid(clue_id):
    if not isinstance(clue_id, int):
        raise NoIDProvidedError("Invalid id was provided to mark a clue invalid.")
    query_params = {"id": clue_id}
    return get_api_response("http://jservice.io/api/category", query_params)


def ui_get_random_clues():
    """
    Displays a list of random clues depending on what was put into get_clues_entry.
    """
    try:
        clues_to_get = clues_entry.get()
        clues_to_get = int(clues_to_get)
        random_clues = api_get_random_clues(clues_to_get)
        if random_clues is not None:
            ui_show_clues(random_clues)
    except ValueError as exception:
        messagebox.showerror("Oops!", "Invalid entry for number of clues to retrieve!")
        clues_entry.delete(0, len(clues_entry.get()))


def ui_get_random_question():
    random_question_response = api_get_random_clues(1)
    if random_question_response is not None:
        random_question = next(iter(random_question_response), None)
        print(random_question)

        answer = messagebox.askyesno("Question #" + str(random_question.get("id")),
                                        "Value: " + str(random_question.get("value"))
                                        + "\nQ: " + random_question.get("question")
                                        + "\n\n" + "Show Answer?")
        if answer:
            messagebox.showinfo("Answer #" + str(random_question.get("id")), random_question.get("answer"))


def ui_search_clue():
    win = Toplevel()
    win.title('Clue Search')
    Label(win, text="Value").pack()
    value_entry = Entry(win, width=200)
    value_entry.pack()
    Label(win, text="Category ID").pack()
    category_id_entry = Entry(win, width=200)
    category_id_entry.pack()
    Label(win, text="Minimum date (YYYY-MM-DD)").pack()
    min_date_entry = Entry(win, width=200)
    min_date_entry.pack()
    Label(win, text="Maximum date (YYYY-MM-DD)").pack()
    max_date_entry = Entry(win,width=200)
    max_date_entry.pack()

    Button(win, text='Search', command=lambda: search_api(value_entry.get(),
                                                          category_id_entry.get(),
                                                          min_date_entry.get(),
                                                          max_date_entry.get(),
                                                          win)).pack()


def search_api(value, category_id, min_date, max_date, window):
    print(value)
    clue_search_results = api_get_clues(value, category_id, min_date, max_date)
    if clue_search_results is not None:
        ui_show_clues(clue_search_results)
    window.destroy()


def ui_show_clues(clues):
    win = Toplevel()
    win.title("Clue Search Results")
    width = 125
    clue_list = Listbox(win, width=width, height=30)
    for clue in clues:
        clue_list.insert(END, "Value: " + str(clue.get("value")),
                         "Question: " + clue.get("question"),
                         "Answer: " + clue.get("answer"),
                         "Air Date: " + clue.get("airdate"),
                         "Category ID: " + str(clue.get("category_id")),
                         "Invalid Votes: " + str(clue.get("invalid_count")),
                         "Clue ID: " + str(clue.get("id")),
                         "-" * width)

    scrollbar = Scrollbar(win, orient='vertical', command=clue_list.yview)
    scrollbar.grid(row=0,column=1, sticky=tk.NS)

    clue_list['yscrollcommand'] = scrollbar.set
    clue_list.grid(row=0, column=0)
    Button(win, text='Close', command=win.destroy)


def get_api_response(url, query_params):
    response = None
    try:
        response = requests.get(url, params=query_params).json()
    except requests.exceptions.RequestException as e:  # This is the correct syntax
        messagebox.showerror("Error", "The response from the API wasn't correct, is it available?")
    except requests.exceptions.JSONDecodeError as json_error:
        messagebox.showerror("Error", "The response from the API wasn't correct, is it available?")

    return response


window = tk.Tk()
window.title("JSService API Calls")
window.minsize(800, 560)
clue_label = tk.Label(text="Enter the number of random clues you wish to retrieve.")
clue_label.grid(row=0, column=0, padx=20, pady=0)
clues_entry = tk.Entry(width=25)
clues_entry.insert(0, "1")
clues_entry.grid(row=1, column=0, padx=20, pady=0)

random_clues_button = tk.Button(
    text="Get random clues",
    width=25,
    height=5,
    command=ui_get_random_clues
)
random_clues_button.grid(row=2, column=0, padx=20, pady=0)
random_question_button = tk.Button(
    text="Get random question",
    width=25,
    height=5,
    command=ui_get_random_question
)
random_question_button.grid(row=0, column=2, padx=20, pady=5)

search_clues_button = tk.Button(
    text="Search clues",
    width=25,
    height=5,
    command=ui_search_clue
)
search_clues_button.grid(row=0, column=4, padx=20, pady=5)


if __name__ == '__main__':
    window.mainloop()

