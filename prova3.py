import traceback

try:
    #print(x)
    result = "ciao" + 5
except NameError as e:
    traceback.print_exc()
    print(f"NameError: {e}")
except TypeError as e:
    traceback.print_exc()
    print(f"Errore TypeError: {e}")
except:
    print("Something else went wrong") 